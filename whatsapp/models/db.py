from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path

MOCK_DIR = Path(__file__).resolve().parent.parent / "mock_data"

@dataclass
class User:
    phone: str
    name: str
    role: str
    location: str
    email: Optional[str] = None
    previousOrders: list = field(default_factory=list)

@dataclass
class OrderItem:
    csv_id: str
    name: str
    qty: int
    price: int

@dataclass
class Order:
    id: str
    phone: str
    status: str
    items: list
    total: int
    trackingCode: Optional[str]
    courierUrl: Optional[str]
    courier: Optional[str]
    eta: Optional[str]
    createdAt: str
    updatedAt: str

def _load_json(name):
    path = MOCK_DIR / name
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))

def _norm(p: str) -> str:
    """Normalize to 10-digit last 10, so +919137098051 and 9137098051 match."""
    p = str(p).lstrip("+").replace(" ", "").replace("-", "")
    # keep last 10 digits for Indian numbers
    if len(p) > 10 and p.startswith("91"):
        return p[-10:]
    if len(p) > 10:
        return p[-10:]
    return p

def get_user(phone: str):
    want = _norm(phone)
    for u in _load_json("users.json"):
        if _norm(u["phone"]) == want:
            return User(**u)
    return None

def get_orders(phone: str, current_only: bool = False):
    want = _norm(phone)
    orders = _load_json("orders.json")
    filtered = [o for o in orders if _norm(o["phone"]) == want]
    if current_only:
        filtered = [o for o in filtered if o["status"] in ("placed", "shipped", "out_for_delivery")]
    return [Order(**o) for o in filtered]

def get_order_by_id(order_id: str):
    for o in _load_json("orders.json"):
        if o["id"] == order_id:
            return Order(**o)
    return None

def get_all_users():
    return [User(**u) for u in _load_json("users.json")]

def get_all_orders():
    return [Order(**o) for o in _load_json("orders.json")]
