import threading
import time
from fastapi import FastAPI
from sources.email.email_poller import EmailPoller
from services.message_service import MessageService
from sources.telegram.telegram_poller import TelegramPoller
from db import SessionLocal

app = FastAPI(title="Altair Code Backend", version="1.0.0")

email_poller_thread = None
telegram_poller_thread = None
email_poller = None
telegram_poller = None
message_service = None

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event to initialize both email and telegram poller threads 
    each of those will be running in a separate thread and even the thread will sleep from duratino of time 
    to modfify time duration of sleep , we can change the time in the config.json file
    """
    
    global email_poller_thread, telegram_poller_thread, email_poller, telegram_poller, message_service
 
    db = SessionLocal()
    message_service = MessageService(db)
    
 
    email_poller = EmailPoller(message_service)
    email_poller_thread = threading.Thread(
        target=email_poller.start_polling,
        daemon=True
    )
    email_poller_thread.start()
    

    telegram_poller = TelegramPoller(message_service)
    telegram_poller_thread = threading.Thread(
        target=telegram_poller.start_polling,
        daemon=True
    )
    telegram_poller_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    
    global email_poller, telegram_poller
    if email_poller:
        email_poller.is_running = False
    if telegram_poller:
        telegram_poller.is_running = False

@app.get("/")
async def root():
    return {"message": "Altair Code Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    global email_poller_thread, telegram_poller_thread
    
    email_status = "running" if email_poller_thread and email_poller_thread.is_alive() else "stopped"
    telegram_status = "running" if telegram_poller_thread and telegram_poller_thread.is_alive() else "stopped"
    
    return {
        "status": "healthy",
        "email_poller_thread": email_status,
        "telegram_poller_thread": telegram_status,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    pass 
