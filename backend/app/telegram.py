from fastapi import APIRouter, Request
import requests
import os

from app.api.chat import ChatRequest, chat_endpoint

router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    # Ignore non-message updates
    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = str(message["chat"]["id"])
    text = message.get("text")

    if not text:
        return {"ok": True}

    # 🔑 IMPORTANT: pass chat_id INSIDE ChatRequest
    chat_request = ChatRequest(
        message=text,
        chat_id=chat_id
    )

    # Call backend chat logic
    response = chat_endpoint(
        request=request,
        body=chat_request
    )

    # Send reply back to Telegram
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": response.reply
        },
        timeout=15
    )

    return {"ok": True}
