"""
User API router.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from models.user import UserUpdate, UserResponse, UserStats
from models.base import PaginatedResponse, MessageResponse
from services import UserService
from .auth import get_current_user

router = APIRouter(prefix='/users', tags=['Users'])
user_service = UserService()


@router.get('', response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List all users (paginated)."""
    filters = {}
    if role:
        filters['role'] = role
    result = await user_service.get_all(filters=filters, page=page, page_size=page_size)
    return PaginatedResponse(**result)


@router.get('/professors', response_model=List[UserResponse])
async def list_professors(current_user: UserResponse = Depends(get_current_user)):
    """List all professors."""
    return await user_service.get_professors()


@router.get('/students', response_model=List[UserResponse])
async def list_students(current_user: UserResponse = Depends(get_current_user)):
    """List all students."""
    return await user_service.get_students()


@router.get('/ranking', response_model=List[UserResponse])
async def get_ranking(
    limit: int = Query(10, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user ranking by points."""
    return await user_service.get_ranking(limit)


@router.get('/search', response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2),
    role: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Search users by name or email."""
    return await user_service.search_users(q, role)


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user by ID."""
    user = await user_service.get_by_id(user_id)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user profile."""
    # Only allow updating own profile or admin
    if str(user_id) != str(current_user.id) and current_user.role != 'admin':
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await user_service.update_profile(user_id, data)


@router.get('/{user_id}/stats', response_model=UserStats)
async def get_user_stats(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user statistics."""
    return await user_service.get_stats(user_id)


@router.delete('/{user_id}', response_model=MessageResponse)
async def delete_user(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete user (admin only)."""
    if current_user.role != 'admin':
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin only')
    success = await user_service.delete(user_id)
    return MessageResponse(message='User deleted', success=success)
