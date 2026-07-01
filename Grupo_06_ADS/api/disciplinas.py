"""
Disciplina API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.disciplina import DisciplinaCreate, DisciplinaUpdate, DisciplinaResponse, DisciplinaWithDetails
from models.base import PaginatedResponse, MessageResponse
from models.user import UserResponse
from services import DisciplinaService
from .auth import get_current_user

router = APIRouter(prefix='/disciplinas', tags=['Disciplinas'])
disciplina_service = DisciplinaService()


@router.post('', response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def create_disciplina(
    data: DisciplinaCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new disciplina (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await disciplina_service.create_disciplina(data)


@router.get('', response_model=List[DisciplinaWithDetails])
async def list_disciplinas(
    professor_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List all disciplinas."""
    if professor_id:
        return await disciplina_service.get_by_professor(professor_id)
    return await disciplina_service.get_all_summary()


@router.get('/active', response_model=List[DisciplinaResponse])
async def list_active_disciplinas(current_user: UserResponse = Depends(get_current_user)):
    """List all active disciplinas."""
    return await disciplina_service.get_active()


@router.get('/{disciplina_id}', response_model=DisciplinaWithDetails)
async def get_disciplina(
    disciplina_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get disciplina by ID with details."""
    return await disciplina_service.get_with_details(disciplina_id)


@router.put('/{disciplina_id}', response_model=DisciplinaResponse)
async def update_disciplina(
    disciplina_id: UUID,
    data: DisciplinaUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update disciplina."""
    disciplina = await disciplina_service.get_by_id(disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Disciplina not found')
    # Check ownership
    if str(disciplina.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await disciplina_service.update_disciplina(disciplina_id, data)


@router.delete('/{disciplina_id}', response_model=MessageResponse)
async def deactivate_disciplina(
    disciplina_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Deactivate disciplina."""
    disciplina = await disciplina_service.get_by_id(disciplina_id)
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Disciplina not found')
    if str(disciplina.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    await disciplina_service.deactivate(disciplina_id)
    return MessageResponse(message='Disciplina deactivated')
