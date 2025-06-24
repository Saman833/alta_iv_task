from fastapi import APIRouter, HTTPException, status
from deps import SessionDep
from schemas.schemas import ContentResponse, SearchQuery
from services.content_table_service import ContentTableService
from typing import List
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["content_table"], prefix="/contents")

@router.get("/{content_id}")
async def get_content_by_id(content_id: str, db: SessionDep):
    try:
        content_table_service = ContentTableService(db)
        content = content_table_service.get_public_summary(content_id=content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content with id {content_id} not found"
            )
        return content[0] if content else None
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/", response_model=List[ContentResponse])
async def get_public_summary(db: SessionDep) -> List[ContentResponse]:
    try:
        content_table_service = ContentTableService(db)
        public_summary = content_table_service.get_public_summary()
        return public_summary
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
@router.post("/search_query") 
async def search_contents(search_query: SearchQuery, db: SessionDep) -> List[ContentResponse]:
    try:
        content_table_service = ContentTableService(db)
        contents = content_table_service.search_contents(search_query)
        return contents
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

