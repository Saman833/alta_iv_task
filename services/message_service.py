from message_parsers.parser_factory import ParserFactory
from sqlalchemy.orm import Session
from models import Content, Source, Category
from repository.content_repository import ContentRepository
from repository.entity_repository import EntityRepository
from services.telegram_voice_service import TelegramVoiceService
from services.classification_service import ClassificationService
from services.agent_service import AgentService
from clients.elevenlabs_client import ElevenLabsClient
from clients.telegram_messager import TelegramMessager
from config import config
from services.autonomous_analytics_service import AutonomousAnalyticsService
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
        self.agent_service = AgentService()
        self.telegram_messager = TelegramMessager(config.TELEGRAM_BOT_TOKEN)
        self.elevenlabs_client = ElevenLabsClient()
        self.analytics_service = AutonomousAnalyticsService(db)

    def process_message(self, source: str, raw_data: dict):
        parser = self.parser_factory.get_parser(source, raw_data)
        
        if not parser:
            raise ValueError(f"No parser found for source: {source}")
        chat_id = raw_data['message']['chat']['id']
        parsed_data = parser.parse(raw_data)
        if parsed_data['type'] == 'voice' and parsed_data['content_data']['source'] == Source.TELEGRAM: 
            parsed_data = self.telegram_voice_service.process_voice_message(parsed_data)
        elif parsed_data['type'] != 'text':
            raise ValueError(f"Unsupported message type: {parsed_data['type']}")
        if parsed_data['content_data']['source'] == Source.TELEGRAM: 
            # Get the text content from the correct field
            text_content = parsed_data['content_data']['content_data']
            result = self.analytics_service.analyze_user_request_autonomously(text_content)
            if isinstance(result, dict) and "final_user_response" in result:
                self.telegram_messager.send_message(chat_id, result["final_user_response"])
            else:
                self.telegram_messager.send_message(chat_id, "Unable to generate answer. Please try again.")


        return None

        # Pass the parsed content data directly to avoid issues with SQLAlchemy object serialization
        category = self.classification_service.extract_category(**parsed_data['content_data'])
        content = self.update_content(content, {'category': category})
        entities = self.classification_service.extract_entities(**parsed_data['content_data'])
        if entities:
            for entity in entities: 
                entity.content_id = content.id
            self.entity_repository.create_entities(entities)
        call_requires=self.agent_service.run_agent("call_recognizer", parsed_data['content_data'])['requires_call']
        if call_requires == 1:
            message = parsed_data['content_data']
            template_for_agent = f"""
            you are an assitant , if something urgent happens , you need to call the user and inform them about the urgency.
            now that something bad happened , you need to call the user and inform them about the urgency.
            in belew is the message that the user sent to you and you need to inform Saman which is your boss so call him and explina to him the message content and why did you thinked you need to call him. 
            the message is : {message}
            """
            self.start_a_call("", template_for_agent)
        return content

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
    def start_a_call(self, agent_prompt : str , prompt_for_agent : str):
        from config import config
        to_number = config.ELEVENLABS_TO_NUMBER
        phone_number_id = config.ELEVENLABS_PHONE_NUMBER_ID
        agent_id =self.elevenlabs_client.create_elevenlabs_agent(prompt_for_agent)
        self.elevenlabs_client.connect_phone_number_to_agent_elevenlabs(phone_number_id, agent_id)
        return self.elevenlabs_client.start_a_call(agent_id, phone_number_id, to_number)
        
        
    