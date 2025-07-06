from fastapi import APIRouter, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from services.conversational_ai_service import ConversationalAIService
from clients.elevenlabs_client import ELEVENLABS_AVAILABLE
from config import config

router = APIRouter(prefix="/conversational-ai", tags=["conversational-ai"])

# Initialize the conversational AI service
conversational_ai_service = ConversationalAIService()

@router.get("/")
async def root():
    """Root endpoint for conversational AI service"""
    return {
        "message": "Conversational AI Service is running!",
        "endpoints": ["/html", "/ws/voice"],
        "status": {
            "elevenlabs_available": "✅ Available" if ELEVENLABS_AVAILABLE else "❌ Not Available",
            "elevenlabs_key": "✅ Set" if config.ELEVENLABS_API_KEY else "❌ Missing",
            "openai_key": "✅ Set" if config.OPENAI_API_KEY else "❌ Missing"
        }
    }

@router.get("/html")
async def serve_html():
    """Serve the HTML frontend for the conversational AI agent"""
    # Read the frontend HTML file
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(
            content="Frontend file not found. Please ensure frontend.html exists.", 
            status_code=404
        )

@router.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    """WebSocket endpoint for voice conversation"""
    if not config.OPENAI_API_KEY:
        await websocket.close(code=4000, reason="OpenAI API key not configured")
        return
    
    if not ELEVENLABS_AVAILABLE:
        await websocket.close(code=4001, reason="ElevenLabs not available")
        return
    
    await conversational_ai_service.handle_websocket_conversation(websocket) 