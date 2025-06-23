from message_parsers.parser_factory import ParserFactory
from sqlalchemy.orm import Session
from models import Content, Source, Category
from repository.content_repository import ContentRepository
from repository.entity_repository import EntityRepository
from services.telegram_voice_service import TelegramVoiceService
from services.classification_service import ClassificationService
class MessageService:
    """
        this function is the core of the message processing pipeline 
        what it does is :
        1- get first polled message from sources 
        2-passing the message to parser factory to get the parsed data
        3-passing the parsed data to telegram voice service if its a voice message response from telegram 
        4- passing to classification service to extract category and entities
        5- saving the content and entities to the database
       
    """
    def __init__(self, db: Session):
        self.db = db
        self.parser_factory = ParserFactory()
        self.content_repository = ContentRepository(self.db)
        self.entity_repository = EntityRepository(self.db)
        self.telegram_voice_service = TelegramVoiceService()
        self.classification_service = ClassificationService()

    def process_message(self, source: str, raw_data: dict):
        parser = self.parser_factory.get_parser(source, raw_data)
        
        if not parser:
            raise ValueError(f"No parser found for source: {source}")
        
        parsed_data = parser.parse(raw_data)
        if parsed_data['type'] == 'voice' and parsed_data['content_data']['source'] == Source.TELEGRAM: 
            parsed_data = self.telegram_voice_service.process_voice_message(parsed_data)
        elif parsed_data['type'] != 'text':
            raise ValueError(f"Unsupported message type: {parsed_data['type']}")
        
        content = self.create_content_message(parsed_data)
        if content is None:
            print(f"Skipping duplicate message from {source}")
            return None
        
        # Pass the parsed content data directly to avoid issues with SQLAlchemy object serialization
        category = self.classification_service.extract_category(**parsed_data['content_data'])
        content = self.update_content(content, {'category': category})
        entities = self.classification_service.extract_entities(**parsed_data['content_data'])
        if entities:
            for entity in entities: 
                entity.content_id = content.id
            self.entity_repository.create_entities(entities)

    def create_content_message(self, parsed_data: dict):
        content = Content(**parsed_data['content_data'])
        return self.content_repository.create_content(content) 

    def update_content(self, content: Content, data: dict):
        try : 
            for key, value in data.items():
                if key == 'category' and isinstance(value, str):
                    # Convert string category to Category enum
                    try:
                        value = Category(value)
                    except ValueError:
                        # If the category string is invalid, use OTHER as fallback
                        value = Category.OTHER
                setattr(content, key, value)
            self.content_repository.update_content(content)
        except Exception as e:
            raise ValueError(f"Error updating content: {e}")
        return content

    def get_first_unread_source_id_telegram(self):
        """
        Get the next offset for Telegram by adding 1 to the last processed source_id
        this way telegram poller will get the next message to process and avoid processing the same message again 
        this approach works even if platform shut down and restart 
        """
        last_source_id = self.content_repository.get_last_source_id(source=Source.TELEGRAM)
        return last_source_id + 1 if last_source_id else 30
        
        
        
    