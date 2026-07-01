"""
Desafio repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from models.desafio import (
    DesafioCreate, DesafioUpdate, DesafioResponse, DesafioWithDetails,
    SubmissaoCreate, SubmissaoUpdate, SubmissaoResponse, SubmissaoWithDetails,
    VotoCreate, VotoResponse, RankingEntry
)
from .base import BaseRepository


class DesafioRepository(BaseRepository[DesafioResponse]):
    """Repository for desafio operations."""

    def __init__(self):
        super().__init__('desafios', DesafioResponse)

    async def get_by_professor(self, professor_id: UUID) -> List[DesafioResponse]:
        """Get desafios by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)})

    async def get_by_turma(self, turma_id: UUID, active_only: bool = True) -> List[DesafioResponse]:
        """Get desafios for a turma."""
        filters = {'turma_id': str(turma_id)}
        if active_only:
            filters['ativo'] = True
        return await self.get_all(filters=filters, order_by='-created_at')

    async def get_by_disciplina(self, disciplina_id: UUID) -> List[DesafioResponse]:
        """Get desafios for a disciplina."""
        return await self.get_all(filters={'disciplina_id': str(disciplina_id)})

    async def get_with_details(self, id: UUID, aluno_id: Optional[UUID] = None) -> Optional[DesafioWithDetails]:
        """Get desafio with details."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,disciplinas(nome),turmas(nome),profiles!professor_id(nome)'
        )
        if result:
            data = result
            data['disciplina_nome'] = result.get('disciplinas', {}).get('nome') if result.get('disciplinas') else None
            data['turma_nome'] = result.get('turmas', {}).get('nome') if result.get('turmas') else None
            data['professor_nome'] = result.get('profiles', {}).get('nome') if result.get('profiles') else None
            return DesafioWithDetails.model_validate(data)
        return None

    async def get_active(self) -> List[DesafioResponse]:
        """Get all active desafios."""
        return await self.get_all(filters={'ativo': True}, order_by='-created_at')

    async def get_by_difficulty(self, difficulty: str) -> List[DesafioResponse]:
        """Get desafios by difficulty."""
        return await self.get_all(filters={'dificuldade': difficulty, 'ativo': True})


class SubmissaoRepository(BaseRepository[SubmissaoResponse]):
    """Repository for submissao operations."""

    def __init__(self):
        super().__init__('submissoes', SubmissaoResponse)

    async def get_by_desafio(self, desafio_id: UUID) -> List[SubmissaoResponse]:
        """Get submissoes for a desafio."""
        return await self.get_all(filters={'desafio_id': str(desafio_id)}, order_by='-votos')

    async def get_by_aluno(self, aluno_id: UUID) -> List[SubmissaoResponse]:
        """Get submissoes by aluno."""
        return await self.get_all(filters={'aluno_id': str(aluno_id)}, order_by='-created_at')

    async def get_aluno_submissao(self, desafio_id: UUID, aluno_id: UUID) -> Optional[SubmissaoResponse]:
        """Get student's submission for a desafio."""
        return await self.get_one({'desafio_id': str(desafio_id), 'aluno_id': str(aluno_id)})

    async def get_with_details(self, id: UUID) -> Optional[SubmissaoWithDetails]:
        """Get submissao with details."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,desafios(titulo),profiles!aluno_id(nome,email)'
        )
        if result:
            data = result
            data['desafio_titulo'] = result.get('desafios', {}).get('titulo') if result.get('desafios') else None
            data['aluno_nome'] = result.get('profiles', {}).get('nome') if result.get('profiles') else None
            data['aluno_email'] = result.get('profiles', {}).get('email') if result.get('profiles') else None
            return SubmissaoWithDetails.model_validate(data)
        return None

    async def update_points(self, id: UUID, points: int, feedback: Optional[str] = None) -> Optional[SubmissaoResponse]:
        """Update submission with points and feedback."""
        data = {'pontos_obtidos': points, 'status': 'nota_atribuida'}
        if feedback:
            data['feedback_professor'] = feedback
        return await self.update(id, data)


class VotoRepository(BaseRepository[VotoResponse]):
    """Repository for voto operations."""

    def __init__(self):
        super().__init__('votos', VotoResponse)

    async def get_by_submissao(self, submissao_id: UUID) -> List[VotoResponse]:
        """Get votos for a submissao."""
        return await self.get_all(filters={'submissao_id': str(submissao_id)})

    async def has_voted(self, submissao_id: UUID, aluno_id: UUID) -> bool:
        """Check if student has voted for submissao."""
        result = await self.get_one({'submissao_id': str(submissao_id), 'aluno_id': str(aluno_id)})
        return result is not None

    async def get_average_score(self, submissao_id: UUID) -> float:
        """Get average vote score for submissao."""
        votos = await self.get_by_submissao(submissao_id)
        if not votos:
            return 0.0
        total = sum(v.pontuacao for v in votos)
        return total / len(votos)
