from sqlalchemy.orm import Session
from models.file import File, Folder
from typing import List

class FileRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_file(self, file: File):
        """Create a new file"""
        self.session.add(file)
        self.session.commit()
        self.session.refresh(file)
        return file
    
    def create_folder(self, folder: Folder):
        """Create a new folder"""
        self.session.add(folder)
        self.session.commit()
        self.session.refresh(folder)
        return folder
    
    def get_file(self, file_id: str) -> File:
        """Get a file by ID"""
        return self.session.query(File).filter(File.id == file_id).first()
    
    def get_folder(self, folder_id: str) -> Folder:
        """Get a folder by ID"""
        return self.session.query(Folder).filter(Folder.id == folder_id).first()
    
    def get_user_files(self, user_id: str) -> List[File]:
        """Get all files for a user"""
        return self.session.query(File).filter(File.user_id == user_id).all()
    
    def get_user_folders(self, user_id: str) -> List[Folder]:
        """Get all folders for a user"""
        return self.session.query(Folder).filter(Folder.user_id == user_id).all()
    
    def get_folder_files(self, folder_id: str) -> List[File]:
        """Get all files in a specific folder"""
        return self.session.query(File).filter(File.folder_id == folder_id).all()
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file"""
        try:
            file = self.session.query(File).filter(File.id == file_id).first()
            if file:
                self.session.delete(file)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete_folder(self, folder_id: str) -> bool:
        """Delete a folder"""
        try:
            folder = self.session.query(Folder).filter(Folder.id == folder_id).first()
            if folder:
                self.session.delete(folder)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            raise e