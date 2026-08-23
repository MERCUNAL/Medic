# dKart WhatsApp Microservice (Abstracted Meta/Twilio)

Separate microservice at **:8001** (RAG stays at :8000). Frontend `WhatsAppButton` (`medic-frontend/components/WhatsAppButton.tsx`) replaces `ChatWidget` at `bottom-6 right-6`.

## Provider abstraction
- `providers/interface.py` – abstract `WhatsAppProvider`
- `providers/meta.py` – Meta Cloud API (production, native Catalog, product_list)
- `providers/twilio.py` – Twilio sandbox (testing, flattened list fallback)
- Switch via `WHATSAPP_PROVIDER=twilio|meta` in `.env` – no code change. See `.env.example`.

Mock data in `mock_data/users.json` + `orders.json` – swap to DB later via `models/db.py` interface.

## Catalog
Native WhatsApp Commerce Catalog: sync `documents/Medical_list_with_specs.csv` (900 items, id `csv_{index}`) to `META_CATALOG_ID` via Graph API. Twilio path sends interactive list fallback (10 rows).

## Quick start
```bash
pip install -r whatsapp/requirements.txt
uvicorn whatsapp.app:app --reload --port 8001
# in another terminal
# ngrok http 8001  -> set webhook https://<ngrok>/webhook in Meta/Twilio dashboard
```
Set Meta `META_VERIFY_TOKEN`, `META_TOKEN`, `META_PHONE_ID` or Twilio `TWILIO_ACCOUNT_SID` etc. For local mock both tokens empty = console mock (logs payload).

## Fix for `POST /api/whatsapp/webhook 404` (common misconfiguration)
If Twilio shows `POST /api/whatsapp/webhook 404`, you pointed ngrok to Next.js (:3000) or used wrong path.
* **Correct Twilio webhook:** `https://<ngrok>.ngrok-free.app/webhook` (POST) — *not* `/api/whatsapp/webhook`.
* **This service now accepts both** `POST /webhook` and `POST /api/whatsapp/webhook` (`routers/webhook.py:19` alias) for robustness.
* **Next.js also rewrites** `/api/whatsapp/:path*` → `WHATSAPP_SERVICE_URL/:path*` (`medic-frontend/next.config.ts:5`) so `/api/whatsapp/webhook` via frontend works too.
* **Must run ngrok on :8001:** `ngrok http 8001`, verify `curl https://<ngrok>/health` returns `{"status":"ok"}`.

## Why "mock output but no WhatsApp"
`providers/twilio.py:30` `if not SID/TOKEN` or placeholder `AC22cd02...` → `[TWILIO MOCK]` log only. Create `whatsapp/.env` from `.env.example` with real `TWILIO_ACCOUNT_SID/TOKEN` from console.twilio.com, restart. Check `GET /health` → `twilio_configured:true, is_placeholder_sid:false`.
Sandbox phone must be `join`ed: send `join <code>` to `+1 415 523 8886`.

## Website auth handoff
Login JWT/phone stored in `localStorage (auth_token/phone)` → `POST /auth/link` → returns `https://wa.me/<number>?text=REF_<8chars> Hi`. Webhook consumes `REF_` to link phone → personalization + `get_orders(phone, current_only)` for tracking.

## Webhook intents
- `catalog`/`hi` → product_list (meta) or list (twilio)
- `track`/`ORD-xxxx` → `models/db.get_orders` → active else previous → RAG fallback
- `csv_xxx` / product tap → detail card
- fallback → `services/rag_client.query_rag` → `backend :8000 /chat` (thread `wa:{phone}`) + 3 options as buttons
