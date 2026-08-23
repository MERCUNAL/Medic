from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from ..config import JWT_SECRET, JWT_ALGO, WHATSAPP_NUMBER
from ..services import session

router = APIRouter(prefix="/auth", tags=["auth"])

class LinkRequest(BaseModel):
    token: str | None = None  # JWT from website login
    phone: str | None = None
    role: str | None = None
    location: str | None = None

@router.post("/link")
async def create_link(req: LinkRequest):
    phone = req.phone
    role = req.role or ""
    location = req.location or ""
    if req.token:
        try:
            data = jwt.decode(req.token, JWT_SECRET, algorithms=[JWT_ALGO])
            phone = data.get("phone") or data.get("sub") or phone
            role = data.get("role", role)
            location = data.get("location", location)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    if not phone:
        raise HTTPException(status_code=400, detail="phone required (or valid JWT)")
    phone = phone.lstrip("+").replace(" ", "").replace("-", "")
    link_id = session.create_link(phone, role, location)
    wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text=REF_{link_id}%20Hi"
    return {"linkId": link_id, "wa_link": wa_link, "phone": phone}

@router.get("/link/{link_id}")
async def get_link(link_id: str):
    data = session.consume_link(link_id)
    if not data:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    return data
