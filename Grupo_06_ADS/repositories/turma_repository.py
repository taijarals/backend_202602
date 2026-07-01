"""
Turma repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from models.turma import TurmaCreate, TurmaUpdate, TurmaResponse, TurmaWithDetails, TurmaAlunoResponse
from .base import BaseRepository


class TurmaRepository(BaseRepository[TurmaResponse]):
    """Repository for turma operations."""

    def __init__(self):
        super().__init__('turmas', TurmaResponse)

    async def get_by_disciplina(self, disciplina_id: UUID) -> List[TurmaResponse]:
        """Get turmas by disciplina."""
        return await self.get_all(filters={'disciplina_id': str(disciplina_id)})

    async def get_by_professor(self, professor_id: UUID) -> List[TurmaResponse]:
        """Get turmas by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)})

    async def get_with_details(self, id: UUID) -> Optional[TurmaWithDetails]:
        """Get turma with details."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,disciplinas(nome),profiles!professor_id(nome)'
        )
        if result:
            data = result
            data['disciplina_nome'] = result.get('disciplinas', {}).get('nome') if result.get('disciplinas') else None
            data['professor_nome'] = result.get('profiles', {}).get('nome') if result.get('profiles') else None
            return TurmaWithDetails.model_validate(data)
        return None

    async def get_all_with_details(self, filters: Optional[Dict[str, Any]] = None) -> List[TurmaWithDetails]:
        """Get all turmas with details."""
        results = await self.db.get_all(
            self.table,
            filters=filters,
            order_by='-created_at',
            select='*,disciplinas(nome),profiles!professor_id(nome)'
        )

        items = []
        for r in results:
            r['disciplina_nome'] = r.get('disciplinas', {}).get('nome') if r.get('disciplinas') else None
            r['professor_nome'] = r.get('profiles', {}).get('nome') if r.get('profiles') else None
            items.append(TurmaWithDetails.model_validate(r))
        return items

    async def get_by_invite_code(self, codigo: str) -> Optional[TurmaResponse]:
        """Get turma by invite code."""
        return await self.get_one({'codigo_convite': codigo})

    async def get_active(self) -> List[TurmaResponse]:
        """Get all active turmas."""
        return await self.get_all(filters={'ativa': True})


class TurmaAlunoRepository(BaseRepository[TurmaAlunoResponse]):
    """Repository for turma-aluno enrollment operations."""

    def __init__(self):
        super().__init__('turma_alunos', TurmaAlunoResponse)

    async def enroll(self, turma_id: UUID, aluno_id: UUID) -> TurmaAlunoResponse:
        """Enroll student in turma."""
        return await self.create({
            'turma_id': str(turma_id),
            'aluno_id': str(aluno_id)
        })

    async def unenroll(self, turma_id: UUID, aluno_id: UUID) -> bool:
        """Unenroll student from turma."""
        results = await self.get_all(filters={'turma_id': str(turma_id), 'aluno_id': str(aluno_id)})
        if results:
            return await self.delete(results[0].id)
        return False

    async def get_students_by_turma(self, turma_id: UUID) -> List[TurmaAlunoResponse]:
        """Get all students in a turma."""
        results = await self.db.get_all(
            self.table,
            filters={'turma_id': str(turma_id)},
            select='*,profiles!aluno_id(nome,email,pontuacao_total)'
        )
        items = []
        for r in results:
            r['aluno_nome'] = r.get('profiles', {}).get('nome') if r.get('profiles') else None
            r['aluno_email'] = r.get('profiles', {}).get('email') if r.get('profiles') else None
            items.append(TurmaAlunoResponse.model_validate(r))
        return items

    async def get_turmas_by_aluno(self, aluno_id: UUID) -> List[Dict[str, Any]]:
        """Get all turmas for a student."""
        results = await self.db.get_all(
            self.table,
            filters={'aluno_id': str(aluno_id)},
            select='*,turmas(*,disciplinas(nome),profiles!professor_id(nome))'
        )
        return results

    async def is_enrolled(self, turma_id: UUID, aluno_id: UUID) -> bool:
        """Check if student is enrolled in turma."""
        result = await self.get_one({'turma_id': str(turma_id), 'aluno_id': str(aluno_id)})
        return result is not None
