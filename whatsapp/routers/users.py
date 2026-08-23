from fastapi import APIRouter, HTTPException
from ..models.db import get_user, get_orders

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{phone}")
async def get_user_profile(phone: str):
    phone = phone.lstrip("+")
    user = get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    orders = get_orders(phone)
    current = get_orders(phone, current_only=True)
    return {
        "user": user.__dict__,
        "previousOrders": [o.__dict__ for o in orders if o.status in ("delivered","cancelled")],
        "currentOrders": [o.__dict__ for o in current],
        "totalOrders": len(orders)
    }
