"""
Desafio API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.desafio import (
    DesafioCreate, DesafioUpdate, DesafioResponse, DesafioWithDetails,
    SubmissaoCreate, SubmissaoUpdate, SubmissaoResponse, SubmissaoWithDetails,
    VotoCreate, VotoResponse
)
from models.base import MessageResponse
from models.user import UserResponse
from services import DesafioService, SubmissaoService, VotoService
from .auth import get_current_user

router = APIRouter(prefix='/desafios', tags=['Desafios'])
desafio_service = DesafioService()
submissao_service = SubmissaoService()
voto_service = VotoService()


# === DESAFIOS ===

@router.post('', response_model=DesafioResponse, status_code=status.HTTP_201_CREATED)
async def create_desafio(
    data: DesafioCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new desafio (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await desafio_service.create_desafio(data)


@router.get('', response_model=List[DesafioResponse])
async def list_desafios(
    turma_id: Optional[UUID] = None,
    disciplina_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List desafios."""
    if turma_id:
        return await desafio_service.get_by_turma(turma_id)
    elif disciplina_id:
        return await desafio_service.get_by_disciplina(disciplina_id)
    return await desafio_service.get_all(filters={'ativo': True}, order_by='-created_at')


@router.get('/{desafio_id}', response_model=DesafioWithDetails)
async def get_desafio(
    desafio_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get desafio by ID."""
    return await desafio_service.get_for_aluno(desafio_id, current_user.id)


@router.put('/{desafio_id}', response_model=DesafioResponse)
async def update_desafio(
    desafio_id: UUID,
    data: DesafioUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update desafio."""
    desafio = await desafio_service.get_by_id(desafio_id)
    if not desafio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Desafio not found')
    if str(desafio.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await desafio_service.update_desafio(desafio_id, data)


@router.get('/{desafio_id}/ranking', response_model=List[SubmissaoWithDetails])
async def get_desafio_ranking(
    desafio_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get ranking for desafio."""
    return await desafio_service.get_ranking(desafio_id)


# === SUBMISSOES ===

@router.post('/submissoes', response_model=SubmissaoResponse, status_code=status.HTTP_201_CREATED)
async def create_submissao(
    data: SubmissaoCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a submission for a desafio."""
    if current_user.role != 'student':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Students only')
    data.aluno_id = current_user.id
    return await submissao_service.create_submissao(data)


@router.get('/submissoes/{submissao_id}', response_model=SubmissaoWithDetails)
async def get_submissao(
    submissao_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get submission by ID."""
    return await submissao_service.get_by_id(submissao_id)


@router.post('/submissoes/{submissao_id}/grade', response_model=SubmissaoResponse)
async def grade_submissao(
    submissao_id: UUID,
    points: int = Query(..., ge=0),
    feedback: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Grade a submission (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await submissao_service.grade_submissao(submissao_id, points, feedback)


@router.get('/my/submissoes', response_model=List[SubmissaoWithDetails])
async def get_my_submissoes(current_user: UserResponse = Depends(get_current_user)):
    """Get current student's submissions."""
    return await submissao_service.get_student_submissions(current_user.id)


# === VOTOS ===

@router.post('/votos', response_model=VotoResponse, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    data: VotoCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Cast a vote on a submission."""
    if current_user.role != 'student':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Students only')
    data.aluno_id = current_user.id
    return await voto_service.cast_vote(data)


@router.get('/submissoes/{submissao_id}/votos', response_model=List[VotoResponse])
async def get_submissao_votes(
    submissao_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all votes for a submission."""
    return await voto_service.get_submission_votes(submissao_id)
