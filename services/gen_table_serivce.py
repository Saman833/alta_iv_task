from sqlalchemy.orm import Session
from repository.table_respository import TableRepository
from models.table import Table
import uuid
from datetime import datetime

class GenTableService:
    def __init__(self, db: Session):
        self.table_repository = TableRepository(db)

    def gen_table(self, create_file) -> Table:
        """
        Generate table metadata based on file information
        """
        table = Table(
            id=str(uuid.uuid4()),
            table_name=create_file.file_name,
            folder_id=create_file.folder_id,
            user_id=create_file.user_id if hasattr(create_file, 'user_id') else str(uuid.uuid4()),
            table_description=f"Table generated from {create_file.file_type.value} file: {create_file.file_name}",
            table_created_at=datetime.now(),
            table_updated_at=datetime.now(),
        )
        return table
    
    def save_table(self, table: Table) -> Table:
        """
        Save table metadata to database
        """
        try:
            return self.table_repository.create_table(table)
        except Exception as e:
            print(f"Error saving table: {e}")
            return None


