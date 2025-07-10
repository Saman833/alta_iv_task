from sqlalchemy.orm import Session
from repository.file_repository import FileRepository
from models.file import CreateFile, File, Folder
import uuid

class FileService:
    def __init__(self, db: Session):
        self.file_repository = FileRepository(db)

    def create_file(self, create_file: CreateFile):
        """Create a new file record"""
        file_id = str(uuid.uuid4()) 
        file = File(
            id=file_id,
            file_name=create_file.file_name,
            detail_summary=f"File created from {create_file.file_type.value}",
            folder_id=create_file.folder_id,
            file_type=create_file.file_type,
            file_size=create_file.file_size,
            user_id=create_file.user_id or str(uuid.uuid4())
        )
        return self.file_repository.create_file(file)
    
    def create_json_file(self, table_name: str, table_content: str):
        """Create a JSON representation of table content"""
        # This method can be implemented to store JSON files if needed
        # For now, it's a placeholder
        pass 
    
    def get_file(self, file_id: str):
        """Get a file by ID"""
        return self.file_repository.get_file(file_id)
    
    def get_user_files(self, user_id: str):
        """Get all files for a user"""
        return self.file_repository.get_user_files(user_id)
    
    def get_folder_files(self, folder_id: str):
        """Get all files in a specific folder"""
        return self.file_repository.get_folder_files(folder_id)
    
    def delete_file(self, file_id: str):
        """Delete a file"""
        return self.file_repository.delete_file(file_id)
    
    # Folder management methods
    def create_folder(self, folder: Folder):
        """Create a new folder"""
        return self.file_repository.create_folder(folder)
    
    def get_folder(self, folder_id: str):
        """Get a folder by ID"""
        return self.file_repository.get_folder(folder_id)
    
    def get_user_folders(self, user_id: str):
        """Get all folders for a user"""
        return self.file_repository.get_user_folders(user_id)
    
    def delete_folder(self, folder_id: str):
        """Delete a folder"""
        return self.file_repository.delete_folder(folder_id)