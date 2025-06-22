from message_parsers.parser_factory import ParserFactory
from sqlalchemy.orm import Session
from models import Content, Classification, Entity, Sender, ContentSender, ContentEntity, ContentType, Source
from typing import Optional, Dict, Any, List
from datetime import datetime
from repository.content_repository import ContentRepository

class MessageService:
    def __init__(self, db: Session):
        self.db = db
        self.parser_factory = ParserFactory()
        self.content_repository = ContentRepository(self.db)
    
    def process_message(self, source: str, raw_data: dict):
        """Process a message from any source."""
        parser = self.parser_factory.get_parser(source, raw_data)
        
        if not parser:
            raise ValueError(f"No parser found for source: {source}")
        
        parsed_data = parser.parse(raw_data)
        
        if parsed_data['type'] == 'voice':
            return self._process_voice_message(parsed_data)
        elif parsed_data['type'] == 'text':
            return self._process_text_message(parsed_data)
        else:
            raise ValueError(f"No parser found for message: {raw_data['type']}")
        
    def _process_text_message(self, message_raw: dict):
        content_data = message_raw['content_data']
        content = Content(
            source_id=content_data['source_id'],
            content_type=content_data['content_type'],
            content_data=content_data['content_data'],
            content_html=content_data['content_html'],
            source=content_data['source'],
            timestamp=content_data['timestamp']
        )
        return self.content_repository.create_content(content)

    def _process_voice_message(self, message_raw: dict):
        pass 
    
        
        
        
    