from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import aiofiles
import shutil
from pathlib import Path
from datetime import datetime

from app.middleware.auth import get_current_user
from app.utils.security import validate_path, get_user_directory

files_router = APIRouter()

class FileItem(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'folder'
    size: Optional[int] = None
    modified: Optional[datetime] = None

class FileTreeResponse(BaseModel):
    tree: List[FileItem]
    current_path: str

class DeleteRequest(BaseModel):
    path: str

class UploadResponse(BaseModel):
    message: str
    file: dict

ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'ppt', 'pptx'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_router.get("/tree", response_model=FileTreeResponse)
async def get_file_tree(
    path: str = Query("", description="Directory path to explore"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get file tree structure for the current user
    
    - **path**: Directory path relative to user's root directory
    """
    try:
        user_dir = get_user_directory(current_user["id"])
        full_path = validate_path(user_dir, path)
        
        # Ensure directory exists
        os.makedirs(full_path, exist_ok=True)
        
        items = []
        for item_name in os.listdir(full_path):
            item_path = os.path.join(full_path, item_name)
            relative_path = os.path.join(path, item_name) if path else item_name
            
            stat = os.stat(item_path)
            is_dir = os.path.isdir(item_path)
            
            items.append(FileItem(
                name=item_name,
                path=relative_path,
                type="folder" if is_dir else "file",
                size=None if is_dir else stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime)
            ))
        
        # Sort items: folders first, then files
        items.sort(key=lambda x: (x.type == "file", x.name.lower()))
        
        return FileTreeResponse(tree=items, current_path=path)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read directory: {str(e)}"
        )

@files_router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    path: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a file to the specified directory
    
    - **file**: File to upload
    - **path**: Directory path where file should be uploaded
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type not allowed"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds maximum limit (10MB)"
            )
        
        # Reset file position
        await file.seek(0)
        
        # Prepare file path
        user_dir = get_user_directory(current_user["id"])
        upload_dir = validate_path(user_dir, path)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = int(datetime.now().timestamp())
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return UploadResponse(
            message="File uploaded successfully",
            file={
                "name": file.filename,
                "stored_name": filename,
                "size": len(content),
                "path": os.path.join(path, filename) if path else filename
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@files_router.get("/download")
async def download_file(
    path: str = Query(..., description="File path to download"),
    current_user: dict = Depends(get_current_user)
):
    """
    Download a file
    
    - **path**: File path relative to user's root directory
    """
    try:
        user_dir = get_user_directory(current_user["id"])
        file_path = validate_path(user_dir, path)
        
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        filename = os.path.basename(path)
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )

@files_router.delete("/delete")
async def delete_file(
    delete_request: DeleteRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a file or directory
    
    - **path**: Path to file or directory to delete
    """
    try:
        user_dir = get_user_directory(current_user["id"])
        file_path = validate_path(user_dir, delete_request.path)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File or directory not found"
            )
        
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )

@files_router.post("/create-folder")
async def create_folder(
    name: str = Form(...),
    path: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new folder
    
    - **name**: Folder name
    - **path**: Parent directory path
    """
    try:
        user_dir = get_user_directory(current_user["id"])
        parent_path = validate_path(user_dir, path)
        
        folder_path = os.path.join(parent_path, name)
        
        if os.path.exists(folder_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder already exists"
            )
        
        os.makedirs(folder_path, exist_ok=True)
        
        return {"message": "Folder created successfully", "folder_name": name}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create folder: {str(e)}"
        )
