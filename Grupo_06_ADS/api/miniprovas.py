"""
Mini Prova API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.miniprova import (
    MiniProvaCreate, MiniProvaUpdate, MiniProvaResponse,
    MiniProvaWithQuestoes, MiniProvaForStudent,
    TentativaResponse, TentativaWithDetails, RespostaCreate
)
from models.base import MessageResponse
from models.user import UserResponse
from services import MiniProvaService, TentativaService
from .auth import get_current_user

router = APIRouter(prefix='/mini-provas', tags=['Mini Provas'])
mini_prova_service = MiniProvaService()
tentativa_service = TentativaService()


# === MINI PROVAS ===

@router.post('', response_model=MiniProvaWithQuestoes, status_code=status.HTTP_201_CREATED)
async def create_mini_prova(
    data: MiniProvaCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new mini prova (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    data.professor_id = current_user.id
    return await mini_prova_service.create_mini_prova(data)


@router.get('', response_model=List[MiniProvaResponse])
async def list_mini_provas(
    turma_id: Optional[UUID] = None,
    disciplina_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List mini provas."""
    filters = {'ativa': True}
    if turma_id:
        filters['turma_id'] = str(turma_id)
    if disciplina_id:
        filters['disciplina_id'] = str(disciplina_id)

    if current_user.role == 'professor':
        return await mini_prova_service.repository.get_by_professor(current_user.id)
    return await mini_prova_service.get_all(filters=filters)


@router.get('/{prova_id}', response_model=MiniProvaWithQuestoes)
async def get_mini_prova(
    prova_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get mini prova by ID with questions (professor view)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await mini_prova_service.get_with_questoes(prova_id, include_answers=True)


@router.get('/{prova_id}/student', response_model=MiniProvaForStudent)
async def get_mini_prova_student(
    prova_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get mini prova for student (no answers shown)."""
    return await mini_prova_service.get_for_student(prova_id, current_user.id)


@router.put('/{prova_id}', response_model=MiniProvaResponse)
async def update_mini_prova(
    prova_id: UUID,
    data: MiniProvaUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update mini prova."""
    prova = await mini_prova_service.get_by_id(prova_id)
    if not prova:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Mini prova not found')
    if str(prova.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await mini_prova_service.update_mini_prova(prova_id, data)


# === TENTATIVAS ===

@router.post('/{prova_id}/start', response_model=TentativaResponse, status_code=status.HTTP_201_CREATED)
async def start_tentativa(
    prova_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Start a new test attempt."""
    return await tentativa_service.start_tentativa(prova_id, current_user.id)


@router.post('/tentativas/{tentativa_id}/answer', response_model=dict)
async def submit_answer(
    tentativa_id: UUID,
    questao_id: UUID,
    resposta: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Submit an answer during attempt."""
    return await tentativa_service.submit_answer(tentativa_id, questao_id, resposta)


@router.post('/tentativas/{tentativa_id}/finish', response_model=TentativaWithDetails)
async def finish_tentativa(
    tentativa_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Finish and grade attempt."""
    return await tentativa_service.finish_tentativa(tentativa_id)


@router.get('/tentativas/{tentativa_id}', response_model=TentativaWithDetails)
async def get_tentativa(
    tentativa_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get attempt details."""
    return await tentativa_service.get_by_id(tentativa_id)


@router.get('/my/tentativas', response_model=List[TentativaWithDetails])
async def get_my_tentativas(
    mini_prova_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current student's attempts."""
    return await tentativa_service.get_student_attempts(current_user.id, mini_prova_id)
