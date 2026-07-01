"""
Turma API router.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from uuid import UUID
from models.turma import TurmaCreate, TurmaUpdate, TurmaResponse, TurmaWithDetails, TurmaAlunoResponse
from models.base import MessageResponse
from models.user import UserResponse
from services import TurmaService
from .auth import get_current_user

router = APIRouter(prefix='/turmas', tags=['Turmas'])
turma_service = TurmaService()


@router.post('', response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def create_turma(
    data: TurmaCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new turma (professor only)."""
    if current_user.role not in ['professor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Professors only')
    return await turma_service.create_turma(data)


@router.get('', response_model=List[TurmaWithDetails])
async def list_turmas(
    professor_id: Optional[UUID] = None,
    disciplina_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List turmas."""
    if professor_id:
        return await turma_service.get_by_professor(professor_id)
    elif disciplina_id:
        return await turma_service.get_by_disciplina(disciplina_id)
    else:
        # Return turmas based on user role
        if current_user.role == 'professor':
            return await turma_service.get_by_professor(current_user.id)
        else:
            return await turma_service.get_all_summary()


@router.post('/join/{codigo}', response_model=TurmaAlunoResponse)
async def join_turma(
    codigo: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Join turma by invite code."""
    if current_user.role != 'student':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Students only')
    return await turma_service.join_by_code(codigo, current_user.id)


@router.get('/my', response_model=List[dict])
async def get_my_turmas(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's turmas."""
    if current_user.role == 'student':
        return await turma_service.get_student_turmas(current_user.id)
    elif current_user.role == 'professor':
        return await turma_service.get_by_professor(current_user.id)
    return []


@router.get('/{turma_id}', response_model=TurmaWithDetails)
async def get_turma(
    turma_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get turma by ID with details."""
    return await turma_service.get_with_details(turma_id)


@router.put('/{turma_id}', response_model=TurmaResponse)
async def update_turma(
    turma_id: UUID,
    data: TurmaUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update turma."""
    turma = await turma_service.get_by_id(turma_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Turma not found')
    if str(turma.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await turma_service.update_turma(turma_id, data)


@router.post('/{turma_id}/enroll/{aluno_id}', response_model=TurmaAlunoResponse)
async def enroll_student(
    turma_id: UUID,
    aluno_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Enroll a student in turma."""
    turma = await turma_service.get_by_id(turma_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Turma not found')
    # Only professor or the student themselves can enroll
    if str(turma.professor_id) != str(current_user.id) and str(aluno_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await turma_service.enroll_student(turma_id, aluno_id)


@router.delete('/{turma_id}/enroll/{aluno_id}', response_model=MessageResponse)
async def unenroll_student(
    turma_id: UUID,
    aluno_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Remove student from turma."""
    turma = await turma_service.get_by_id(turma_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Turma not found')
    if str(turma.professor_id) != str(current_user.id) and str(aluno_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    success = await turma_service.unenroll_student(turma_id, aluno_id)
    return MessageResponse(message='Student removed', success=success)


@router.get('/{turma_id}/students', response_model=List[TurmaAlunoResponse])
async def get_turma_students(
    turma_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all students in turma."""
    return await turma_service.get_students(turma_id)


@router.post('/{turma_id}/regenerate-code', response_model=TurmaResponse)
async def regenerate_invite_code(
    turma_id: UUID,
    current_user: UserResponse = Depends(get_current_user)
):
    """Regenerate invite code."""
    turma = await turma_service.get_by_id(turma_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Turma not found')
    if str(turma.professor_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized')
    return await turma_service.regenerate_invite_code(turma_id)
