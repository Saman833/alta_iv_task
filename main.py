import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.message_service import MessageService
from sources.telegram.telegram_poller import TelegramPoller
from db import SessionLocal
from routes.content_table_router import router as content_table_router
from routes.conversational_ai_router import router as conversational_ai_router
from routes.file_router import router as file_router
from routes.analytics_router import router as analytics_router


app = FastAPI(title="Altair Code Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(content_table_router)
app.include_router(conversational_ai_router)
app.include_router(file_router)
app.include_router(analytics_router)

telegram_poller_thread = None
telegram_poller = None
message_service = None

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event to initialize the telegram poller thread.
    """
    global telegram_poller_thread, telegram_poller, message_service
    db = SessionLocal()
    message_service = MessageService(db)
    telegram_poller = TelegramPoller(message_service)
    telegram_poller_thread = threading.Thread(
        target=telegram_poller.start_polling,
        daemon=True
    )
    telegram_poller_thread.start()
    print("✅ FastAPI startup completed with Telegram poller.")

@app.on_event("shutdown")
async def shutdown_event():
    global telegram_poller
    if telegram_poller:
        telegram_poller.is_running = False

@app.get("/")
async def root():
    return {"message": "Altair Code Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    global telegram_poller_thread
    telegram_status = "disabled" if telegram_poller_thread is None else ("running" if telegram_poller_thread.is_alive() else "stopped")
    return {
        "status": "healthy",
        "telegram_poller_thread": telegram_status,
        "note": "Email poller removed. Only Telegram poller is active.",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    pass 
