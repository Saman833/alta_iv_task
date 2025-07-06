from fastapi import APIRouter 
from services.assistant_service import AssistantService
from deps import SessionDep

router = APIRouter(tags=["assistant"],prefix="/assistant")

@router.post("/new_chat")
async def new_chat(chat:str, db: SessionDep):
    assistant_service = AssistantService(db)
    return assistant_service.handle_new_chat(chat)
