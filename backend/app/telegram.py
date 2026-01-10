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

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text")

    if not text:
        return {"ok": True}

    # IMPORTANT: use chat_id as session id
    request.state.session_override = str(chat_id)

    response = chat_endpoint(
        request=request,
        body=ChatRequest(message=text)
    )

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": response.reply
        }
    )

    return {"ok": True}
