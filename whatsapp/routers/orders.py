from fastapi import APIRouter, HTTPException, Query
from ..models.db import get_orders, get_order_by_id

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("")
async def list_orders(phone: str = Query(...), current_only: bool = False):
    phone = phone.lstrip("+")
    orders = get_orders(phone, current_only=current_only)
    return {"phone": phone, "orders": [o.__dict__ for o in orders]}

@router.get("/{order_id}")
async def get_order(order_id: str):
    o = get_order_by_id(order_id)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return o.__dict__

@router.post("/track")
async def track_order(payload: dict):
    order_id = payload.get("orderId") or payload.get("order_id")
    phone = payload.get("phone")
    if not order_id:
        raise HTTPException(status_code=400, detail="orderId required")
    o = get_order_by_id(order_id)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    if phone and o.phone != phone.lstrip("+"):
        raise HTTPException(status_code=403, detail="Order does not belong to phone")
    if o.status == "delivered":
        return {"order": o.__dict__, "message": f"Order {o.id} delivered on {o.updatedAt}"}
    if o.status == "cancelled":
        return {"order": o.__dict__, "message": f"Order {o.id} was cancelled."}
    return {
        "order": o.__dict__,
        "tracking": {"courier": o.courier, "code": o.trackingCode, "url": o.courierUrl, "eta": o.eta, "status": o.status}
    }
