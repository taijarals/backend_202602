"""
Turma service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
import secrets
import string
from fastapi import HTTPException, status
from models.turma import TurmaCreate, TurmaUpdate, TurmaResponse, TurmaWithDetails, TurmaAlunoResponse
from repositories import TurmaRepository, TurmaAlunoRepository
from .base import BaseService


def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


class TurmaService(BaseService[TurmaResponse, TurmaRepository]):
    """Service for turma operations."""

    def __init__(self):
        super().__init__(TurmaRepository())
        self.aluno_repo = TurmaAlunoRepository()

    async def create_turma(self, data: TurmaCreate) -> TurmaResponse:
        """Create a new turma with invite code."""
        turma_data = data.model_dump()
        if not turma_data.get('codigo_convite'):
            turma_data['codigo_convite'] = generate_invite_code()

        return await self.create(turma_data)

    async def update_turma(self, id: UUID, data: TurmaUpdate) -> TurmaResponse:
        """Update turma."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Turma not found'
            )
        return result

    async def get_by_disciplina(self, disciplina_id: UUID) -> List[TurmaResponse]:
        """Get turmas by disciplina."""
        return await self.repository.get_by_disciplina(disciplina_id)

    async def get_by_professor(self, professor_id: UUID) -> List[TurmaWithDetails]:
        """Get turmas by professor with details."""
        return await self.repository.get_all_with_details({'professor_id': str(professor_id)})

    async def get_with_details(self, id: UUID) -> TurmaWithDetails:
        """Get turma with details."""
        result = await self.repository.get_with_details(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Turma not found'
            )
        return result

    async def join_by_code(self, codigo: str, aluno_id: UUID) -> TurmaAlunoResponse:
        """Join turma by invite code."""
        turma = await self.repository.get_by_invite_code(codigo)
        if not turma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Invalid invite code'
            )

        # Check if already enrolled
        enrolled = await self.aluno_repo.is_enrolled(turma.id, aluno_id)
        if enrolled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Already enrolled in this turma'
            )

        return await self.aluno_repo.enroll(turma.id, aluno_id)

    async def enroll_student(self, turma_id: UUID, aluno_id: UUID) -> TurmaAlunoResponse:
        """Enroll student in turma."""
        # Check if turma exists
        turma = await self.get_by_id(turma_id)
        if not turma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Turma not found'
            )

        # Check if already enrolled
        enrolled = await self.aluno_repo.is_enrolled(turma_id, aluno_id)
        if enrolled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Student already enrolled'
            )

        return await self.aluno_repo.enroll(turma_id, aluno_id)

    async def unenroll_student(self, turma_id: UUID, aluno_id: UUID) -> bool:
        """Remove student from turma."""
        return await self.aluno_repo.unenroll(turma_id, aluno_id)

    async def get_students(self, turma_id: UUID) -> List[TurmaAlunoResponse]:
        """Get all students in turma."""
        return await self.aluno_repo.get_students_by_turma(turma_id)

    async def get_student_turmas(self, aluno_id: UUID) -> List[Dict[str, Any]]:
        """Get all turmas for a student."""
        return await self.aluno_repo.get_turmas_by_aluno(aluno_id)

    async def regenerate_invite_code(self, turma_id: UUID) -> TurmaResponse:
        """Generate new invite code for turma."""
        new_code = generate_invite_code()
        return await self.update(turma_id, {'codigo_convite': new_code})
