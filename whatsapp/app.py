import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import whatsapp.config as cfg
from .routers import webhook, auth, catalog, users, orders

app = FastAPI(title="dKart WhatsApp Microservice", version="1.0.0", description="Abstracted Meta/Twilio provider + catalog + orders + RAG proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(users.router)
app.include_router(orders.router)

@app.get("/")
async def root():
    prov = (os.getenv("WHATSAPP_PROVIDER") or cfg.WHATSAPP_PROVIDER)
    return {"service": "whatsapp", "provider": prov}

@app.get("/health")
async def health():
    prov = (os.getenv("WHATSAPP_PROVIDER") or cfg.WHATSAPP_PROVIDER)
    return {
        "status": "ok",
        "provider": prov,
        "rag": cfg.RAG_SERVICE_URL,
        "catalog_id": bool(os.getenv("META_CATALOG_ID") or cfg.META_CATALOG_ID),
        "wa_number": os.getenv("WHATSAPP_NUMBER") or cfg.WHATSAPP_NUMBER,
        "twilio_configured": bool((os.getenv("TWILIO_ACCOUNT_SID") or cfg.TWILIO_ACCOUNT_SID) and (os.getenv("TWILIO_AUTH_TOKEN") or cfg.TWILIO_AUTH_TOKEN)),
        "twilio_from": os.getenv("TWILIO_WHATSAPP_FROM") or cfg.TWILIO_WHATSAPP_FROM,
    }
