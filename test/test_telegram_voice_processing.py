import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from message_parsers.telegram.telegram_voice_parser import TelegramVoiceParser
from message_parsers.parser_factory import ParserFactory
from services.message_service import MessageService
from services.telegram_voice_service import TelegramVoiceService
from models import Content, Source, ContentType, Base
from sources.telegram.telegram_poller import TelegramPoller


class TestTelegramVoiceProcessing:
    """Test the complete Telegram voice message processing pipeline """
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def sample_voice_message(self):
        """Sample Telegram voice message raw data."""
        return {
            "update_id": 700929839,
            "message": {
                "message_id": 6,
                "from": {
                    "id": 1021474158,
                    "is_bot": False,
                    "first_name": "saman",
                    "username": "S_sa_f_ss_A",
                    "language_code": "en"
                },
                "chat": {
                    "id": 1021474158,
                    "first_name": "saman",
                    "username": "S_sa_f_ss_A",
                    "type": "private"
                },
                "date": 1750631028,
                "voice": {
                    "duration": 2,
                    "mime_type": "audio/ogg",
                    "file_id": "AwACAgQAAxkBAAMGaFiCdCwfOiT9n3slZTl7HeUTMU8AAmgZAALo28FSGKz8j6CbbBU2BA",
                    "file_unique_id": "AgADaBkAAujbwVI",
                    "file_size": 54556
                }
            }
        }
    
    @pytest.fixture
    def mock_telegram_voice_client(self):
        """Mock Telegram voice client."""
        with patch('clients.telegram_voice_client.TelegramVoiceClient') as mock_client:
            # Mock the get_telegram_file_path method
            mock_client.get_telegram_file_path.return_value = "voice/file_123.ogg"
            # Mock the get_voice_message method to return fake audio bytes
            mock_client.get_voice_message.return_value = b"fake_audio_data"
            yield mock_client
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch('clients.openai_client.OpenAIClient') as mock_client:
            # Mock the transcribe_audio method
            mock_client.transcribe_audio.return_value = "Hello, this is a test voice message"
            yield mock_client
    
    def test_voice_parser_parses_correctly(self, sample_voice_message):
        """Test that TelegramVoiceParser correctly parses voice messages."""
        parser = TelegramVoiceParser()
        parsed_data = parser.parse(sample_voice_message)
        
        assert parsed_data['type'] == 'voice'
        assert parsed_data['voice_file_id'] == "AwACAgQAAxkBAAMGaFiCdCwfOiT9n3slZTl7HeUTMU8AAmgZAALo28FSGKz8j6CbbBU2BA"
        assert parsed_data['content_data']['source_id'] == "6"
        assert parsed_data['content_data']['content_type'] == ContentType.VOICE
        assert parsed_data['content_data']['source'] == Source.TELEGRAM
        assert parsed_data['sender_data']['source_id'] == "1021474158"
        assert parsed_data['sender_data']['username'] == "S_sa_f_ss_A"
    
    def test_parser_factory_selects_voice_parser(self, sample_voice_message):
        """Test that ParserFactory correctly selects TelegramVoiceParser for voice messages."""
        factory = ParserFactory()
        parser = factory.get_parser('telegram', sample_voice_message)
        
        assert isinstance(parser, TelegramVoiceParser)
    
    @patch('services.telegram_voice_service.ffmpeg')
    @patch('services.telegram_voice_service.imageio_ffmpeg')
    def test_voice_service_processes_voice_message(
        self, 
        mock_imageio_ffmpeg, 
        mock_ffmpeg, 
        sample_voice_message,
        mock_telegram_voice_client,
        mock_openai_client
    ):
        """Test that TelegramVoiceService correctly processes voice messages."""
        
        mock_imageio_ffmpeg.get_ffmpeg_exe.return_value = "ffmpeg"
        mock_proc = Mock()
        mock_proc.communicate.return_value = (b"converted_audio", None)
        mock_ffmpeg.input.return_value.output.return_value.run_async.return_value = mock_proc
        
        voice_service = TelegramVoiceService()
        voice_service.telegram_voice_client = mock_telegram_voice_client
        voice_service.openai_client = mock_openai_client
        

        parser = TelegramVoiceParser()
        parsed_data = parser.parse(sample_voice_message)
        
        result = voice_service.process_voice_message(parsed_data)
        
        assert result['content_data']['content_data'] == "Hello, this is a test voice message"
        assert result['type'] == 'voice'
        assert result['voice_file_id'] == "AwACAgQAAxkBAAMGaFiCdCwfOiT9n3slZTl7HeUTMU8AAmgZAALo28FSGKz8j6CbbBU2BA"
        
        # Verify that the clients were called correctly
        mock_telegram_voice_client.get_telegram_file_path.assert_called_once_with(
            "AwACAgQAAxkBAAMGaFiCdCwfOiT9n3slZTl7HeUTMU8AAmgZAALo28FSGKz8j6CbbBU2BA"
        )
        mock_telegram_voice_client.get_voice_message.assert_called_once_with("voice/file_123.ogg")
        mock_openai_client.transcribe_audio.assert_called_once()
    
    @patch('services.telegram_voice_service.ffmpeg')
    @patch('services.telegram_voice_service.imageio_ffmpeg')
    def test_complete_voice_message_journey(
        self,
        mock_imageio_ffmpeg,
        mock_ffmpeg,
        db_session,
        sample_voice_message,
        mock_telegram_voice_client,
        mock_openai_client
    ):
        """Test the complete journey from raw voice message to database storage."""
        mock_imageio_ffmpeg.get_ffmpeg_exe.return_value = "ffmpeg"
        mock_proc = Mock()
        mock_proc.communicate.return_value = (b"converted_audio", None)
        mock_ffmpeg.input.return_value.output.return_value.run_async.return_value = mock_proc
        
        with patch('services.message_service.TelegramVoiceService') as mock_voice_service_class:
            mock_voice_service = Mock()
            mock_voice_service.process_voice_message.return_value = {
                'type': 'voice',
                'voice_file_id': "AwACAgQAAxkBAAMGaFiCdCwfOiT9n3slZTl7HeUTMU8AAmgZAALo28FSGKz8j6CbbBU2BA",
                'content_data': {
                    'source_id': "6",
                    'content_type': ContentType.VOICE,
                    'content_data': "Hello, this is a test voice message",
                    'content_html': None,
                    'source': Source.TELEGRAM,
                    'timestamp': datetime.fromtimestamp(1750631028)
                },
                'sender_data': {
                    'source_id': "1021474158",
                    'username': "S_sa_f_ss_A",
                    'first_name': "saman",
                    'last_name': None,
                    'source': Source.TELEGRAM
                }
            }
            mock_voice_service_class.return_value = mock_voice_service
            
            message_service = MessageService(db_session)
            
            result = message_service.process_message('telegram', sample_voice_message)
            
            assert isinstance(result, Content)
            assert result.source_id == "6"
            assert result.content_type == ContentType.VOICE
            assert result.content_data == "Hello, this is a test voice message"
            assert result.source == Source.TELEGRAM
            
            mock_voice_service.process_voice_message.assert_called_once()
            
            saved_content = db_session.query(Content).filter_by(source_id="6").first()
            assert saved_content is not None
            assert saved_content.content_data == "Hello, this is a test voice message"
    
    def test_voice_parser_handles_missing_voice_data(self):
        """Test that TelegramVoiceParser raises error for messages without voice data."""
        parser = TelegramVoiceParser()
        
        invalid_message = {
            "update_id": 700929839,
            "message": {
                "message_id": 6,
                "from": {"id": 1021474158},
                "date": 1750631028
            }
        }
        
        with pytest.raises(ValueError, match="No voice content found in message"):
            parser.parse(invalid_message)
    
    def test_voice_parser_handles_missing_message(self):
        """Test that TelegramVoiceParser raises error for invalid message structure."""
        parser = TelegramVoiceParser()
        
        invalid_message = {
            "update_id": 700929839
        }
        
        with pytest.raises(ValueError, match="No message found in raw_data"):
            parser.parse(invalid_message)
    
    @patch('services.telegram_voice_service.ffmpeg')
    @patch('services.telegram_voice_service.imageio_ffmpeg')
    def test_voice_service_handles_telegram_client_error(
        self,
        mock_imageio_ffmpeg,
        mock_ffmpeg,
        sample_voice_message,
        mock_telegram_voice_client,
        mock_openai_client
    ):
        """Test that TelegramVoiceService handles Telegram client errors gracefully."""
        mock_imageio_ffmpeg.get_ffmpeg_exe.return_value = "ffmpeg"
        mock_proc = Mock()
        mock_proc.communicate.return_value = (b"converted_audio", None)
        mock_ffmpeg.input.return_value.output.return_value.run_async.return_value = mock_proc
        
        mock_telegram_voice_client.get_voice_message.return_value = None
        
        voice_service = TelegramVoiceService()
        voice_service.telegram_voice_client = mock_telegram_voice_client
        voice_service.openai_client = mock_openai_client
        
        parser = TelegramVoiceParser()
        parsed_data = parser.parse(sample_voice_message)
        
        with pytest.raises(ValueError, match="Voice message not found"):
            voice_service.process_voice_message(parsed_data)
    
    def test_telegram_poller_processes_voice_messages(self, sample_voice_message):
        """Test that TelegramPoller correctly identifies and processes voice messages."""
        with patch('sources.telegram.telegram_poller.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "ok": True,
                "result": [sample_voice_message]
            }
            mock_get.return_value = mock_response
            
            mock_message_service = Mock()
            
            poller = TelegramPoller(mock_message_service)
            
            updates = poller.get_updates()
            
            assert len(updates) == 1
            assert updates[0] == sample_voice_message
            
            assert 'voice' in updates[0]['message']


if __name__ == "__main__":
    pytest.main([__file__]) 