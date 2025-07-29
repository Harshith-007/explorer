from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from google.auth.transport import requests
from google.oauth2 import id_token
import requests as http_requests
import os

from app.middleware.auth import auth_middleware

auth_router = APIRouter()

class GoogleAuthRequest(BaseModel):
    token: str

class MicrosoftAuthRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    token: str
    user: dict

@auth_router.post("/google", response_model=AuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    """
    Authenticate user with Google OAuth token
    
    - **token**: Google OAuth ID token
    """
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            auth_request.token, 
            requests.Request(), 
            os.getenv("GOOGLE_CLIENT_ID")
        )

        # Extract user information
        user_data = {
            "id": idinfo['sub'],
            "email": idinfo['email'],
            "name": idinfo['name'],
            "picture": idinfo.get('picture', ''),
            "provider": "google"
        }

        # Create JWT token
        access_token = auth_middleware.create_access_token(data=user_data)

        return AuthResponse(
            token=access_token,
            user=user_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@auth_router.post("/microsoft", response_model=AuthResponse)
async def microsoft_auth(auth_request: MicrosoftAuthRequest):
    """
    Authenticate user with Microsoft OAuth token
    
    - **token**: Microsoft OAuth access token
    """
    try:
        # Verify Microsoft token by calling Microsoft Graph API
        headers = {"Authorization": f"Bearer {auth_request.token}"}
        response = http_requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Microsoft token"
            )

        user_info = response.json()
        
        user_data = {
            "id": user_info['id'],
            "email": user_info.get('userPrincipalName') or user_info.get('mail'),
            "name": user_info['displayName'],
            "provider": "microsoft"
        }

        # Create JWT token
        access_token = auth_middleware.create_access_token(data=user_data)

        return AuthResponse(
            token=access_token,
            user=user_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Microsoft authentication failed: {str(e)}"
        )
