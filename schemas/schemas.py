from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class EntityResponse(BaseModel):
    """Pydantic model for Entity responses"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[int] = None
    content_id: str
    entity_type: str
    entity_value: str
    created_at: Optional[datetime] = None


class ContentResponse(BaseModel):
    """Pydantic model for Content responses"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str
    source_id: str
    content_type: str
    content_data: str
    content_html: Optional[str] = None
    source: str
    category: str
    subject: Optional[str] = None
    timestamp: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    entities: List[EntityResponse] = []


class Entities(BaseModel): 
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    entities: List[EntityResponse]
    count: int = 10 


class Public_Summary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    content: ContentResponse
    entities: Entities
    


