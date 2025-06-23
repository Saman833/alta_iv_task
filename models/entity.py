from sqlalchemy import Column, Integer, String, DateTime, Text , Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base
from sqlalchemy import ForeignKey
from enum import Enum as PyEnum

class EntityType(PyEnum):
    PROJECT = 'PROJECT'
    CONTACT = 'CONTACT'
    DATE = 'DATE'
    KEYWORD = 'KEYWORD'


class Entity(Base):
    """Entities from content (names, emails, phone numbers, etc.).
    Now uses one-to-many relationship with Content via content_id foreign key.
    """
    
    __tablename__ = 'entity'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(36), ForeignKey('content.id'), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False)  # 'PROJECT', 'CONTACT', 'DATE', 'KEYWORD'
    entity_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship to content
    content = relationship("Content", back_populates="entities")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, type='{self.entity_type}', value='{self.entity_value}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'entity_type': self.entity_type,
            'entity_value': self.entity_value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 