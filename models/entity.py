from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from . import Base

class Entity(Base):
    """Entities from content (names, emails, phone numbers, etc.).
    Now uses many-to-many relationship with Content via ContentEntity table.
    """
    
    __tablename__ = 'entity'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)  # 'person', 'email', 'phone', 'address', 'date'
    entity_value = Column(Text, nullable=False)
    confidence = Column(Integer, nullable=True)  # confidence score 0-100
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Entity(id={self.id}, type='{self.entity_type}', value='{self.entity_value}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_value': self.entity_value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 