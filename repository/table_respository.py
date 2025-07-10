from sqlalchemy.orm import Session
from models.table import Table
from typing import List
class TableRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_table(self, table: Table):
        self.session.add(table)
        self.session.commit()
        return table
    
    def get_table(self, table_id: str) -> Table :
        return self.session.query(Table).filter(Table.id == table_id).first()
    
    def get_all_tables(self, user_id) -> List[Table]:
        return self.session.query(Table).filter(Table.user_id == user_id).all()
    