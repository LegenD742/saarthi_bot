# from fastapi import FastAPI
# from app.api.chat import router as chat_router

# app = FastAPI(title="Gov Scheme AI Assistant")

# @app.get("/")
# def health_check():
#     return {
#         "status": "running",
#         "message": "Gov Scheme AI Backend is live"
#     }


# app.include_router(chat_router)

from fastapi import FastAPI

# Chat API
from app.api.chat import router as chat_router

# Telegram webhook API
from app.telegram import router as telegram_router


# ----------------------------------
# FastAPI App
# ----------------------------------
app = FastAPI(title="Gov Scheme AI Assistant")


# ----------------------------------
# Health check (Render needs this)
# ----------------------------------
@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Gov Scheme AI Backend is live"
    }


# ----------------------------------
# Routers
# ----------------------------------
app.include_router(chat_router)
app.include_router(telegram_router)
