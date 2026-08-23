from typing import Dict, Optional
import time
import uuid

# In-memory stores – swap to Redis later without touching callers
_link_store: Dict[str, dict] = {}  # linkId -> {phone, role, location, exp}
_state_store: Dict[str, dict] = {}  # phone -> {state, last_message, history}

LINK_TTL = 600  # 10 min

def create_link(phone: str, role: str = "", location: str = "") -> str:
    link_id = uuid.uuid4().hex[:8]
    _link_store[link_id] = {"phone": phone, "role": role, "location": location, "exp": time.time()+LINK_TTL}
    return link_id

def consume_link(link_id: str) -> Optional[dict]:
    data = _link_store.get(link_id)
    if not data:
        return None
    if data["exp"] < time.time():
        _link_store.pop(link_id, None)
        return None
    # keep for 24h window? pop after first consume for security
    _link_store.pop(link_id, None)
    return data

def set_state(phone: str, state: str, extra: dict = None):
    s = _state_store.get(phone, {})
    s.update({"state": state, "updatedAt": time.time()})
    if extra:
        s.update(extra)
    _state_store[phone] = s

def get_state(phone: str) -> dict:
    return _state_store.get(phone, {"state": "idle"})

def append_history(phone: str, role: str, content: str, limit=20):
    s = get_state(phone)
    hist = s.get("history", [])
    hist.append({"role": role, "content": content, "ts": time.time()})
    s["history"] = hist[-limit:]
    _state_store[phone] = s

# For debugging
def dump(): return {"links": _link_store, "states": _state_store}
