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

