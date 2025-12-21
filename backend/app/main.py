from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(title="Gov Scheme AI Assistant")

@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Gov Scheme AI Backend is live"
    }


app.include_router(chat_router)

