import base64
from typing import Optional
from fastapi import Request, HTTPException
import httpx

from .interface import WhatsAppProvider, InboundMessage
import os
# Import config dynamically to pick up .env changes without stale import
import whatsapp.config as cfg

class TwilioProvider(WhatsAppProvider):
    name = "twilio"

    async def verify_webhook(self, request: Request) -> Optional[str]:
        # Twilio uses no GET verify; return None. Optionally validate X-Twilio-Signature
        return None

    def parse_inbound(self, payload: dict, request=None) -> list[InboundMessage]:
        # Twilio posts x-www-form-urlencoded; we accept both dict and form
        # payload may already be parsed form dict
        from_phone = payload.get("From", "") or payload.get("from", "")
        # strip whatsapp: prefix
        if from_phone.startswith("whatsapp:"):
            from_phone = from_phone[len("whatsapp:"):]
        # remove leading +
        from_phone = from_phone.lstrip("+")
        body = payload.get("Body") or payload.get("body") or payload.get("text")
        button_id = payload.get("ButtonPayload") or payload.get("ListId")
        # Twilio doesn't give structured button – we infer via body
        return [InboundMessage(provider="twilio", from_phone=from_phone, text=body, button_reply_id=button_id, raw=payload)]

    async def send_text(self, to_phone: str, text: str, buttons: Optional[list[dict]] = None) -> dict:
        sid = os.getenv("TWILIO_ACCOUNT_SID") or cfg.TWILIO_ACCOUNT_SID
        token = os.getenv("TWILIO_AUTH_TOKEN") or cfg.TWILIO_AUTH_TOKEN
        wa_from = os.getenv("TWILIO_WHATSAPP_FROM") or cfg.TWILIO_WHATSAPP_FROM
        if not sid or not token:
            print(f"[TWILIO MOCK] to={to_phone} text={text[:120]} buttons={buttons} (SID/TOKEN missing -> not sending to Twilio)")
            return {"mock": True, "to": to_phone, "body": text}
        if sid.startswith("AC22cd02"):
            print(f"[TWILIO WARNING] Placeholder SID still in .env – using mock. Replace with real SID from console.twilio.com")
            print(f"[TWILIO MOCK] to={to_phone} text={text[:120]}")
            return {"mock": True, "to": to_phone, "body": text, "warning": "placeholder SID"}
        # Twilio can't send interactive buttons via simple Messages API – send as text + numbered options
        if buttons:
            text = text + "\n\n" + "\n".join([f"{i+1}. {b['title']} (reply {b['id']})" for i, b in enumerate(buttons)])
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = {"From": wa_from, "To": f"whatsapp:+{to_phone}", "Body": text}
        auth = (sid, token)
        print(f"[TWILIO SEND] From={wa_from} To=whatsapp:+{to_phone} len={len(text)}")
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.post(url, data=data, auth=auth)
                print(f"[TWILIO RESP] status={r.status_code} body={r.text[:500]}")
                r.raise_for_status()
                return r.json()
        except httpx.HTTPStatusError as e:
            print(f"[TWILIO ERROR] status={e.response.status_code} body={e.response.text[:1000]}")
            raise
        except Exception as e:
            print(f"[TWILIO EXCEPTION] {e}")
            raise

    async def send_interactive_list(self, to_phone: str, header: str, body: str, button_text: str, sections: list[dict]) -> dict:
        # Twilio fallback: flatten list into numbered text
        lines = [f"*{header}*", body, ""]
        idx = 1
        for sec in sections:
            lines.append(f"*{sec.get('title','')}*")
            for row in sec.get("rows", []):
                lines.append(f"{idx}. {row.get('title')} - {row.get('description','')[:40]} (id:{row.get('id')})")
                idx += 1
        text = "\n".join(lines)
        return await self.send_text(to_phone, text)

    async def send_catalog(self, to_phone: str, body_text: str, catalog_id: str, product_retailer_ids: list[str]) -> dict:
        # No native catalog – send link to catalog preview
        link = f"{body_text}\n\nView catalog: https://wa.me/{product_retailer_ids[0] if product_retailer_ids else ''}"
        return await self.send_text(to_phone, body_text)

    async def send_product_list(self, to_phone: str, header: str, body: str, catalog_id: str, sections: list[dict]) -> dict:
        return await self.send_interactive_list(to_phone, header, body, "View Products", sections)
