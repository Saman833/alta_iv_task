import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set a test database URL (SQLite for testing)
os.environ["SQL_URI"] = "sqlite:///./test.db"

from db import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_database_engine_creation(db_session):
    """Test if database engine can be created"""
    assert db_session is not None


def test_database_session_creation(db_session):
    """Test if database session can be created"""
    assert db_session is not None


def test_database_query_execution(db_session):
    """Test if database queries can be executed"""
    result = db_session.execute(text("SELECT 1"))
    assert result is not None


def test_database_connection_flow(db_session):
    """Test complete database connection flow"""
    try:
        assert db_session is not None
        result = db_session.execute(text("SELECT 1"))
        assert result is not None
    except Exception as e:
        pytest.fail(f"Database connection flow failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 