from fastapi import APIRouter 
from deps import SessionDep
from schemas.schemas import ContentResponse
from services.content_table_service import ContentTableService
from typing import List

router = APIRouter(tags=["content_table"], prefix="/contents")

@router.get("/{content_id}")
async def get_content_by_id(content_id: str, db: SessionDep):
    pass 

@router.get("/")
async def get_public_summary(db: SessionDep) -> List[ContentResponse]:
    content_table_service = ContentTableService(db)
    public_summary = content_table_service.get_public_summary()
    return public_summary


