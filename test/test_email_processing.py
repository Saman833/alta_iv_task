import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Content, ContentType, Source
from message_parsers.email.email_text_parser import EmailTextParser
from services.message_service import MessageService
from repository.content_repository import ContentRepository

class TestEmailProcessing:
    """Test the complete email processing flow."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def sample_gmail_data(self):
        """Sample Gmail API response with text and HTML content."""
        return {
            'historyId': '3118',
            'id': '197982890e12e974',
            'internalDate': '1750604461000',
            'labelIds': ['UNREAD', 'INBOX'],
            'snippet': 'Test for the whole Json',
            'threadId': '197982890e12e974',
            'sizeEstimate': 5662,
            'payload': {
                'partId': '',
                'mimeType': 'multipart/alternative',
                'filename': '',
                'headers': [
                    {'name': 'Delivered-To', 'value': 'saman.interview.task@gmail.com'},
                    {'name': 'From', 'value': 'saman ahmadifar <s.ahmadifar2005@gmail.com>'},
                    {'name': 'Subject', 'value': 'Test for the whole json'},
                    {'name': 'To', 'value': '"saman.interview.task@gmail.com" <saman.interview.task@gmail.com>'}
                ],
                'body': {'size': 0},
                'parts': [
                    {
                        'partId': '0',
                        'mimeType': 'text/plain',
                        'filename': '',
                        'headers': [{'name': 'Content-Type', 'value': 'text/plain; charset="UTF-8"'}],
                        'body': {'size': 25, 'data': 'VGVzdCBmb3IgdGhlIHdob2xlIEpzb24NCg=='}
                    },
                    {
                        'partId': '1',
                        'mimeType': 'text/html',
                        'filename': '',
                        'headers': [{'name': 'Content-Type', 'value': 'text/html; charset="UTF-8"'}],
                        'body': {'size': 47, 'data': 'PGRpdiBkaXI9ImF1dG8iPlRlc3QgZm9yIHRoZSB3aG9sZSBKc29uPC9kaXY-DQo='}
                    }
                ]
            }
        }
    
    def test_email_parser_extracts_content(self, sample_gmail_data):
        """Test that EmailTextParser correctly extracts text and HTML content."""
        parser = EmailTextParser()
        parsed_data = parser.parse(sample_gmail_data)
        
        # Check structure
        assert parsed_data['type'] == 'text'
        assert parsed_data['source'] == Source.EMAIL
        assert parsed_data['source_id'] == '197982890e12e974'
        
        # Check content data
        content_data = parsed_data['content_data']
        assert content_data['source_id'] == '197982890e12e974'
        assert content_data['content_type'] == ContentType.TEXT
        assert content_data['source'] == Source.EMAIL
        assert content_data['content_data'].replace('\r\n', '\n') == 'Test for the whole Json\n'  # Decoded base64
        assert content_data['content_html'].replace('\r\n', '\n') == '<div dir="auto">Test for the whole Json</div>\n'  # Decoded base64
        
        # Check timestamp conversion
        assert isinstance(content_data['timestamp'], datetime)
    
    def test_content_repository_saves_content(self, db_session):
        """Test that ContentRepository correctly saves content to database."""
        repo = ContentRepository(db_session)
        
        # Create a test content object
        content = Content(
            source_id='test123',
            content_type=ContentType.TEXT,
            content_data='Test content',
            content_html='<p>Test content</p>',
            source=Source.EMAIL,
            timestamp=datetime.now()
        )
        
        # Save to database
        saved_content = repo.create_content(content)
        
        # Verify it was saved
        assert saved_content.id is not None
        assert saved_content.source_id == 'test123'
        assert saved_content.content_data == 'Test content'
        
        # Verify it's in the database
        db_content = db_session.query(Content).filter_by(source_id='test123').first()
        assert db_content is not None
        assert db_content.content_data == 'Test content'
    
    def test_message_service_processes_email(self, db_session, sample_gmail_data):
        """Test that MessageService correctly processes email through the entire flow."""
        message_service = MessageService(db_session)
        
        # Process the email
        result = message_service.process_message('email', sample_gmail_data)
        
        # Verify result
        assert result is not None
        assert result.source_id == '197982890e12e974'
        assert result.content_type == ContentType.TEXT
        assert result.source == Source.EMAIL
        assert result.content_data.replace('\r\n', '\n') == 'Test for the whole Json\n'
        assert result.content_html.replace('\r\n', '\n') == '<div dir="auto">Test for the whole Json</div>\n'
        
        # Verify it's saved in database
        db_content = db_session.query(Content).filter_by(source_id='197982890e12e974').first()
        assert db_content is not None
        assert db_content.content_data.replace('\r\n', '\n') == 'Test for the whole Json\n'
    
    def test_parser_handles_simple_text_email(self):
        """Test parser with simple text-only email."""
        simple_email = {
            'id': 'simple123',
            'internalDate': '1750604461000',
            'snippet': 'Simple text email',
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': 'U2ltcGxlIHRleHQgZW1haWw=',
                    'size': 15
                }
            }
        }
        
        parser = EmailTextParser()
        parsed_data = parser.parse(simple_email)
        
        assert parsed_data['content_data']['content_data'] == 'Simple text email'
        assert parsed_data['content_data']['content_html'] == ''
    
    def test_parser_handles_html_only_email(self):
        """Test parser with HTML-only email."""
        html_email = {
            'id': 'html123',
            'internalDate': '1750604461000',
            'snippet': 'HTML email',
            'payload': {
                'mimeType': 'text/html',
                'body': {
                    'data': 'PGgxPkhUTUwgZW1haWw8L2gxPg==',
                    'size': 15
                }
            }
        }
        
        parser = EmailTextParser()
        parsed_data = parser.parse(html_email)
        
        assert parsed_data['content_data']['content_data'] == 'HTML email'  # Falls back to snippet
        assert parsed_data['content_data']['content_html'] == '<h1>HTML email</h1>'
    
    def test_parser_handles_missing_content(self):
        """Test parser with email that has no content parts."""
        empty_email = {
            'id': 'empty123',
            'internalDate': '1750604461000',
            'snippet': 'Empty email content',
            'payload': {
                'mimeType': 'multipart/mixed',
                'body': {'size': 0}
            }
        }
        
        parser = EmailTextParser()
        parsed_data = parser.parse(empty_email)
        
        # Should fall back to snippet
        assert parsed_data['content_data']['content_data'] == 'Empty email content'
        assert parsed_data['content_data']['content_html'] == ''
    
    def test_database_uuid_generation(self, db_session):
        """Test that Content objects get UUID IDs generated by database."""
        repo = ContentRepository(db_session)
        
        content = Content(
            source_id='uuid_test',
            content_type=ContentType.TEXT,
            content_data='Test UUID generation',
            source=Source.EMAIL,
            timestamp=datetime.now()
        )
        
        # Before saving, id should be None
        assert content.id is None
        
        # Save to database
        saved_content = repo.create_content(content)
        
        # After saving, id should be a UUID
        assert saved_content.id is not None
        assert isinstance(saved_content.id, str)
        assert len(saved_content.id) > 0 