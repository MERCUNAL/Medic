from fastapi import APIRouter, Request, HTTPException
import re
import os
from ..providers import get_provider
import whatsapp.config as cfg
from ..models.db import get_user, get_orders
from ..services import catalog_service, session
from ..services.rag_client import query_rag, thread_for_phone

router = APIRouter(tags=["webhook"])

REF_RE = re.compile(r"REF_([a-f0-9]{8})", re.I)

def _provider():
    return get_provider()

def _is_meta():
    return (os.getenv("WHATSAPP_PROVIDER") or cfg.WHATSAPP_PROVIDER).lower() == "meta"

def _meta_catalog_id():
    return os.getenv("META_CATALOG_ID") or cfg.META_CATALOG_ID

def _extract_ref(text: str):
    if not text: return None
    m = REF_RE.search(text)
    return m.group(1) if m else None

@router.get("/webhook")
@router.get("/api/whatsapp/webhook")
async def verify(request: Request):
    # Support both /webhook and /api/whatsapp/webhook (legacy misconfigured Twilio URL)
    # Meta verification; Twilio ignores
    if _is_meta():
        challenge = await _provider().verify_webhook(request)
        if challenge:
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(challenge)
    return {"status": "ok"}

@router.post("/webhook")
@router.post("/api/whatsapp/webhook")
async def inbound(request: Request):
    content_type = request.headers.get("content-type","")
    payload = {}
    raw_body = await request.body()
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except:
            payload = {}
        # verify Meta signature if needed
        if _is_meta():
            sig = request.headers.get("X-Hub-Signature-256","")
            app_secret = os.getenv("META_APP_SECRET") or cfg.META_APP_SECRET
            if app_secret and sig:
                import hmac, hashlib
                expected = "sha256=" + hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
                if not hmac.compare_digest(expected, sig):
                    raise HTTPException(status_code=403, detail="Invalid signature")
    else:
        # Twilio form
        form = await request.form()
        payload = dict(form)

    provider = _provider()
    print(f"[WEBHOOK] provider={provider.name} content-type={content_type} payload_keys={list(payload.keys())[:5]} raw_len={len(raw_body)}")
    msgs = provider.parse_inbound(payload, request)
    print(f"[WEBHOOK] parsed {len(msgs)} msgs: {[m.text for m in msgs]}")
    if not msgs:
        return {"status": "no messages"}

    for msg in msgs:
        phone = msg.from_phone.lstrip("+")
        text = (msg.text or "").strip()
        btn_id = msg.button_reply_id or msg.list_reply_id or ""
        # Handle REF linking
        ref = _extract_ref(text)
        if ref:
            linked = session.consume_link(ref)
            if linked:
                session.set_state(phone, "linked", {"linked_phone": linked["phone"], "role": linked.get("role",""), "location": linked.get("location","")})
                await provider.send_text(phone, f"Hi {linked.get('role','')}! Your WhatsApp is now linked to dKart (phone {linked['phone']}).\n\nYou can:\n• Browse Catalog\n• Track Orders\n• Ask Medic Assistant")
                # strip REF from text for next handling
                text = re.sub(r"REF_[a-f0-9]{8}", "", text, flags=re.I).strip()
                if not text:
                    text = "Hi"
            # if no ref found keep going

        state = session.get_state(phone)
        user = get_user(phone)
        # merge linked role/location if available
        role = state.get("role") or (user.role if user else "general user")
        location = state.get("location") or (user.location if user else "unknown")

        # Determine intent - normalized (strip to avoid "hi " != "hi" bug)
        text_lower = text.strip().lower()
        combined_lower = (text + " " + btn_id).lower().strip()
        lower = combined_lower  # keep alias for legacy checks

        # --- Direct replies without RAG (no HTTP to backend) ---
        # These are answered locally from code/mock_data/catalog, saving RAG cost/latency
        DIRECT_REPLIES = {
            "help": "🆘 *dKart Help*\n• `catalog` or `catalog BP` → browse products\n• `track` → active orders\n• `ORD-1001` → tracking link\n• any medical question → Medic AI\n• `menu` → this help",
            "menu": "📋 *Menu*\n1. Browse Catalog (`catalog`)\n2. Track Order (`track`)\n3. Ask Medic (`what is BP-Advance price?`)",
        }
        if text_lower in DIRECT_REPLIES:
            await provider.send_text(phone, DIRECT_REPLIES[text_lower])
            continue
        if text_lower in ("hi", "hello", "hey", "start"):
            # Greeting without RAG – shows help + catalog entry
            await provider.send_text(phone, f"👋 Hi {user.name if user else ''}! Welcome to dKart Medical.\n{DIRECT_REPLIES['help']}", buttons=[{"id":"catalog","title":"Browse Catalog"},{"id":"track","title":"Track Order"}])
            continue

        # Product selection from list/catalog
        if msg.product_retailer_id or (btn_id and btn_id.startswith("csv_")) or (combined_lower.startswith("csv_")):
            prid = msg.product_retailer_id or btn_id or text.strip()
            item = catalog_service.get_item(prid)
            if item:
                detail = f"*{item['title']}*\n{item['name']}\nPrice: INR {item['price']}\nModel: {item['model']}\nBrand: {item['brand']}\nSpecs: {item['specs'][:400]}\n\nReply *order* to enquire or *catalog* to see more."
                await provider.send_text(phone, detail, buttons=[{"id":"catalog","title":"Browse Catalog"},{"id":"track","title":"Track Order"},{"id":"ask","title":"Ask Assistant"}])
                continue

        if "catalog" in combined_lower or "product" in combined_lower or "browse" in combined_lower:
            # Show catalog – use product_list if meta + catalog_id else list
            q = "" 
            # if user typed "catalog bp" extract query
            if combined_lower.startswith("catalog"):
                q = text[len("catalog"):].strip()
            res = catalog_service.list_catalog(q=q, page=1, limit=10)
            items = res["items"]
            if not items:
                await provider.send_text(phone, "No products found. Try: *catalog BP* or ask me anything.")
                continue
            catalog_id = _meta_catalog_id()
            if _is_meta() and catalog_id:
                sections = catalog_service.to_product_list_sections(items, catalog_id)
                await provider.send_product_list(phone, "dKart Catalog", f"Found {res['total']} items. Tap to view:", catalog_id, sections)
            else:
                sections = catalog_service.to_interactive_list_sections(items)
                await provider.send_interactive_list(phone, "dKart Catalog", f"Found {res['total']} items. Select one:", "View Products", sections)
            continue

        if "track" in combined_lower or "order" in combined_lower or "where" in combined_lower or "status" in combined_lower:
            orders = get_orders(phone, current_only=True)
            if not orders:
                # No current -> show previous + fallback to RAG
                await provider.send_text(phone, "You have no active orders at the moment.\n\nYou can still:\n• Browse catalog (reply *catalog*)\n• Ask our Medic Assistant anything (just type your question)", buttons=[{"id":"catalog","title":"Browse Catalog"},{"id":"ask","title":"Ask Assistant"}])
                # Also push to RAG if they asked a question beyond tracking intent
                if len(text.split()) > 2 and "track" not in combined_lower:
                    try:
                        rag = await query_rag(text, thread_for_phone(phone), role, location)
                        await provider.send_text(phone, rag.get("answer","Sorry! I do not have that information."))
                        if rag.get("options"):
                            await provider.send_text(phone, "Try:", buttons=[{"id": o, "title": o[:20]} for o in rag["options"][:3]])
                    except Exception as e:
                        print("RAG error", e)
                continue
            # Has current orders – show selector
            lines = []
            for o in orders:
                lines.append(f"*{o.id}* - {o.status.upper()} | ETA {o.eta or 'TBD'}\nItems: {', '.join([it['name'] for it in o.items])[:60]}")
            body = "\n\n".join(lines) + "\n\nReply with order ID (e.g. ORD-1001) to get tracking link."
            await provider.send_text(phone, f"📦 Your active orders:\n\n{body}", buttons=[{"id":"catalog","title":"Browse Catalog"},{"id":"ask","title":"Ask Assistant"}])
            continue

        # Direct order ID lookup
        if re.match(r"ORD-\d+", text.upper()):
            from ..models.db import get_order_by_id
            o = get_order_by_id(text.upper().strip())
            if o:
                if o.phone != phone:
                    await provider.send_text(phone, "That order does not belong to this WhatsApp number.")
                else:
                    if o.status in ("delivered","cancelled"):
                        await provider.send_text(phone, f"Order *{o.id}* is *{o.status}*. Total INR {o.total}.")
                    else:
                        await provider.send_text(phone, f"Order *{o.id}* is *{o.status}*.\nCourier: {o.courier}\nAWB: {o.trackingCode}\nTrack: {o.courierUrl}\nETA: {o.eta}")
                continue

        # Fallback -> RAG (preserve Medic behaviour)
        try:
            rag = await query_rag(text or btn_id or "Hi", thread_for_phone(phone), role, location)
            answer = rag.get("answer","Sorry! I do not have that information.")
            options = rag.get("options", [])
            await provider.send_text(phone, answer)
            if options:
                await provider.send_text(phone, "You might also ask:", buttons=[{"id": o, "title": o[:20]} for o in options[:3]])
            session.append_history(phone, "user", text)
            session.append_history(phone, "assistant", answer)
        except Exception as e:
            print("RAG proxy error", e)
            await provider.send_text(phone, "Sorry, the assistant is temporarily unavailable. Try *catalog* or *track*.")

    return {"status": "processed", "count": len(msgs)}

@router.get("/debug/state")
async def debug_state():
    return session.dump()
