from sqlalchemy.orm import Session
from repository.content_repository import ContentRepository   
from repository.entity_repository import EntityRepository
from schemas.schemas import ContentResponse, EntityResponse, SearchQuery, CreateContentRequest, CreateEntityRequest
from models import Content, Entity
from typing import List

class ContentTableService:
    def __init__(self, db: Session):
        self.db = db
        self.content_repository = ContentRepository(db)
        self.entity_repository = EntityRepository(db)
    
    def get_public_summary(self) -> List[ContentResponse]:
        contents = self.content_repository.get_public_summary()
        
        # Convert SQLAlchemy objects to Pydantic models
        content_responses = []
        for content in contents:
            # Convert entities to EntityResponse objects
            entity_responses = []
            for entity in content.entities:
                entity_response = EntityResponse(
                    id=entity.id,
                    content_id=entity.content_id,
                    entity_type=entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                    entity_value=entity.entity_value,
                    created_at=entity.created_at
                )
                entity_responses.append(entity_response)
            
            # Convert content to ContentResponse object with entities
            content_response = ContentResponse(
                id=content.id,
                source_id=content.source_id,
                content_type=content.content_type.value if hasattr(content.content_type, 'value') else str(content.content_type),
                content_data=content.content_data,
                content_html=content.content_html,
                source=content.source.value if hasattr(content.source, 'value') else str(content.source),
                category=content.category.value if hasattr(content.category, 'value') else str(content.category),
                subject=content.subject,
                timestamp=content.timestamp,
                created_at=content.created_at,
                updated_at=content.updated_at,
                entities=entity_responses  # Include the entities
            )
            content_responses.append(content_response)
        
        return content_responses
    
    def search_contents(self, search_query: SearchQuery) -> List[ContentResponse]:
        contents = self.content_repository.search_contents(search_query)
        
        # Convert SQLAlchemy objects to Pydantic models
        content_responses = []
        for content in contents:
            # Convert entities to EntityResponse objects
            entity_responses = []
            for entity in content.entities:
                entity_response = EntityResponse(
                    id=entity.id,
                    content_id=entity.content_id,
                    entity_type=entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                    entity_value=entity.entity_value,
                    created_at=entity.created_at
                )
                entity_responses.append(entity_response)
            
            # Convert content to ContentResponse object with entities
            content_response = ContentResponse(
                id=content.id,
                source_id=content.source_id,
                content_type=content.content_type.value if hasattr(content.content_type, 'value') else str(content.content_type),
                content_data=content.content_data,
                content_html=content.content_html,
                source=content.source.value if hasattr(content.source, 'value') else str(content.source),
                category=content.category.value if hasattr(content.category, 'value') else str(content.category),
                subject=content.subject,
                timestamp=content.timestamp,
                created_at=content.created_at,
                updated_at=content.updated_at,
                entities=entity_responses  # Include the entities
            )
            content_responses.append(content_response)
        
        return content_responses
    
    def create_content_manually(self, content_request: CreateContentRequest) -> ContentResponse:
        """Manually create a new content entry"""
        # Create content object
        content = Content(
            source_id=content_request.source_id,
            content_type=content_request.content_type,
            content_data=content_request.content_data,
            content_html=content_request.content_html,
            source=content_request.source,
            category=content_request.category,
            subject=content_request.subject,
            timestamp=content_request.timestamp
        )
        
        # Save to database
        saved_content = self.content_repository.create_content(content)
        
        if not saved_content:
            raise ValueError("Failed to create content. Possible duplicate source_id and source combination.")
        
        # Convert to response format with safe enum handling
        content_response = ContentResponse(
            id=saved_content.id,
            source_id=saved_content.source_id,
            content_type=saved_content.content_type.value if hasattr(saved_content.content_type, 'value') else str(saved_content.content_type),
            content_data=saved_content.content_data,
            content_html=saved_content.content_html,
            source=saved_content.source.value if hasattr(saved_content.source, 'value') else str(saved_content.source),
            category=saved_content.category.value if hasattr(saved_content.category, 'value') else str(saved_content.category),
            subject=saved_content.subject,
            timestamp=saved_content.timestamp,
            created_at=saved_content.created_at,
            updated_at=saved_content.updated_at,
            entities=[]
        )
        
        return content_response
    
    def create_entity_manually(self, entity_request: CreateEntityRequest) -> EntityResponse:
        """Manually create a new entity entry"""
        # Validate that content exists
        content = self.content_repository.get_content_by_id(entity_request.content_id)
        if not content:
            raise ValueError(f"Content with id {entity_request.content_id} not found")
        
        # Create entity object
        entity = Entity(
            content_id=entity_request.content_id,
            entity_type=entity_request.entity_type,
            entity_value=entity_request.entity_value
        )
        
        # Save to database
        saved_entity = self.entity_repository.create_entity(entity)
        
        # Convert to response format with safe enum handling
        entity_response = EntityResponse(
            id=saved_entity.id,
            content_id=saved_entity.content_id,
            entity_type=saved_entity.entity_type.value if hasattr(saved_entity.entity_type, 'value') else str(saved_entity.entity_type),
            entity_value=saved_entity.entity_value,
            created_at=saved_entity.created_at
        )
        
        return entity_response

