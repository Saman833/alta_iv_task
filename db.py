from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import config

# Sync engine (used by Alembic or any legacy sync code)
SYNC_DATABASE_URL = config.SQLALCHEMY_DATABASE_URI
engine = create_engine(SYNC_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Async engine for application runtime
ASYNC_DATABASE_URL = config.ASYNC_SQLALCHEMY_DATABASE_URI
if ASYNC_DATABASE_URL and ASYNC_DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

if ASYNC_DATABASE_URL:
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, isolation_level="REPEATABLE READ")
    AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
else:
    AsyncSessionLocal = None