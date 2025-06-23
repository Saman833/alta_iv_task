from sqlalchemy.ext.asyncio import AsyncSession
from repository.content_repository import ContentRepository   
from schemas.schemas import ContentResponse, EntityResponse 
from typing import List, Optional
from datetime import datetime

class ContentTableService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.content_repository = ContentRepository(db)
    
    async def get_public_summary(self) -> List[ContentResponse]:
        contents = await self.content_repository.get_public_summary()
        
        # Convert SQLAlchemy objects to Pydantic models
        content_responses = []
        for content in contents:
            # Convert entities to EntityResponse objects
            entity_responses = []
            for entity in content.entities:
                entity_response = EntityResponse(
                    id=entity.id,
                    content_id=entity.content_id,
                    entity_type=entity.entity_type.value if entity.entity_type else str(entity.entity_type),
                    entity_value=entity.entity_value,
                    created_at=entity.created_at
                )
                entity_responses.append(entity_response)
            
            # Convert content to ContentResponse object with entities
            content_response = ContentResponse(
                id=content.id,
                source_id=content.source_id,
                content_type=content.content_type.value if content.content_type else str(content.content_type),
                content_data=content.content_data,
                content_html=content.content_html,
                source=content.source.value if content.source else str(content.source),
                category=content.category.value if content.category else str(content.category),
                subject=content.subject,
                timestamp=content.timestamp,
                created_at=content.created_at,
                updated_at=content.updated_at,
                entities=entity_responses  # Include the entities
            )
            content_responses.append(content_response)
        
        return content_responses

    # async def search_contents(self, search_query: SearchQuery) -> List[ContentResponse]:
    #     """
    #     Search contents based on the SearchQuery parameters
    #     """
    #     # Extract parameters from search query
    #     contents = await self.content_repository.search_contents(
    #         keywords=search_query.keywords,
    #         start_date=search_query.startDate,
    #         end_date=search_query.endDate,
    #         date_mentioned=search_query.Date_Mentiond,
    #         category=search_query.category,
    #         source=search_query.source
    #     )
        
    #     # Convert SQLAlchemy objects to Pydantic models (same as get_public_summary)
    #     content_responses = []
    #     for content in contents:
    #         # Convert entities to EntityResponse objects
    #         entity_responses = []
    #         for entity in content.entities:
    #             entity_response = EntityResponse(
    #                 id=entity.id,
    #                 content_id=entity.content_id,
    #                 entity_type=entity.entity_type.value if entity.entity_type else str(entity.entity_type),
    #                 entity_value=entity.entity_value,
    #                 created_at=entity.created_at
    #             )
    #             entity_responses.append(entity_response)
            
    #         # Convert content to ContentResponse object with entities
    #         content_response = ContentResponse(
    #             id=content.id,
    #             source_id=content.source_id,
    #             content_type=content.content_type.value if content.content_type else str(content.content_type),
    #             content_data=content.content_data,
    #             content_html=content.content_html,
    #             source=content.source.value if content.source else str(content.source),
    #             category=content.category.value if content.category else str(content.category),
    #             subject=content.subject,
    #             timestamp=content.timestamp,
    #             created_at=content.created_at,
    #             updated_at=content.updated_at,
    #             entities=entity_responses  # Include the entities
    #         )
    #         content_responses.append(content_response)
        
    #     return content_responses
    
    