import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Set a test database URL (SQLite for testing)
os.environ["SQL_URL"] = "sqlite+aiosqlite:///./test.db"

from db import sql_engine, AsyncSessionLocal

@pytest.mark.asyncio
async def test_database_engine_creation():
    """Test if database engine can be created"""
    assert sql_engine is not None

@pytest.mark.asyncio
async def test_database_session_creation():
    """Test if database session can be created"""
    async with AsyncSessionLocal() as session:
        assert isinstance(session, AsyncSession)

@pytest.mark.asyncio
async def test_database_query_execution():
    """Test if database queries can be executed"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        assert result is not None

@pytest.mark.asyncio
async def test_database_connection_flow():
    """Test complete database connection flow"""
    try:
         
        assert sql_engine is not None
        
         
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            assert result is not None
        
    except Exception as e:
        pytest.fail(f"Database connection flow failed: {e}")
    return True

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 