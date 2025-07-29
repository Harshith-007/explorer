import os
from pathlib import Path
from fastapi import HTTPException, status

def get_user_directory(user_id: str) -> str:
    """Get and create user-specific directory"""
    base_dir = os.path.join(os.getcwd(), "uploads")
    user_dir = os.path.join(base_dir, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def validate_path(base_path: str, user_path: str) -> str:
    """Validate and resolve path to prevent directory traversal attacks"""
    if not user_path:
        return base_path
    
    # Normalize the path to prevent directory traversal
    user_path = user_path.replace('..', '').replace('//', '/').strip('/')
    
    # Combine base path with user path
    full_path = os.path.join(base_path, user_path)
    
    # Resolve the path to get the absolute path
    resolved_path = os.path.abspath(full_path)
    base_abs_path = os.path.abspath(base_path)
    
    # Ensure the resolved path is within the base directory
    if not resolved_path.startswith(base_abs_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Invalid path"
        )
    
    return resolved_path

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    from app.middleware.auth import auth_middleware
    return auth_middleware.verify_token(token)