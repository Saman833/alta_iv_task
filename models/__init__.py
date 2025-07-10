from sqlalchemy.orm import declarative_base

# Create a shared Base for all models
Base = declarative_base()

from .content import Content, ContentType, Source, Category
from .entity import Entity, EntityType
from .file import File, FileType
from .table import Table

__all__ = [
    'Base',
    'Content',
    'ContentType',
    'EntityType',
    'Source',
    'Category',
    'Entity',
    'File',
    'FileType',
    'Table'
] 