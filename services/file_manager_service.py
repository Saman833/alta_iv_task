from sqlalchemy.orm import Session
from services.file_service import FileService
from services.gen_table_serivce import GenTableService
from services.csv_import_service_fast import CSVImportServiceFast
from models.file import CreateFile, Folder
from fastapi import HTTPException
import uuid
from datetime import datetime

class FileManagerService:
    def __init__(self, db: Session):
        self.file_service = FileService(db)
        self.gen_table_service = GenTableService(db)
        self.csv_import_service = CSVImportServiceFast(db)

    def create_file(self, create_file: CreateFile):
        """
        Create a file and generate corresponding table based on file type
        """
        try:
            # Generate table metadata
            table = self.gen_table_service.gen_table(create_file)
            if not table:
                raise HTTPException(status_code=400, detail="Failed to generate table metadata")
            
            # Handle different file types
            if create_file.file_type.value == 'CSV':
                # Create dynamic table and import CSV data
                table_id = self.csv_import_service.create_dynamic_table(
                    table_name=create_file.file_name,
                    csv_content=create_file.file_content
                )
                
                # Update table metadata with the actual table ID
                table.id = table_id
                table.table_created_at = datetime.now()
                table.table_updated_at = datetime.now()
                
                # Save table metadata
                saved_table = self.gen_table_service.save_table(table)
                if not saved_table:
                    raise HTTPException(status_code=400, detail="Failed to save table metadata")
                
            else:
                # For non-CSV files, create JSON representation
                json_file = self.file_service.create_json_file(table.id, create_file.file_content)
                if not json_file:
                    raise HTTPException(status_code=400, detail="Failed to create JSON file")
            
            # Create file record
            file = self.file_service.create_file(create_file)
            if not file:
                raise HTTPException(status_code=400, detail="Failed to create file record")
            
            return {
                "file": file,
                "table_id": table.id,
                "table_name": table.table_name,
                "message": f"Successfully created {create_file.file_type.value} file and corresponding table"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating file: {str(e)}")

    # Folder management methods
    def create_folder(self, folder_request):
        """
        Create a new folder
        """
        try:
            folder = Folder(
                id=str(uuid.uuid4()),
                folder_name=folder_request.folder_name,
                detail_summary=folder_request.detail_summary,
                user_id=folder_request.user_id or str(uuid.uuid4())
            )
            
            created_folder = self.file_service.create_folder(folder)
            if not created_folder:
                raise HTTPException(status_code=400, detail="Failed to create folder")
            
            return created_folder.to_dict()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")

    def get_user_folders(self, user_id: str):
        """
        Get all folders for a user
        """
        try:
            folders = self.file_service.get_user_folders(user_id)
            return [folder.to_dict() for folder in folders]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving folders: {str(e)}")

    def get_folder(self, folder_id: str):
        """
        Get a specific folder by ID
        """
        try:
            folder = self.file_service.get_folder(folder_id)
            if not folder:
                return None
            return folder.to_dict()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving folder: {str(e)}")

    def get_folder_files(self, folder_id: str):
        """
        Get all files in a specific folder
        """
        try:
            files = self.file_service.get_folder_files(folder_id)
            return [file.to_dict() for file in files]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving folder files: {str(e)}")

    def delete_folder(self, folder_id: str, force: bool = False):
        """
        Delete a folder. Use force=True to delete folder with files.
        """
        try:
            # Check if folder has files
            files = self.file_service.get_folder_files(folder_id)
            if files and not force:
                raise HTTPException(
                    status_code=400, 
                    detail="Folder contains files. Use force=True to delete folder with files."
                )
            
            # Delete all files in folder if force=True
            if force and files:
                for file in files:
                    self.file_service.delete_file(file.id)
            
            # Delete the folder
            success = self.file_service.delete_folder(folder_id)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to delete folder")
            
            return {"message": "Folder deleted successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error deleting folder: {str(e)}")

    # File management methods
    def get_user_files(self, user_id: str):
        """
        Get all files for a user
        """
        try:
            files = self.file_service.get_user_files(user_id)
            return [file.to_dict() for file in files]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving user files: {str(e)}")

    def get_file(self, file_id: str):
        """
        Get a specific file by ID
        """
        try:
            file = self.file_service.get_file(file_id)
            if not file:
                return None
            return file.to_dict()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving file: {str(e)}")

    def delete_file(self, file_id: str):
        """
        Delete a file
        """
        try:
            success = self.file_service.delete_file(file_id)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to delete file")
            
            return {"message": "File deleted successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error deleting file: {str(e)}")

    def get_table_data(self, table_id: str, limit: int = 100, offset: int = 0):
        """
        Retrieve data from a dynamic table
        """
        try:
            return self.csv_import_service.get_table_data(table_id, limit, offset)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error retrieving table data: {str(e)}")

    def search_table_data(self, table_id: str, search_term: str, columns: list = None):
        """
        Search data in a dynamic table
        """
        try:
            return self.csv_import_service.search_table_data(table_id, search_term, columns)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error searching table data: {str(e)}")

    def delete_table(self, table_id: str):
        """
        Delete a dynamic table and its associated file
        """
        try:
            # Delete the table
            success = self.csv_import_service.delete_table(table_id)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to delete table")
            
            # TODO: Also delete the file record and table metadata
            # This would require additional repository methods
            
            return {"message": "Table deleted successfully"}
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error deleting table: {str(e)}")

    def create_real_table(self, table_name: str, table_content: str):
        """
        Legacy method - now handled by CSVImportService
        """
        # This method is now deprecated in favor of CSVImportService
        pass
