from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class InboundMessage(BaseModel):
    provider: str
    from_phone: str  # E.164 without whatsapp: prefix
    to_phone: Optional[str] = None
    text: Optional[str] = None
    button_reply_id: Optional[str] = None
    button_reply_title: Optional[str] = None
    list_reply_id: Optional[str] = None
    list_reply_title: Optional[str] = None
    product_retailer_id: Optional[str] = None
    catalog_id: Optional[str] = None
    order_id: Optional[str] = None  # for catalog orders
    raw: dict = {}

class WhatsAppProvider(ABC):
    name: str

    @abstractmethod
    async def verify_webhook(self, request) -> Optional[str]:
        pass

    @abstractmethod
    def parse_inbound(self, payload: dict, request=None) -> list[InboundMessage]:
        pass

    @abstractmethod
    async def send_text(self, to_phone: str, text: str, buttons: Optional[list[dict]] = None) -> dict:
        pass

    @abstractmethod
    async def send_interactive_list(self, to_phone: str, header: str, body: str, button_text: str, sections: list[dict]) -> dict:
        pass

    @abstractmethod
    async def send_catalog(self, to_phone: str, body_text: str, catalog_id: str, product_retailer_ids: list[str]) -> dict:
        pass

    @abstractmethod
    async def send_product_list(self, to_phone: str, header: str, body: str, catalog_id: str, sections: list[dict]) -> dict:
        pass
