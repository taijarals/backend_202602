"""
Enquete API router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.enquete import (
    EnqueteCreate, EnqueteUpdate, EnqueteResponse,
    EnqueteWithOpcoes, VotoEnqueteResponse, EnqueteStats
)
from models.base import MessageResponse
from models.user import UserResponse
from services import EnqueteService
from .auth import get_current_user

router = APIRouter(prefix='/enquetes', tags=['Enquetes'])
enquete_service = EnqueteService()


@router.post('', response_model=EnqueteWithOpcoes, status_code=status.HTTP_201_CREATED)
async def create_enquete(
    data: EnqueteCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new enquete (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    data.professor_id = current_user.id
    return await enquete_service.create_enquete(data)


@router.get('', response_model=List[EnqueteResponse])
async def list_enquetes(
    turma_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List enquetes."""
    if current_user.role == 'professor':
        return await enquete_service.repository.get_by_professor(current_user.id)
    elif turma_id:
        return await enquete_service.get_by_turma(turma_id)
    return await enquete_service.get_all()


@router.get('/active', response_model=List[EnqueteWithOpcoes])
async def get_active_enquetes(current_user: UserResponse = Depends(get_current_user)):
    """Get all active enquetes."""
    return await enquete_service.get_active()


@router.get('/{enquete_id}', response_model=EnqueteWithOpcoes)
async def get_enquete(
    enquete_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get enquete by ID with options and results."""
    return await enquete_service.get_with_opcoes(enquete_id)


@router.put('/{enquete_id}', response_model=EnqueteResponse)
async def update_enquete(
    enquete_id: UUID,
    data: EnqueteUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update enquete."""
    enquete = await enquete_service.get_by_id(enquete_id)
    if not enquete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Enquete not found')
    if str(enquete.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await enquete_service.update_enquete(enquete_id, data)


@router.post('/{enquete_id}/vote', response_model=VotoEnqueteResponse)
async def cast_vote(
    enquete_id: UUID,
    opcao_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Cast a vote in enquete."""
    if current_user.role != 'student':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Students only')
    return await enquete_service.cast_vote(enquete_id, opcao_id, current_user.id)


@router.get('/{enquete_id}/stats', response_model=EnqueteStats)
async def get_enquete_stats(
    enquete_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get enquete statistics."""
    return await enquete_service.get_stats(enquete_id)


@router.post('/{enquete_id}/close', response_model=EnqueteResponse)
async def close_enquete(
    enquete_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Close an enquete (professor only)."""
    enquete = await enquete_service.get_by_id(enquete_id)
    if not enquete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Enquete not found')
    if str(enquete.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await enquete_service.close_enquete(enquete_id)


@router.delete('/{enquete_id}', response_model=MessageResponse)
async def delete_enquete(
    enquete_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete enquete (professor only)."""
    enquete = await enquete_service.get_by_id(enquete_id)
    if not enquete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Enquete not found')
    if str(enquete.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    success = await enquete_service.delete(enquete_id)
    return MessageResponse(message='Enquete deleted', success=success)
