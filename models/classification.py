from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from . import Base

class Classification(Base):
    """Content classifications (urgent, work, personal, etc.)."""
    
    __tablename__ = 'classifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(36), ForeignKey('content.id'), nullable=False)
    category = Column(String(50), nullable=False)  # 'urgent', 'work', 'personal', 'spam', 'news'
    confidence = Column(Float, nullable=False)  # confidence score 0.0-1.0
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Classification(id={self.id}, category='{self.category}', confidence={self.confidence})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'category': self.category,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 