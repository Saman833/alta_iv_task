from sqlalchemy import Column, String, DateTime, Text, Integer, Enum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, String as SQLAString
from . import Base
from enum import Enum as PyEnum
import uuid
"""
    I should change name of this model and its classses to message if I get time later 
    for now I will keep it as content 
"""
class ContentType(PyEnum):
    TEXT = 'text'
    VOICE = 'voice'

class Source(PyEnum):
    EMAIL = 'email'
    TELEGRAM = 'telegram'
    
class Category(PyEnum):
    SPAM = 'spam'
    MEETING = 'meeting'
    TASK = 'task'
    INFORMATION = 'information'
    IDEA = 'idea'
    OTHER = 'other'
    
class FlexibleEnum(TypeDecorator):
    """A flexible enum type that can handle both enum objects and strings"""
    
    impl = SQLAString  # Tells SQLAlchemy to store the value as a string
    
    def __init__(self, enum_class):
        self.enum_class = enum_class
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if hasattr(value, 'value'):
            return value.value
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return self.enum_class(value)
        except ValueError:
            # in case  it dosent math any enum value
            return value
    
    @property
    def python_type(self):
        return self.enum_class
    
class Content(Base):
    """Main content table for all message types (text, voice, image, etc.).
    
    Required columns for message model:
    - source: message source (email, telegram, etc.)
    - date: message timestamp
    - category: message classification (via Category enum)
    - subject: subject of the message (for email messages)
    - original text: message content
    """
    
    __tablename__ = 'content'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))   
    source_id = Column(String(255), nullable=False)  
    content_type = Column(FlexibleEnum(ContentType), nullable=False)   
    category = Column(FlexibleEnum(Category), nullable=False, default=Category.OTHER)
    subject = Column(String(255), nullable=True)    
    content_data = Column(Text, nullable=False)         
    content_html = Column(Text, nullable=True)          
    source = Column(FlexibleEnum(Source), nullable=False)        
    timestamp = Column(DateTime, nullable=False)        
    created_at = Column(DateTime, default=func.now())   
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
 
    entities = relationship("Entity", back_populates="content", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('source_id', 'source', name='uq_source_id_source'),
    )
    
    def __repr__(self):
        return f"<Content(id='{self.id}', source_id='{self.source_id}', type='{self.content_type}', source='{self.source}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'content_type': self.content_type.value if self.content_type else None,
            'content_data': self.content_data,
            'content_html': self.content_html,
            'source': self.source.value if self.source else None,
            'category': self.category.value if self.category else None,
            'subject': self.subject if self.subject else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 