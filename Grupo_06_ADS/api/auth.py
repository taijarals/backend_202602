"""
Authentication API router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from services import AuthService

router = APIRouter(prefix='/auth', tags=['Authentication'])
security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = await auth_service.validate_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload'
        )
    user = await auth_service.get_current_user(UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
    return user


@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    return await auth_service.register(user_data)


@router.post('/login', response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user."""
    return await auth_service.login(credentials)


@router.post('/logout')
async def logout():
    """Logout user."""
    success = await auth_service.logout()
    return {'success': success, 'message': 'Logged out successfully'}


@router.post('/refresh')
async def refresh_token():
    """Refresh authentication token."""
    result = await auth_service.refresh_session()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Failed to refresh session'
        )
    return result


@router.get('/me', response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile."""
    return current_user
