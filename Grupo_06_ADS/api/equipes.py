"""
Equipe API router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from models.equipe import (
    EquipeCreate, EquipeUpdate, EquipeResponse,
    EquipeWithDetails, EquipeMembroResponse,
    TeamFormationRequest, TeamFormationResult
)
from models.base import MessageResponse
from models.user import UserResponse
from services import EquipeService
from .auth import get_current_user

router = APIRouter(prefix='/equipes', tags=['Equipes'])
equipe_service = EquipeService()


@router.post('', response_model=EquipeWithDetails, status_code=status.HTTP_201_CREATED)
async def create_equipe(
    data: EquipeCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new equipe."""
    return await equipe_service.create_equipe(data)


@router.get('/turma/{turma_id}', response_model=List[EquipeWithDetails])
async def list_turma_equipes(
    turma_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all equipes for a turma."""
    return await equipe_service.get_by_turma(turma_id)


@router.get('/my', response_model=Optional[EquipeWithDetails])
async def get_my_equipe(
    turma_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user's equipe for a turma."""
    return await equipe_service.get_student_equipe(current_user.id, turma_id)


@router.get('/{equipe_id}', response_model=EquipeWithDetails)
async def get_equipe(
    equipe_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get equipe by ID with members."""
    return await equipe_service.get_with_members(equipe_id)


@router.put('/{equipe_id}', response_model=EquipeResponse)
async def update_equipe(
    equipe_id: UUID,
    data: EquipeUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update equipe."""
    equipe = await equipe_service.get_by_id(equipe_id)
    if not equipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Equipe not found')
    # Check if user is team leader or admin
    membro = await equipe_service.membro_repo.get_aluno_equipe(current_user.id)
    if (not membro or membro.papel != 'lider') and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await equipe_service.update(equipe_id, data.model_dump(exclude_unset=True))


@router.post('/{equipe_id}/members', response_model=EquipeMembroResponse)
async def add_member(
    equipe_id: UUID,
    aluno_id: UUID,
    papel: str = 'membro',
    current_user: UserResponse = Depends(get_current_user)
):
    """Add member to equipe."""
    return await equipe_service.add_member(equipe_id, aluno_id, papel)


@router.delete('/{equipe_id}/members/{aluno_id}', response_model=MessageResponse)
async def remove_member(
    equipe_id: UUID,
    aluno_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Remove member from equipe."""
    success = await equipe_service.remove_member(equipe_id, aluno_id)
    return MessageResponse(message='Member removed', success=success)


@router.post('/auto-create', response_model=TeamFormationResult, status_code=status.HTTP_201_CREATED)
async def auto_form_teams(
    data: TeamFormationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Automatically form teams for a turma (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await equipe_service.auto_form_teams(data)


@router.post('/{equipe_id}/points', response_model=EquipeResponse)
async def add_equipe_points(
    equipe_id: UUID,
    points: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add points to equipe (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await equipe_service.update_equipe_points(equipe_id, points)
