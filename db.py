from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
import os
load_dotenv()

SQL_URI = os.getenv("SQL_URI", "sqlite:///./test.db")

engine = create_engine(SQL_URI, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)