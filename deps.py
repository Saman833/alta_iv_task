from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base
from fastapi import Depends, Annotated
from db import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]



