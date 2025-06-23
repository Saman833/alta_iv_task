import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from message_parsers.telegram.telegram_text_parser import TelegramTextParser
from message_parsers.parser_factory import ParserFactory
from services.message_service import MessageService
from models import Content, Source, ContentType
from sources.telegram.telegram_poller import TelegramPoller


class TestTelegramTextParser:
    """Test the Telegram text parser component."""
    
    @pytest.fixture
    def sample_telegram_text_data(self):
        """Sample Telegram text message data."""
        return {
            "update_id": 700929842,
            "message": {
                "message_id": 9,
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
                "date": 1750635741,
                "text": "Hello, this is a test message!"
            }
        }
    
    @pytest.fixture
    def parser(self):
        """Create a Telegram text parser instance."""
        return TelegramTextParser()
    
    def test_parse_valid_text_message(self, parser, sample_telegram_text_data):
        """Test parsing a valid Telegram text message."""
        result = parser.parse(sample_telegram_text_data)
        
        assert result['type'] == 'text'
        assert 'content_data' in result
        assert 'sender_data' in result
        
        content_data = result['content_data']
        assert content_data['source_id'] == '9'
        assert content_data['content_type'] == ContentType.TEXT
        assert content_data['content_data'] == 'Hello, this is a test message!'
        assert content_data['content_html'] is None
        assert content_data['source'] == Source.TELEGRAM
        assert isinstance(content_data['timestamp'], datetime)
        
        sender_data = result['sender_data']
        assert sender_data['source_id'] == '1021474158'
        assert sender_data['username'] == 'S_sa_f_ss_A'
        assert sender_data['first_name'] == 'saman'
        assert sender_data['last_name'] is None
        assert sender_data['source'] == Source.TELEGRAM
    
    def test_parse_message_without_text(self, parser):
        """Test parsing a message without text content."""
        data_without_text = {
            "update_id": 700929842,
            "message": {
                "message_id": 9,
                "from": {"id": 1021474158},
                "chat": {"id": 1021474158},
                "date": 1750635741
            }
        }
        
        with pytest.raises(ValueError, match="No text content found in message"):
            parser.parse(data_without_text)
    
    def test_parse_message_without_message(self, parser):
        """Test parsing data without message field."""
        data_without_message = {
            "update_id": 700929842
        }
        
        with pytest.raises(ValueError, match="No message found in raw_data"):
            parser.parse(data_without_message)
    
    def test_parse_message_with_optional_fields(self, parser):
        """Test parsing message with optional fields missing."""
        data_with_optional_fields = {
            "update_id": 700929842,
            "message": {
                "message_id": 9,
                "from": {
                    "id": 1021474158,
                    "first_name": "saman"
                },
                "chat": {
                    "id": 1021474158
                },
                "date": 1750635741,
                "text": "Simple message"
            }
        }
        
        result = parser.parse(data_with_optional_fields)
        
        # Should handle missing optional fields gracefully
        sender_data = result['sender_data']
        assert sender_data['username'] is None
        assert sender_data['last_name'] is None
        assert sender_data['first_name'] == 'saman'


class TestParserFactory:
    """Test the parser factory component."""
    
    @pytest.fixture
    def factory(self):
        """Create a parser factory instance."""
        return ParserFactory()
    
    def test_get_telegram_text_parser(self, factory):
        """Test factory returns correct parser for Telegram text messages."""
        telegram_text_data = {
            "message": {
                "text": "Hello world"
            }
        }
        
        parser = factory.get_parser('telegram', telegram_text_data)
        assert parser is not None
        assert isinstance(parser, TelegramTextParser)
    
    def test_get_telegram_voice_parser(self, factory):
        """Test factory returns correct parser for Telegram voice messages."""
        telegram_voice_data = {
            "message": {
                "voice": {
                    "file_id": "test_file_id",
                    "duration": 10
                }
            }
        }
        
        parser = factory.get_parser('telegram', telegram_voice_data)
        assert parser is not None
        # Should return voice parser (when implemented)
    
    def test_get_email_parser(self, factory):
        """Test factory returns correct parser for email messages."""
        email_data = {"id": "test_email_id"}
        
        parser = factory.get_parser('email', email_data)
        assert parser is not None
        # Should return email parser
    
    def test_get_parser_invalid_source(self, factory):
        """Test factory returns None for invalid source."""
        invalid_data = {"message": {"text": "test"}}
        
        parser = factory.get_parser('invalid_source', invalid_data)
        assert parser is None


