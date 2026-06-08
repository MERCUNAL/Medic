from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import os
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "http://127.0.0.1:8000/chat"


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    user_id = str(
        update.effective_user.id
    )

    response = requests.post(
        API_URL,
        json={
            "message": text,
            "session_id": user_id
        }
    )

    data = response.json()

    await update.message.reply_text(
        data["answer"]
    )


app = Application.builder().token(
    BOT_TOKEN
).build()

app.add_handler(
    MessageHandler(
        filters.TEXT,
        handle_message
    )
)

app.run_polling()