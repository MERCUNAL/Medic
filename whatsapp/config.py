import os
from pathlib import Path
from dotenv import load_dotenv

# Load whatsapp/.env explicitly (works when launched from repo root via `uvicorn whatsapp.app:app`)
# Also load root .env for GOOGLE_API_KEY fallback. whatsapp/.env takes precedence.
ROOT_ENV = Path(__file__).resolve().parent.parent / ".env"
WA_ENV = Path(__file__).resolve().parent / ".env"
# Load in order: root first, then WA overrides
load_dotenv(dotenv_path=ROOT_ENV, override=False)
load_dotenv(dotenv_path=WA_ENV, override=True)

WHATSAPP_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "twilio").lower()  # twilio|meta
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGO = "HS256"

# Meta Cloud API
META_TOKEN = os.getenv("META_TOKEN", "")
META_PHONE_ID = os.getenv("META_PHONE_ID", "")
META_APP_SECRET = os.getenv("META_APP_SECRET", "")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "verify_medic")
META_CATALOG_ID = os.getenv("META_CATALOG_ID", "")
META_API_VERSION = os.getenv("META_API_VERSION", "v21.0")

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # sandbox default

# Frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "919999999999")  # wa.me number without +

CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
