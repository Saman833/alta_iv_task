from sqlalchemy.orm import Session 
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from models import Content, Source

class ContentRepository:
    """
    I should change name of this model and its classses to message/message_repository if I get time later 
    """
    def __init__(self, db: Session):
        self.db = db

    def create_content(self, content: Content) -> Content:
        try : 
            self.db.add(content)
            self.db.commit()
            return content 
        except IntegrityError as e:
            self.db.rollback()
            if "UNIQUE constraint failed: content.source_id, content.source" in str(e):
                print(f"Duplicate message detected: source_id={content.source_id}, source={content.source}")
                return None
            else:
                raise e
        except Exception as e:
            self.db.rollback()
            raise e
    def update_content(self, content: Content) -> Content:
        try : 
            self.db.add(content)
            self.db.commit()
            return content 
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error updating content: {e}")
    def get_last_source_id(self, source: Source):
        """To get the last processed source_id for a given source."""
        try:
            # Use raw SQL to avoid enum validation issues
            result = self.db.execute(
                text("SELECT source_id FROM content WHERE source = :source ORDER BY source_id DESC LIMIT 1"),
                {"source": source.value}
            ).fetchone()
            
            if result:
                return int(result[0])
            else:
                return 0
        except Exception as e:
            print(f"Error getting last source_id for {source}: {e}")
            return 0
        