import hmac
import hashlib
import httpx
from typing import Optional
from fastapi import Request, HTTPException

from .interface import WhatsAppProvider, InboundMessage
import os
import whatsapp.config as cfg

def _graph_base():
    ver = os.getenv("META_API_VERSION") or cfg.META_API_VERSION
    return f"https://graph.facebook.com/{ver}"

class MetaProvider(WhatsAppProvider):
    name = "meta"

    async def verify_webhook(self, request: Request) -> Optional[str]:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        verify = os.getenv("META_VERIFY_TOKEN") or cfg.META_VERIFY_TOKEN
        if mode == "subscribe" and token == verify:
            return challenge
        raise HTTPException(status_code=403, detail="Verification failed")

    def _verify_signature(self, raw_body: bytes, signature: str):
        if not META_APP_SECRET or not signature:
            return
        expected = "sha256=" + hmac.new(META_APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

    def parse_inbound(self, payload: dict, request=None) -> list[InboundMessage]:
        msgs: list[InboundMessage] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                for m in value.get("messages", []):
                    from_phone = m.get("from", "")
                    text = None
                    btn_id = None
                    btn_title = None
                    list_id = None
                    list_title = None
                    product_id = None
                    catalog_id = None

                    mtype = m.get("type")
                    if mtype == "text":
                        text = m.get("text", {}).get("body")
                    elif mtype == "button":
                        text = m.get("button", {}).get("text")
                        btn_id = m.get("button", {}).get("payload")
                    elif mtype == "interactive":
                        inter = m.get("interactive", {})
                        itype = inter.get("type")
                        if itype == "button_reply":
                            br = inter.get("button_reply", {})
                            btn_id = br.get("id")
                            btn_title = br.get("title")
                            text = btn_title
                        elif itype == "list_reply":
                            lr = inter.get("list_reply", {})
                            list_id = lr.get("id")
                            list_title = lr.get("title")
                            text = lr.get("title")
                        elif itype == "product":
                            pr = inter.get("product", {})
                            product_id = pr.get("product_retailer_id")
                            catalog_id = pr.get("catalog_id")
                        elif itype == "product_list":
                            # contains multiple? map first
                            pl = inter.get("product_list", {})
                            # keep raw
                            pass
                    elif mtype == "order":
                        order = m.get("order", {})
                        catalog_id = order.get("catalog_id")
                        product_id = order.get("product_items", [{}])[0].get("product_retailer_id") if order.get("product_items") else None
                        text = f"order:{order.get('id')}"

                    msgs.append(InboundMessage(
                        provider="meta",
                        from_phone=from_phone,
                        text=text,
                        button_reply_id=btn_id,
                        button_reply_title=btn_title,
                        list_reply_id=list_id,
                        list_reply_title=list_title,
                        product_retailer_id=product_id,
                        catalog_id=catalog_id,
                        raw=m
                    ))
        return msgs

    async def _post(self, payload: dict) -> dict:
        token = os.getenv("META_TOKEN") or cfg.META_TOKEN
        phone_id = os.getenv("META_PHONE_ID") or cfg.META_PHONE_ID
        graph_base = _graph_base()
        if not token or not phone_id:
            # mock mode – log and return fake
            print(f"[META MOCK] would POST to {graph_base}/{phone_id}/messages: {payload}")
            return {"mock": True, "payload": payload}
        url = f"{graph_base}/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()

    async def send_text(self, to_phone: str, text: str, buttons: Optional[list[dict]] = None) -> dict:
        if buttons:
            # interactive button (max 3)
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text[:1024]},
                    "action": {"buttons": [{"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}} for b in buttons[:3]]}
                }
            }
        else:
            payload = {"messaging_product": "whatsapp", "to": to_phone, "type": "text", "text": {"preview_url": False, "body": text}}
        return await self._post(payload)

    async def send_interactive_list(self, to_phone: str, header: str, body: str, button_text: str, sections: list[dict]) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": header[:60]},
                "body": {"text": body[:1024]},
                "footer": {"text": "dKart Medical"},
                "action": {"button": button_text[:20], "sections": sections}
            }
        }
        return await self._post(payload)

    async def send_catalog(self, to_phone: str, body_text: str, catalog_id: str, product_retailer_ids: list[str]) -> dict:
        # Single product message
        prid = product_retailer_ids[0] if product_retailer_ids else ""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "product",
                "body": {"text": body_text[:1024]},
                "footer": {"text": "dKart Medical"},
                "action": {"catalog_id": catalog_id, "product_retailer_id": prid}
            }
        }
        return await self._post(payload)

    async def send_product_list(self, to_phone: str, header: str, body: str, catalog_id: str, sections: list[dict]) -> dict:
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {"type": "text", "text": header[:60]},
                "body": {"text": body[:1024]},
                "footer": {"text": "dKart Medical"},
                "action": {"catalog_id": catalog_id, "sections": sections}
            }
        }
        return await self._post(payload)
