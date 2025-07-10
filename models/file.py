from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base
from sqlalchemy import ForeignKey
from enum import Enum as PyEnum
from .content import FlexibleEnum
from pydantic import BaseModel
from typing import Optional

class FileType(PyEnum):
    CSV = 'CSV'
    PDF = 'PDF'
    DOC = 'DOC'
    XLSX = 'XLSX'
    OTHER = 'OTHER'

class CreateFile(BaseModel):
    """Pydantic model for creating files"""
    file_name: str
    file_content: str
    folder_id: str
    file_type: FileType
    file_size: int = 0
    user_id: Optional[str] = None

class File(Base):
    __tablename__ = 'file'
    id = Column(String(36), primary_key=True)
    file_name = Column(String(255), nullable=False)
    detail_summary = Column(Text, nullable=True)
    folder_id = Column(String(255), nullable=False)
    file_type = Column(FlexibleEnum(FileType), nullable=False, default=FileType.CSV)
    file_size = Column(Integer, nullable=False)
    user_id = Column(String(36), nullable=False)
    file_created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<File(id='{self.id}', file_name='{self.file_name}', file_type='{self.file_type}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'detail_summary': self.detail_summary,
            'folder_id': self.folder_id,
            'file_type': self.file_type.value if self.file_type else None,
            'file_size': self.file_size,
            'user_id': self.user_id,
            'file_created_at': self.file_created_at.isoformat() if self.file_created_at else None
        }

class Folder(Base):
    __tablename__ = 'folder'
    id = Column(String(36), primary_key=True)
    folder_name = Column(String(255), nullable=False)
    detail_summary = Column(Text, nullable=True)
    user_id = Column(String(36), nullable=False)
    folder_created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Folder(id='{self.id}', folder_name='{self.folder_name}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'folder_name': self.folder_name,
            'detail_summary': self.detail_summary,
            'user_id': self.user_id,
            'folder_created_at': self.folder_created_at.isoformat() if self.folder_created_at else None
        }