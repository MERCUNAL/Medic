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


@app.post("/chat")
async def chat(req: ChatRequest):

    answer, options = get_response(
        req.query,
        req.thread_id
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