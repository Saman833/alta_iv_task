from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Create synchronous engine
sql_engine = create_engine(
    config.SQL_URL, echo=False
)
SessionLocal = sessionmaker(
    bind=sql_engine, expire_on_commit=False
)

# Add async engine and session for async tests (only if needed)
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    # Convert sync URL to async URL
    if config.SQL_URL.startswith('sqlite:///'):
        async_url = config.SQL_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
    elif config.SQL_URL.startswith('postgresql://'):
        async_url = config.SQL_URL.replace('postgresql://', 'postgresql+asyncpg://')
    else:
        async_url = config.SQL_URL
    
    async_engine = create_async_engine(
        async_url, echo=False
    )
    AsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
except ImportError:
    # If async drivers are not installed, create dummy async session
    async_engine = None
    AsyncSessionLocal = None

