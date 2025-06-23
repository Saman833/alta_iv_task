from message_parsers.parser_factory import ParserFactory
from sqlalchemy.orm import Session
from models import Content, Source
from repository.content_repository import ContentRepository
from services.telegram_voice_service import TelegramVoiceService
from clients.telegram_voice_client import TelegramVoiceClient
from clients.openai_client import OpenAIClient

class MessageService:
    def __init__(self, db: Session):
        self.db = db
        self.parser_factory = ParserFactory()
        self.content_repository = ContentRepository(self.db)
        self.telegram_voice_service = TelegramVoiceService()

    def process_message(self, source: str, raw_data: dict):
        """ This function process a message from any source."""
        parser = self.parser_factory.get_parser(source, raw_data)
        
        if not parser:
            raise ValueError(f"No parser found for source: {source}")
        
        parsed_data = parser.parse(raw_data)
        if parsed_data['type'] == 'voice' and parsed_data['content_data']['source'] == Source.TELEGRAM: 
            parsed_data = self.telegram_voice_service.process_voice_message(parsed_data)
        elif parsed_data['type'] != 'text':
            raise ValueError(f"Unsupported message type: {parsed_data['type']}")
        
        content = self.create_content_message(parsed_data)
        return content

    def create_content_message(self, parsed_data: dict):
        content = Content(**parsed_data['content_data'])
        return self.content_repository.create_content(content) 

    def get_first_unread_source_id_telegram(self):
        """Get the next offset for Telegram by adding 1 to the last processed source_id."""
        last_source_id = self.content_repository.get_last_source_id(source=Source.TELEGRAM)
        return last_source_id + 1 if last_source_id else 0
        
        
        
    