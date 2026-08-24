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

## Quick start (also see root README.md for full 4-terminal flow)
```bash
pip install -r whatsapp/requirements.txt
pip install -r ../requirements.txt   # for pandas if needed
uvicorn whatsapp.app:app --reload --port 8001  # :8001 health http://localhost:8001/health
# In parallel:
uvicorn backend.fastapi_app:app --reload --port 8000  # RAG :8000
cd ../medic-frontend && npm install && npm run dev     # frontend :3000 WhatsAppButton
ngrok http 8001  # Forwarding https://<id>.ngrok-free.dev -> http://localhost:8001
# Set Twilio Sandbox https://<id>.ngrok-free.dev/webhook POST (or Meta verify)
```
Set `whatsapp/.env` from `.env.example`: `TWILIO_ACCOUNT_SID/TOKEN` (real `AC...` from console.twilio.com) or `META_TOKEN/PHONE_ID`. Empty → console `[TWILIO MOCK]` / `[META MOCK]` (no WA). Full commands in root `README.md`.

## Commands to run (copy-paste)
```bash
# Backend RAG
uvicorn backend.fastapi_app:app --reload --port 8000

# WhatsApp microservice
uvicorn whatsapp.app:app --reload --port 8001

# Frontend
cd medic-frontend && npm run dev

# ngrok tunnel
ngrok http 8001

# Health checks
curl http://localhost:8001/health
curl http://localhost:8000/docs
curl http://localhost:8001/catalog?limit=2&q=BP

# Mock webhook tests (no phone)
curl -X POST http://localhost:8001/webhook -H "Content-Type: application/x-www-form-urlencoded" -d "From=whatsapp:+919999999991&Body=Hi"
curl -X POST http://localhost:8001/webhook -d "From=whatsapp:+919999999991&Body=catalog"
curl http://localhost:8001/debug/state
```

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
