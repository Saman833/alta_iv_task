from sqlalchemy.orm import Session 
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from models import Content, Source, Entity, Category
import uuid
from schemas.schemas import Public_Summary, SearchQuery
from typing import List
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

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
    def get_content_by_id(self, content_id: uuid.UUID) -> Content:
        return self.db.query(Content).filter(Content.id == content_id).first()
    def get_public_summary(self, content_id: str = None) -> list[Content]:
        """Get contents with their entities in a single query to avoid N+1 problem"""
        query = self.db.query(Content).options(
            joinedload(Content.entities)
        )
        
        if content_id:
            query = query.filter(Content.id == content_id)
        
        contents = query.all()
        return contents
    def search_contents(self, search_query: SearchQuery) -> List[Content]:
        """
        Search contents based on the provided search query conditions:
        - Filter by keywords (search in entity values)
        - Filter by category
        - Filter by source
        - Filter by date range (start_date_duration and end_date_duration)
        """
        # Start with base query including entities to avoid N+1 problem
        query = self.db.query(Content).options(
            joinedload(Content.entities)
        )
        
        # Build filter conditions
        conditions = []
        
        # Filter by keywords (search in entity values)
        if search_query.keywords and len(search_query.keywords) > 0:
            keyword_conditions = []
            for keyword in search_query.keywords:
                # Search in entity values using LIKE for partial matches
                keyword_conditions.append(
                    Content.entities.any(Entity.entity_value.ilike(f"%{keyword}%"))
                )
            if keyword_conditions:
                conditions.append(or_(*keyword_conditions))
        
        # Filter by category
        if search_query.category:
            conditions.append(Content.category == search_query.category)
        
        # Filter by source
        if search_query.source:
            conditions.append(Content.source == search_query.source)
        
        # Filter by start date (content timestamp >= start_date_duration)
        if search_query.start_date_duration:
            start_date = datetime.now() - timedelta(days=search_query.start_date_duration)
            conditions.append(Content.timestamp >= start_date)
        
        # Filter by end date (content timestamp <= end_date_duration)
        if search_query.end_date_duration:
            end_date = datetime.now() - timedelta(days=search_query.end_date_duration)
            conditions.append(Content.timestamp <= end_date)
        
        # Apply all conditions if any exist
        if conditions:
            query = query.filter(and_(*conditions))
        
        # Execute query and return results
        contents = query.all()
        return contents