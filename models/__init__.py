from sqlalchemy.orm import declarative_base

# Create a shared Base for all models
Base = declarative_base()

from .content import Content, ContentType, Source
from .sender import Sender
from .entity import Entity
from .classification import Classification
from .metadata import SourceMetadata
from .content_sender import ContentSender
from .content_entity import ContentEntity

__all__ = [
    'Base',
    'Content',
    'ContentType',
    'Source',
    'Sender',
    'Entity', 
    'Classification',
    'SourceMetadata',
    'ContentSender',
    'ContentEntity'
] 