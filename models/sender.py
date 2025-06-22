from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from . import Base

class Sender(Base):
    """Senders table for all message sources."""
    
    __tablename__ = 'senders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=False)  # 'gmail', 'telegram', 'slack', 'whatsapp'
    platform_user_id = Column(String(255), nullable=True)  # platform-specific user ID
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Sender(id={self.id}, name='{self.name}', platform='{self.platform}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'platform': self.platform,
            'platform_user_id': self.platform_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 