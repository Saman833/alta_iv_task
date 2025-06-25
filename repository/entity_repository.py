from sqlalchemy.orm import Session
from models import Entity

class EntityRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_entities(self, entities: list[Entity]):
        try:
            self.db.add_all(entities)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating entities: {e}")
    
    def create_entity(self, entity: Entity) -> Entity:
        """Create a single entity"""
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating entity: {e}")
        
        
        