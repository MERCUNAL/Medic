import os
from .interface import WhatsAppProvider
from .meta import MetaProvider
from .twilio import TwilioProvider
import whatsapp.config as cfg

def get_provider() -> WhatsAppProvider:
    prov = (os.getenv("WHATSAPP_PROVIDER") or cfg.WHATSAPP_PROVIDER).lower()
    if prov == "meta":
        return MetaProvider()
    return TwilioProvider()

# Backward compat; but callers should use get_provider() for fresh env
provider = get_provider()
