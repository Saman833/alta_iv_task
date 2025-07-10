from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from services.file_manager_service import FileManagerService
from models.file import CreateFile, FileType
from deps import get_db
from typing import Optional, List
import uuid
from pydantic import BaseModel

router = APIRouter(prefix="/files", tags=["files"])

# Pydantic models for folder operations
class CreateFolderRequest(BaseModel):
    folder_name: str
    detail_summary: Optional[str] = None
    user_id: Optional[str] = None

class FolderResponse(BaseModel):
    id: str
    folder_name: str
    detail_summary: Optional[str] = None
    user_id: str
    folder_created_at: Optional[str] = None

@router.post("/folders", response_model=FolderResponse)
async def create_folder(
    folder_request: CreateFolderRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new folder
    """
    try:
        file_manager = FileManagerService(db)
        result = file_manager.create_folder(folder_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")

@router.get("/folders", response_model=List[FolderResponse])
async def get_user_folders(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all folders for a user
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.get_user_folders(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving folders: {str(e)}")

@router.get("/folders/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific folder by ID
    """
    try:
        file_manager = FileManagerService(db)
        folder = file_manager.get_folder(folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        return folder
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving folder: {str(e)}")

@router.get("/folders/{folder_id}/files")
async def get_folder_files(
    folder_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all files in a specific folder
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.get_folder_files(folder_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving folder files: {str(e)}")

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: str,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete a folder. Use force=True to delete folder with files.
    """
    try:
        file_manager = FileManagerService(db)
        result = file_manager.delete_folder(folder_id, force)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting folder: {str(e)}")

@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    folder_id: str = Form(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file and create a dynamic table for it
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create file object
        create_file = CreateFile(
            file_name=file.filename,
            file_content=csv_content,
            folder_id=folder_id,
            file_type=FileType.CSV,
            file_size=len(content),
            user_id=user_id or str(uuid.uuid4())
        )
        
        # Process file and create table
        file_manager = FileManagerService(db)
        result = file_manager.create_file(create_file)
        
        return {
            "message": "CSV file uploaded and table created successfully",
            "file_id": result["file"].id,
            "table_id": result["table_id"],
            "table_name": result["table_name"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")

@router.get("/table/{table_id}/data")
async def get_table_data(
    table_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Retrieve data from a dynamic table
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.get_table_data(table_id, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/table/{table_id}/search")
async def search_table_data(
    table_id: str,
    search_term: str,
    columns: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Search data in a dynamic table
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.search_table_data(table_id, search_term, columns)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/table/{table_id}")
async def delete_table(
    table_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a dynamic table
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.delete_table(table_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload-csv-from-content")
async def upload_csv_from_content(
    csv_content: str = Form(...),
    file_name: str = Form(...),
    folder_id: str = Form(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a dynamic table from CSV content (useful for testing)
    """
    try:
        # Create file object
        create_file = CreateFile(
            file_name=file_name,
            file_content=csv_content,
            folder_id=folder_id,
            file_type=FileType.CSV,
            file_size=len(csv_content.encode('utf-8')),
            user_id=user_id or str(uuid.uuid4())
        )
        
        # Process file and create table
        file_manager = FileManagerService(db)
        result = file_manager.create_file(create_file)
        
        return {
            "message": "CSV content processed and table created successfully",
            "file_id": result["file"].id,
            "table_id": result["table_id"],
            "table_name": result["table_name"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV content: {str(e)}")

@router.get("/users/{user_id}/files")
async def get_user_files(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all files for a user
    """
    try:
        file_manager = FileManagerService(db)
        return file_manager.get_user_files(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving user files: {str(e)}")

@router.get("/files/{file_id}")
async def get_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific file by ID
    """
    try:
        file_manager = FileManagerService(db)
        file = file_manager.get_file(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving file: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a file
    """
    try:
        file_manager = FileManagerService(db)
        result = file_manager.delete_file(file_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting file: {str(e)}")

