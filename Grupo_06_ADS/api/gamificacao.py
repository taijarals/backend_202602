"""
Gamification API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.gamificacao import (
    MedalhaCreate, MedalhaResponse, ConquistaResponse,
    NivelResponse, UserGamificationStats, LeaderboardEntry
)
from models.user import UserResponse
from services import GamificacaoService, MedalhaService
from .auth import get_current_user

router = APIRouter(prefix='/gamificacao', tags=['Gamificacao'])
gamificacao_service = GamificacaoService()
medalha_service = MedalhaService()


# === LEADERBOARD ===

@router.get('/leaderboard', response_model=List[LeaderboardEntry])
async def get_leaderboard(
    turma_id: Optional[UUID] = None,
    limit: int = Query(100, ge=1, le=500),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get leaderboard (global or turma)."""
    return await gamificacao_service.get_leaderboard(turma_id, limit)


# === USER STATS ===

@router.get('/stats', response_model=UserGamificationStats)
async def get_my_stats(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's gamification stats."""
    return await gamificacao_service.get_user_stats(current_user.id)


@router.get('/stats/{user_id}', response_model=UserGamificationStats)
async def get_user_stats(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's gamification stats."""
    return await gamificacao_service.get_user_stats(user_id)


# === LEVELS ===

@router.get('/levels', response_model=List[NivelResponse])
async def get_levels(current_user: UserResponse = Depends(get_current_user)):
    """Get all levels."""
    return await gamificacao_service.get_levels()


# === MEDALHAS ===

@router.get('/medalhas', response_model=List[MedalhaResponse])
async def list_medalhas(current_user: UserResponse = Depends(get_current_user)):
    """Get all active medalhas."""
    return await gamificacao_service.get_medalhas()


@router.post('/medalhas', response_model=MedalhaResponse, status_code=status.HTTP_201_CREATED)
async def create_medalha(
    data: MedalhaCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new medalha (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin only')
    return await medalha_service.create_medalha(data)


# === CONQUISTAS ===

@router.get('/conquistas', response_model=List[ConquistaResponse])
async def get_my_conquistas(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's conquistas."""
    return await gamificacao_service.get_aluno_conquistas(current_user.id)


@router.get('/conquistas/{user_id}', response_model=List[ConquistaResponse])
async def get_user_conquistas(
    user_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get user's conquistas."""
    return await gamificacao_service.get_aluno_conquistas(user_id)
