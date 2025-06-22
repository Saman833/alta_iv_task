from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from . import Base

class ContentSender(Base):
    """Many-to-many relationship between content and senders."""
    
    __tablename__ = 'content_senders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(36), ForeignKey('content.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('senders.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ContentSender(content_id='{self.content_id}', sender_id={self.sender_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'sender_id': self.sender_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 