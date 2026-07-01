"""
Missao API router.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from uuid import UUID
from models.missao import (
    MissaoCreate, MissaoUpdate, MissaoResponse,
    MissaoWithEtapas, MissaoProgress, UserMissionStats
)
from models.base import MessageResponse
from models.user import UserResponse
from services import MissaoService, MissaoEtapaService
from .auth import get_current_user

router = APIRouter(prefix='/missoes', tags=['Missoes'])
missao_service = MissaoService()
etapa_service = MissaoEtapaService()


@router.post('', response_model=MissaoWithEtapas, status_code=status.HTTP_201_CREATED)
async def create_missao(
    data: MissaoCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new missao (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    data.professor_id = current_user.id
    return await missao_service.create_missao(data)


@router.get('', response_model=List[MissaoResponse])
async def list_missoes(
    turma_id: Optional[UUID] = None,
    disciplina_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List missoes."""
    if turma_id:
        return await missao_service.get_by_turma(turma_id)
    elif disciplina_id:
        return await missao_service.get_by_disciplina(disciplina_id)
    elif current_user.role == 'professor':
        return await missao_service.repository.get_by_professor(current_user.id)
    return await missao_service.get_all(filters={'ativa': True})


@router.get('/available', response_model=List[MissaoProgress])
async def get_available_missoes(current_user: UserResponse = Depends(get_current_user)):
    """Get available missoes with progress for current student."""
    return await missao_service.get_available_for_aluno(current_user.id)


@router.get('/{missao_id}', response_model=MissaoWithEtapas)
async def get_missao(
    missao_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get missao by ID with etapas."""
    return await missao_service.get_with_etapas(missao_id)


@router.get('/{missao_id}/progress', response_model=MissaoProgress)
async def get_missao_progress(
    missao_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get missao with student's progress."""
    return await missao_service.get_for_aluno(missao_id, current_user.id)


@router.put('/{missao_id}', response_model=MissaoResponse)
async def update_missao(
    missao_id: UUID,
    data: MissaoUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update missao."""
    missao = await missao_service.get_by_id(missao_id)
    if not missao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Missao not found')
    if str(missao.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await missao_service.update_missao(missao_id, data)


@router.post('/{missao_id}/etapas/{etapa_id}/start')
async def start_etapa(
    missao_id: UUID,
    etapa_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Start working on an etapa."""
    return await missao_service.start_etapa(missao_id, etapa_id, current_user.id)


@router.post('/{missao_id}/etapas/{etapa_id}/complete')
async def complete_etapa(
    missao_id: UUID,
    etapa_id: UUID,
    points: Optional[int] = Query(None),
    current_user: UserResponse = Depends(get_current_user)
):
    """Complete an etapa."""
    return await missao_service.complete_etapa(missao_id, etapa_id, current_user.id, points)


@router.get('/stats/my', response_model=UserMissionStats)
async def get_my_mission_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's mission stats."""
    return await missao_service.get_student_stats(current_user.id)


@router.get('/stats/{user_id}', response_model=UserMissionStats)
async def get_user_mission_stats(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's mission stats."""
    return await missao_service.get_student_stats(user_id)
