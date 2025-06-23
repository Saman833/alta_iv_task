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
async_engine = None
AsyncSessionLocal = None

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    # Convert sync URL to async URL
    if config.SQL_URL.startswith('sqlite:///'):
        async_url = config.SQL_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
    elif config.SQL_URL.startswith('postgresql://'):
        async_url = config.SQL_URL.replace('postgresql://', 'postgresql+asyncpg://')
    elif config.SQL_URL.startswith('postgresql+psycopg2://'):
        async_url = config.SQL_URL.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
    else:
        async_url = config.SQL_URL
    
    print(f"🔧 Creating async engine with URL: {async_url}")
    
    async_engine = create_async_engine(
        async_url, echo=False
    )
    AsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    print("✅ Async engine created successfully")
    
except ImportError as e:
    print(f"❌ Import error for async engine: {e}")
    print("⚠️  Continuing without async engine support")
except Exception as e:
    print(f"❌ Error creating async engine: {e}")
    print("⚠️  Continuing without async engine support")

