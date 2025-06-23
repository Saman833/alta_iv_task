from sqlalchemy.orm import Session 
from models import Content, Source

class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_content(self, content: Content) -> Content:
        try : 
            self.db.add(content)
            self.db.commit()
            return content 
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_last_source_id(self, source: Source):
        """Get the last processed source_id for a given source."""
        try:
            last_content = self.db.query(Content)\
                .filter(Content.source == source)\
                .order_by(Content.source_id.desc())\
                .first()
            
            if last_content:
                return int(last_content.source_id)
            else:
                return 0
        except Exception as e:
            print(f"Error getting last source_id for {source}: {e}")
            return 0
        