from fastapi import FastAPI
from pydantic import BaseModel

from rag.chatbot import get_response

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    session_id: str


@app.post("/chat")
async def chat(req: ChatRequest):

    answer, options = get_response(
        req.message,
        req.session_id
    )

    return {
        "answer": answer,
        "options": options
    }


@app.get("/")
async def root():
    return {
        "status": "running"
    }