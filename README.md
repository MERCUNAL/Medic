# dKart Medical RAG + WhatsApp — dKart Medical Equipment

RAG chatbot (Chroma + Gemini + hybrid BM25) with separate WhatsApp microservice (Meta/Twilio abstracted) on bottom-right `WhatsApp` button (replaces `ChatWidget`). Catalog 900 items, mock orders, order tracking or RAG fallback.

## Architecture
- `backend/` FastAPI `:8000` RAG `POST /chat` (`rag/chatbot.py`)
- `whatsapp/` FastAPI `:8001` WhatsApp `POST /webhook` (`whatsapp/app.py`)
- `medic-frontend/` Next.js `:3000` `WhatsAppButton` (`components/WhatsAppButton.tsx`)
- `documents/Medical_list_with_specs.csv` → Chroma `chroma_db_new` + WhatsApp catalog
- `telegram/` existing Telegram bot (unchanged)

## Prerequisites
- Python 3.11 + `.venv` (recommended)
- Node 18+
- `ngrok` for Twilio/Meta webhook (https://ngrok.com/download)
- Twilio account (sandbox `+14155238886` for testing, `+18039621282` voice) or Meta Cloud API
- `GOOGLE_API_KEY` in root `.env` for Gemini

## Setup
```bash
# 1. Clone + envs
cp whatsapp/.env.example whatsapp/.env   # fill TWILIO_ACCOUNT_SID/TOKEN or META_TOKEN
# root .env already has GOOGLE_API_KEY, BOT_TOKEN

# 2. Python deps (from repo root)
pip install -r requirements.txt
pip install -r whatsapp/requirements.txt

# 3. Frontend env
# medic-frontend/.env.local should contain:
# NEXT_PUBLIC_WHATSAPP_SERVICE_URL=http://localhost:8001
# NEXT_PUBLIC_WHATSAPP_NUMBER=14155238886   # sandbox, use wa.me number
# NEXT_PUBLIC_RAG_URL=http://localhost:8000
```

## Run – All 4 terminals
```bash
# Terminal 1 – RAG backend :8000
uvicorn backend.fastapi_app:app --reload --port 8000
# health: http://localhost:8000/docs

# Terminal 2 – WhatsApp microservice :8001
uvicorn whatsapp.app:app --reload --port 8001
# health: http://localhost:8001/health  -> {"status":"ok","provider":"twilio", ...}
# docs:   http://localhost:8001/docs

# Terminal 3 – Frontend :3000
cd medic-frontend
npm install
npm run dev
# open http://localhost:3000 → bottom-right WhatsApp button

# Terminal 4 – ngrok (for Twilio/Meta)
ngrok http 8001
# Forwarding https://<id>.ngrok-free.dev -> http://localhost:8001
# Copy https://<id>.ngrok-free.dev/webhook

# Optional – Telegram bot
python telegram/telegram_bot.py
```

## Twilio Sandbox (testing)
```bash
# 1. Console https://console.twilio.com/ -> Messaging -> Try it out -> Send a WhatsApp message
#    Note sandbox number +14155238886 and join code e.g. `join word-word`
# 2. On your phone: send `join word-word` to +1 415 523 8886 (re-join every 72h)
# 3. Sandbox Configuration -> When a message comes in = https://<ngrok>.ngrok-free.app/webhook  (POST)
#    Save. Must be /webhook not /api/whatsapp/webhook (both now accepted but prefer /webhook)
# 4. Verify: curl https://<ngrok>.ngrok-free.app/health
# 5. Test in WhatsApp: Hi | catalog | catalog BP | track | ORD-1001 | csv_7 | What is BP-Basic price?
```

## Meta Cloud API (production – native Catalog)
```bash
# whatsapp/.env:
WHATSAPP_PROVIDER=meta
META_TOKEN=EAA...
META_PHONE_ID=123...
META_CATALOG_ID=456...
META_VERIFY_TOKEN=verify_medic
# Then: ngrok http 8001 -> Meta Dashboard -> WhatsApp -> Configuration -> Webhook https://<ngrok>/webhook -> Verify
```

## WhatsApp intents (what works without RAG)
- `Hi`/`hello`/`help`/`menu` → local greeting/help, no RAG
- `catalog` / `catalog BP` → `services/catalog_service.py` lists 900 items, 10/page, Twilio numbered list or Meta `product_list`
- `csv_7` / product tap → detail `*BP-Advance… Price INR 1100…`
- `track` / `order` → `models/db.py` mock `orders.json` → active `ORD-1001 shipped` or `no active…`
- `ORD-1001` → tracking `Courier: Delhivery AWB… Track: https://…`
- Anything else → `services/rag_client.py` → `POST http://localhost:8000/chat` → Gemini hybrid retrieval → answer + 3 options as WhatsApp buttons

## Order history (mock)
Currently from `whatsapp/mock_data/orders.json` (4 orders) + `users.json` (3 users 919999999991/992/993) via `models/db.py:get_orders(phone, current_only)`. Swap to DB by replacing `models/db.py` interface. Endpoints:
```bash
curl http://localhost:8001/users/919999999991
curl "http://localhost:8001/orders?phone=919999999991&current_only=true"
curl -X POST http://localhost:8001/orders/track -H "Content-Type: application/json" -d '{"orderId":"ORD-1001","phone":"919999999991"}'
curl "http://localhost:8001/catalog?limit=2&q=BP"
curl "http://localhost:8001/catalog/categories"
```

## Auth handoff (login → WhatsApp)
```bash
# Website stores phone/JWT in localStorage (auth_token/phone/user)
# WhatsAppButton -> POST /auth/link {phone, token, role, location}
curl -X POST http://localhost:8001/auth/link -H "Content-Type: application/json" -d '{"phone":"919999999991","role":"Doctor"}'
# -> {"wa_link":"https://wa.me/14155238886?text=REF_ab12cd34 Hi"}
# Send REF_... Hi in WhatsApp → webhook links phone→role/location for RAG personalization
```

## Testing without phone (mock)
```bash
# All via curl, logs [TWILIO MOCK] if SID/TOKEN missing
curl -X POST http://localhost:8001/webhook -H "Content-Type: application/x-www-form-urlencoded" -d "From=whatsapp:+919999999991&Body=Hi"
curl -X POST http://localhost:8001/webhook -d "From=whatsapp:+919999999991&Body=catalog" --header "Content-Type: application/x-www-form-urlencoded"
curl http://localhost:8001/debug/state  # see session links/history
```

## Troubleshooting
- `POST /api/whatsapp/webhook 404` → ngrok pointed to :3000 not :8001; use `https://<ngrok>/webhook` POST (alias `/api/whatsapp/webhook` also works)
- `[TWILIO MOCK]` → `whatsapp/.env` missing/placeholder → fill `TWILIO_ACCOUNT_SID/TOKEN` from console.twilio.com, restart :8001; `GET /health` must show `twilio_configured:true`
- `63007 Twilio could not find a Channel` → `TWILIO_WHATSAPP_FROM` not WhatsApp-enabled; use sandbox `whatsapp:+14155238886`
- `ngrok ERR_NGROK_6024` → visit `https://<ngrok>/health` in browser, click Visit Site
- RAG timeout → ensure backend :8000 running, `GOOGLE_API_KEY` valid, `chroma_db_new` exists
