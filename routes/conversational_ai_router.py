from fastapi import APIRouter, WebSocket
from clients.openai_client import OpenAIClient
from config import config
from services.assistant_service import AssistantService

router = APIRouter()

@router.get("/status")
async def get_status():
    return {
        "openai_key": "✅ Set" if config.OPENAI_API_KEY else "❌ Missing",
    }

@router.websocket("/ws/ai")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Only OpenAI logic remains
    # ElevenLabs logic removed
    await websocket.close() 