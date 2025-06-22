from sqlalchemy.orm import Session
from models import Content

class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_content(self, content: Content) -> Content:
        self.db.add(content)
        self.db.commit()
        return content 