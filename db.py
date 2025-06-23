from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Create sync engine using Railway's SYNC_SQL_URI
sql_engine = create_engine(
    str(config.SQLALCHEMY_DATABASE_URI), 
    echo=False
)

SessionLocal = sessionmaker(
    bind=sql_engine, 
    expire_on_commit=False
)

print("✅ Sync engine created successfully")

# For backward compatibility, keep sync engine for Alembic
try:
    from sqlalchemy import create_engine
    sync_engine = create_engine(
        str(config.SQLALCHEMY_DATABASE_URI), 
        echo=False
    )
    SessionLocal = sessionmaker(
        bind=sync_engine, 
        expire_on_commit=False
    )
    print("✅ Sync engine created for Alembic compatibility")
except Exception as e:
    print(f"❌ Error creating sync engine: {e}")
    SessionLocal = None

