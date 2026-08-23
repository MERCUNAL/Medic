import httpx
from ..config import RAG_SERVICE_URL

async def query_rag(query: str, thread_id: str, user_role: str = "general user", user_location: str = "unknown") -> dict:
    url = f"{RAG_SERVICE_URL.rstrip('/')}/chat"
    payload = {"query": query, "thread_id": thread_id, "user_role": user_role, "user_location": user_location}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()  # {"answer":..., "options":[...]}

def thread_for_phone(phone: str) -> str:
    return f"wa:{phone}"
