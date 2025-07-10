from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from . import Base
from enum import Enum as PyEnum

class Table(Base):
    __tablename__ = 'table' 
    id = Column(String(36), primary_key=True)
    table_name = Column(String(255), nullable=False)
    folder_id = Column(String(36), nullable=False) 
    user_id = Column(String(36), nullable=False)
    table_description = Column(Text, nullable=True)
    table_created_at = Column(DateTime, default=func.now())
    table_updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Table(id='{self.id}', table_name='{self.table_name}', folder_id='{self.folder_id}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'table_name': self.table_name,
            'folder_id': self.folder_id,
            'user_id': self.user_id,
            'table_description': self.table_description,
            'table_created_at': self.table_created_at.isoformat() if self.table_created_at else None,
            'table_updated_at': self.table_updated_at.isoformat() if self.table_updated_at else None
        }
