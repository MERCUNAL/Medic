from fastapi import FastAPI
from pydantic import BaseModel

from rag.chatbot import get_response

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    thread_id: str
    user_role: str = "general user"
    user_location: str = "unknown"

@app.post("/chat")
async def chat(req: ChatRequest):
    answer, options = get_response(
        req.query,
        req.thread_id,
        req.user_role,
        req.user_location
    )
    return {"answer": answer, "options": options}