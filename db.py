from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Create synchronous engine using the validated PostgreSQL URL
sql_engine = create_engine(
    str(config.SQLALCHEMY_DATABASE_URI), echo=False
)
SessionLocal = sessionmaker(
    bind=sql_engine, expire_on_commit=False
)

# Add async engine and session for async tests (only if needed)
async_engine = None
AsyncSessionLocal = None

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    
    # Build async URL from scratch using the same connection details
    database_url = str(config.SQLALCHEMY_DATABASE_URI)
    
    if database_url.startswith('sqlite:///'):
        async_url = database_url.replace('sqlite:///', 'sqlite+aiosqlite:///')
    elif database_url.startswith('postgresql://') or database_url.startswith('postgresql+psycopg2://'):
        # Extract connection details and build async URL from scratch
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        # Build async URL with asyncpg scheme
        async_url = f"postgresql+asyncpg://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}{parsed.path}"
    else:
        async_url = database_url
    
    print(f"🔧 Creating async engine with URL: {async_url}")
    
    # Try to create async engine with timeout
    async_engine = create_async_engine(
        async_url, 
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300
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
    print(f"🔧 Sync URL being used: {str(config.SQLALCHEMY_DATABASE_URI)}")