class TestMessageService:
    """Test the message service component."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def message_service(self, mock_db_session):
        """Create a message service instance with mock database."""
        return MessageService(mock_db_session)
    
    @pytest.fixture
    def sample_parsed_data(self):
        """Sample parsed data from parser."""
        return {
            'type': 'text',
            'content_data': {
                'source_id': '9',
                'content_type': ContentType.TEXT,
                'content_data': 'Hello, this is a test message!',
                'content_html': None,
                'source': Source.TELEGRAM,
                'timestamp': datetime.now()
            },
            'sender_data': {
                'source_id': '1021474158',
                'username': 'S_sa_f_ss_A',
                'first_name': 'saman',
                'last_name': None,
                'source': Source.TELEGRAM
            }
        }
    
    def test_process_text_message(self, message_service, sample_parsed_data):
        """Test processing a text message through the service."""
        mock_parser = Mock()
        mock_parser.parse.return_value = sample_parsed_data
        message_service.parser_factory.get_parser = Mock(return_value=mock_parser)
        
        mock_content = Mock(spec=Content)
        message_service.content_repository.create_content = Mock(return_value=mock_content)
        
        raw_data = {
            "message": {
                "message_id": 9,
                "from": {"id": 1021474158, "first_name": "saman"},
                "chat": {"id": 1021474158},
                "date": 1750635741,
                "text": "test"
            }
        }
        
        result = message_service.process_message('telegram', raw_data)
        
        message_service.parser_factory.get_parser.assert_called_once_with('telegram', raw_data)
        mock_parser.parse.assert_called_once_with(raw_data)
        
        message_service.content_repository.create_content.assert_called_once()
        call_args = message_service.content_repository.create_content.call_args[0][0]
        assert call_args.source_id == '9'
        assert call_args.content_type == ContentType.TEXT
        assert call_args.content_data == 'Hello, this is a test message!'
        assert call_args.source == Source.TELEGRAM
        
        assert result == mock_content


class TestTelegramPoller:
    """Test the Telegram poller component."""
    
    @pytest.fixture
    def mock_message_service(self):
        """Create a mock message service."""
        return Mock(spec=MessageService)
    
    @patch('config.config')
    def test_telegram_poller_initialization(self, mock_config, mock_message_service):
        """Test Telegram poller initialization."""
        mock_config.config_json = {
            "telegram_poller_sleep_time": 30
        }
        mock_config.TELEGRAM_BOT_TOKEN = "test_token"
        
        poller = TelegramPoller(mock_message_service)
        
        assert poller.bot_token is not None
        assert poller.message_service == mock_message_service
        assert poller.sleep_time == int(poller.sleep_time)
    
    @patch('requests.get')
    @patch('config.config')
    def test_get_updates(self, mock_config, mock_get, mock_message_service):
        """Test getting updates from Telegram API."""
        mock_config.config_json = {"telegram_poller_sleep_time": 30}
        mock_config.TELEGRAM_BOT_TOKEN = "test_token"
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 1,
                        "text": "test message",
                        "from": {"id": 123},
                        "chat": {"id": 123},
                        "date": 1750635741
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        poller = TelegramPoller(mock_message_service)
        updates = poller.get_updates()
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "getUpdates" in call_args[0][0]
        assert call_args[1]["params"]["timeout"] == 30
        
        # Verify result
        assert len(updates) == 1
        assert updates[0]["update_id"] == 1


class TestTelegramIntegration:
    """Integration tests for the complete Telegram text processing pipeline."""
    
    @pytest.fixture
    def db_session(self, request):
        """Create a real database session for integration tests."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from models import Base
        
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    def test_complete_telegram_text_pipeline(self, db_session):
        """Test the complete pipeline from raw data to database storage."""
        # Sample Telegram data
        raw_telegram_data = {
            "update_id": 700929842,
            "message": {
                "message_id": 9,
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
                "date": 1750635741,
                "text": "Integration test message!"
            }
        }
        
        # Create message service
        message_service = MessageService(db_session)
        
        # Process the message
        result = message_service.process_message('telegram', raw_telegram_data)
        
        # Verify result
        assert result is not None
        assert result.source_id == '9'
        assert result.content_type == ContentType.TEXT
        assert result.content_data == 'Integration test message!'
        assert result.source == Source.TELEGRAM
        
        # Verify it's in the database
        db_content = db_session.query(Content).filter_by(source_id='9').first()
        assert db_content is not None
        assert db_content.content_data == 'Integration test message!'
        assert db_content.source == Source.TELEGRAM
    
    def test_multiple_telegram_messages(self, db_session):
        """Test processing multiple Telegram messages."""
        message_service = MessageService(db_session)
        
        messages = [
            {
                "update_id": 1,
                "message": {
                    "message_id": 1,
                    "from": {"id": 123, "first_name": "user1"},
                    "chat": {"id": 123},
                    "date": 1750635741,
                    "text": "First message"
                }
            },
            {
                "update_id": 2,
                "message": {
                    "message_id": 2,
                    "from": {"id": 456, "first_name": "user2"},
                    "chat": {"id": 456},
                    "date": 1750635742,
                    "text": "Second message"
                }
            }
        ]
        
        # Process all messages
        for message in messages:
            result = message_service.process_message('telegram', message)
            assert result is not None
        
        # Verify all messages are in database
        db_contents = db_session.query(Content).all()
        assert len(db_contents) == 2
        
        # Verify content
        content_ids = [c.source_id for c in db_contents]
        assert '1' in content_ids
        assert '2' in content_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 