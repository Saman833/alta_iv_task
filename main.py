import threading
import time
from fastapi import FastAPI
from sources.email.email_poller import EmailPoller
from services.message_service import MessageService
from db import SessionLocal

app = FastAPI(title="Alta Code Backend", version="1.0.0")

# Global variables
email_poller_thread = None
email_poller = None
message_service = None

@app.on_event("startup")
async def startup_event():
    """FastAPI startup event to initialize the email poller."""
    global email_poller_thread, email_poller, message_service
    
    # Get database session
    db = SessionLocal()
    message_service = MessageService(db)
    
    email_poller = EmailPoller(message_service)
    email_poller_thread = threading.Thread(
        target=email_poller.start_polling,
        daemon=True
    )
    email_poller_thread.start()

@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI shutdown event to stop the email poller."""
    global email_poller
    if email_poller:
        email_poller.is_running = False

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Alta Code Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global email_poller_thread
    
    thread_status = "running" if email_poller_thread and email_poller_thread.is_alive() else "stopped"
    
    return {
        "status": "healthy",
        "email_poller_thread": thread_status,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    pass 
