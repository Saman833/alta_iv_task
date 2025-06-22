from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from . import Base

class SourceMetadata(Base):
    """Source-specific metadata (Gmail thread ID, Telegram chat ID, etc.)."""
    
    __tablename__ = 'source_metadata'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(36), ForeignKey('content.id'), nullable=False)
    metadata_source = Column(String(50), nullable=False)  # 'gmail_thread_id', 'telegram_chat_id', 's3_key'
    metadata_id = Column(String(255), nullable=False)     # actual value (thread ID, chat ID, S3 key)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<SourceMetadata(id={self.id}, source='{self.metadata_source}', value='{self.metadata_id}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'metadata_source': self.metadata_source,
            'metadata_id': self.metadata_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 