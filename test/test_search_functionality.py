import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Content, ContentType, Source, Category, Entity, EntityType
from repository.content_repository import ContentRepository
from services.content_table_service import ContentTableService
from schemas.schemas import SearchQuery, ContentResponse, EntityResponse


class TestSearchFunctionality:
    """Test the search functionality with various SearchQuery parameters."""
    
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
    def sample_contents_with_entities(self, db_session):
        """Create sample content with entities for testing."""
        # Create test content
        content1 = Content(
            source_id='email_001',
            content_type=ContentType.TEXT,
            content_data='Meeting about project Alpha tomorrow at 2 PM',
            content_html='<p>Meeting about project Alpha tomorrow at 2 PM</p>',
            source=Source.EMAIL,
            category=Category.MEETING,
            subject='Project Alpha Meeting',
            timestamp=datetime.now() - timedelta(days=1)
        )
        
        content2 = Content(
            source_id='telegram_001',
            content_type=ContentType.TEXT,
            content_data='Task: Review the beta documentation by Friday',
            content_html='<p>Task: Review the beta documentation by Friday</p>',
            source=Source.TELEGRAM,
            category=Category.TASK,
            subject='Documentation Review',
            timestamp=datetime.now() - timedelta(days=3)
        )
        
        content3 = Content(
            source_id='email_002',
            content_type=ContentType.TEXT,
            content_data='Spam message about winning lottery',
            content_html='<p>Spam message about winning lottery</p>',
            source=Source.EMAIL,
            category=Category.SPAM,
            subject='You won!',
            timestamp=datetime.now() - timedelta(days=5)
        )
        
        content4 = Content(
            source_id='telegram_002',
            content_type=ContentType.TEXT,
            content_data='Information about new company policy',
            content_html='<p>Information about new company policy</p>',
            source=Source.TELEGRAM,
            category=Category.INFORMATION,
            subject='New Policy',
            timestamp=datetime.now() - timedelta(days=7)
        )
        
        # Add content to database
        db_session.add_all([content1, content2, content3, content4])
        db_session.commit()
        
        # Create entities for content1
        entity1_1 = Entity(
            content_id=content1.id,
            entity_type=EntityType.PROJECT,
            entity_value='Alpha'
        )
        entity1_2 = Entity(
            content_id=content1.id,
            entity_type=EntityType.DATE,
            entity_value='tomorrow'
        )
        
        # Create entities for content2
        entity2_1 = Entity(
            content_id=content2.id,
            entity_type=EntityType.PROJECT,
            entity_value='beta'
        )
        entity2_2 = Entity(
            content_id=content2.id,
            entity_type=EntityType.DATE,
            entity_value='Friday'
        )
        
        # Create entities for content3
        entity3_1 = Entity(
            content_id=content3.id,
            entity_type=EntityType.KEYWORD,
            entity_value='lottery'
        )
        
        # Create entities for content4
        entity4_1 = Entity(
            content_id=content4.id,
            entity_type=EntityType.KEYWORD,
            entity_value='policy'
        )
        
        # Add entities to database
        db_session.add_all([entity1_1, entity1_2, entity2_1, entity2_2, entity3_1, entity4_1])
        db_session.commit()
        
        return {
            'content1': content1,
            'content2': content2,
            'content3': content3,
            'content4': content4
        }
    
    def test_search_by_keywords(self, db_session, sample_contents_with_entities):
        """Test searching by keywords in entity values."""
        repo = ContentRepository(db_session)
        
        # Search for 'Alpha' keyword
        search_query = SearchQuery(keywords=['Alpha'])
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].source_id == 'email_001'
        assert any(entity.entity_value == 'Alpha' for entity in results[0].entities)
    
    def test_search_by_multiple_keywords(self, db_session, sample_contents_with_entities):
        """Test searching by multiple keywords."""
        repo = ContentRepository(db_session)
        
        # Search for 'Alpha' or 'beta' keywords
        search_query = SearchQuery(keywords=['Alpha', 'beta'])
        results = repo.search_contents(search_query)
        
        assert len(results) == 2
        source_ids = [content.source_id for content in results]
        assert 'email_001' in source_ids
        assert 'telegram_001' in source_ids
    
    def test_search_by_category(self, db_session, sample_contents_with_entities):
        """Test searching by category."""
        repo = ContentRepository(db_session)
        
        # Search for meeting category
        search_query = SearchQuery(category=Category.MEETING)
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].category == Category.MEETING
        assert results[0].source_id == 'email_001'
    
    def test_search_by_source(self, db_session, sample_contents_with_entities):
        """Test searching by source."""
        repo = ContentRepository(db_session)
        
        # Search for email source
        search_query = SearchQuery(source=Source.EMAIL)
        results = repo.search_contents(search_query)
        
        assert len(results) == 2
        for result in results:
            assert result.source == Source.EMAIL
    
    def test_search_by_date_range(self, db_session, sample_contents_with_entities):
        """Test searching by date range."""
        repo = ContentRepository(db_session)
        
        # Search for content from last 2 days
        search_query = SearchQuery(start_date_duration=2)
        results = repo.search_contents(search_query)
        
        # Should return content1 (1 day ago)
        assert len(results) == 1
        assert results[0].source_id == 'email_001'
    
    def test_search_by_end_date(self, db_session, sample_contents_with_entities):
        """Test searching by end date."""
        repo = ContentRepository(db_session)
        
        # Search for content older than 4 days
        search_query = SearchQuery(end_date_duration=4)
        results = repo.search_contents(search_query)
        
        # Should return content3 (5 days ago) and content4 (7 days ago)
        assert len(results) == 2
        source_ids = [content.source_id for content in results]
        assert 'email_002' in source_ids
        assert 'telegram_002' in source_ids
    
    def test_search_by_date_range_both_dates(self, db_session, sample_contents_with_entities):
        """Test searching by both start and end date."""
        repo = ContentRepository(db_session)
        
        # Search for content between 2 and 6 days ago
        search_query = SearchQuery(start_date_duration=6, end_date_duration=2)
        results = repo.search_contents(search_query)
        
        # Should return content2 (3 days ago) and content3 (5 days ago)
        assert len(results) == 2
        source_ids = [content.source_id for content in results]
        assert 'telegram_001' in source_ids
        assert 'email_002' in source_ids
    
    def test_search_combined_filters(self, db_session, sample_contents_with_entities):
        """Test searching with multiple filters combined."""
        repo = ContentRepository(db_session)
        
        # Search for email content with 'Alpha' keyword
        search_query = SearchQuery(
            keywords=['Alpha'],
            source=Source.EMAIL
        )
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].source == Source.EMAIL
        assert results[0].source_id == 'email_001'
    
    def test_search_no_filters(self, db_session, sample_contents_with_entities):
        """Test searching with no filters (should return all content)."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery()
        results = repo.search_contents(search_query)
        
        assert len(results) == 4
    
    def test_search_partial_keyword_match(self, db_session, sample_contents_with_entities):
        """Test that keyword search uses partial matching."""
        repo = ContentRepository(db_session)
        
        # Search for 'Alph' (partial match of 'Alpha')
        search_query = SearchQuery(keywords=['Alph'])
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].source_id == 'email_001'
    
    def test_search_case_insensitive(self, db_session, sample_contents_with_entities):
        """Test that keyword search is case insensitive."""
        repo = ContentRepository(db_session)
        
        # Search for 'alpha' (lowercase)
        search_query = SearchQuery(keywords=['alpha'])
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].source_id == 'email_001'
    
    def test_service_layer_conversion(self, db_session, sample_contents_with_entities):
        """Test that service layer properly converts to ContentResponse objects."""
        service = ContentTableService(db_session)
        
        search_query = SearchQuery(keywords=['Alpha'])
        results = service.search_contents(search_query)
        
        assert len(results) == 1
        assert isinstance(results[0], ContentResponse)
        assert results[0].id == sample_contents_with_entities['content1'].id
        assert len(results[0].entities) == 2
        
        # Check entity conversion
        entity_values = [entity.entity_value for entity in results[0].entities]
        assert 'Alpha' in entity_values
        assert 'tomorrow' in entity_values
    
    def test_search_empty_keywords_list(self, db_session, sample_contents_with_entities):
        """Test searching with empty keywords list."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery(keywords=[])
        results = repo.search_contents(search_query)
        
        # Should return all content (no keyword filter applied)
        assert len(results) == 4
    
    def test_search_none_keywords(self, db_session, sample_contents_with_entities):
        """Test searching with None keywords."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery(keywords=None)
        results = repo.search_contents(search_query)
        
        # Should return all content (no keyword filter applied)
        assert len(results) == 4
    
    def test_search_spam_category(self, db_session, sample_contents_with_entities):
        """Test searching for spam category."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery(category=Category.SPAM)
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].category == Category.SPAM
        assert results[0].source_id == 'email_002'
    
    def test_search_task_category(self, db_session, sample_contents_with_entities):
        """Test searching for task category."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery(category=Category.TASK)
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].category == Category.TASK
        assert results[0].source_id == 'telegram_001'
    
    def test_search_telegram_source(self, db_session, sample_contents_with_entities):
        """Test searching for telegram source."""
        repo = ContentRepository(db_session)
        
        search_query = SearchQuery(source=Source.TELEGRAM)
        results = repo.search_contents(search_query)
        
        assert len(results) == 2
        for result in results:
            assert result.source == Source.TELEGRAM
    
    def test_search_complex_combination(self, db_session, sample_contents_with_entities):
        """Test a complex search combination."""
        repo = ContentRepository(db_session)
        
        # Search for telegram content with 'beta' keyword from last 5 days
        search_query = SearchQuery(
            keywords=['beta'],
            source=Source.TELEGRAM,
            start_date_duration=5
        )
        results = repo.search_contents(search_query)
        
        assert len(results) == 1
        assert results[0].source == Source.TELEGRAM
        assert results[0].source_id == 'telegram_001'
        assert any(entity.entity_value == 'beta' for entity in results[0].entities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
