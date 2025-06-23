from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Create synchronous engine
sql_engine = create_engine(
    config.SQL_URI, echo=False
)
SessionLocal = sessionmaker(
    bind=sql_engine, expire_on_commit=False
)

# Add async engine and session for async tests (only if needed)
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    # Convert sync URI to async URI for SQLite
    if config.SQL_URI.startswith('sqlite:///'):
        async_uri = config.SQL_URI.replace('sqlite:///', 'sqlite+aiosqlite:///')
    else:
        async_uri = config.SQL_URI
    
    async_engine = create_async_engine(
        async_uri, echo=False
    )
    AsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
except ImportError:
    # If aiosqlite is not installed, create dummy async session
    async_engine = None
    AsyncSessionLocal = None

