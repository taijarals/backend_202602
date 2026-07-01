"""
Desafio service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from models.desafio import (
    DesafioCreate, DesafioUpdate, DesafioResponse, DesafioWithDetails,
    SubmissaoCreate, SubmissaoUpdate, SubmissaoResponse, SubmissaoWithDetails,
    VotoCreate, VotoResponse, RankingEntry
)
from repositories import DesafioRepository, SubmissaoRepository, VotoRepository, PontuacaoRepository
from .base import BaseService


class DesafioService(BaseService[DesafioResponse, DesafioRepository]):
    """Service for desafio operations."""

    def __init__(self):
        super().__init__(DesafioRepository())
        self.submissao_repo = SubmissaoRepository()
        self.pontuacao_repo = PontuacaoRepository()

    async def create_desafio(self, data: DesafioCreate) -> DesafioResponse:
        """Create a new desafio."""
        return await self.create(data.model_dump())

    async def update_desafio(self, id: UUID, data: DesafioUpdate) -> DesafioResponse:
        """Update desafio."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Desafio not found'
            )
        return result

    async def get_by_turma(self, turma_id: UUID) -> List[DesafioResponse]:
        """Get desafios for a turma."""
        return await self.repository.get_by_turma(turma_id)

    async def get_for_aluno(self, desafio_id: UUID, aluno_id: UUID) -> DesafioWithDetails:
        """Get desafio with student's status."""
        result = await self.repository.get_with_details(desafio_id, aluno_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Desafio not found'
            )

        # Check if student has submitted
        submissao = await self.submissao_repo.get_aluno_submissao(desafio_id, aluno_id)
        if submissao:
            result.meu_status = submissao.status

        return result

    async def get_ranking(self, desafio_id: UUID) -> List[SubmissaoWithDetails]:
        """Get ranking for desafio."""
        submissoes = await self.submissao_repo.get_by_desafio(desafio_id)
        ranked = sorted(submissoes, key=lambda x: x.pontos_obtidos, reverse=True)
        return [await self.submissao_repo.get_with_details(s.id) for s in ranked]


class SubmissaoService(BaseService[SubmissaoResponse, SubmissaoRepository]):
    """Service for submissao operations."""

    def __init__(self):
        super().__init__(SubmissaoRepository())
        self.voto_repo = VotoRepository()
        self.pontuacao_repo = PontuacaoRepository()

    async def create_submissao(self, data: SubmissaoCreate) -> SubmissaoResponse:
        """Create a new submissao."""
        # Check if already submitted
        existing = await self.repository.get_aluno_submissao(data.desafio_id, data.aluno_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You have already submitted for this desafio'
            )

        submissao = await self.create(data.model_dump())
        return submissao

    async def grade_submissao(
        self,
        submissao_id: UUID,
        points: int,
        feedback: Optional[str] = None
    ) -> SubmissaoResponse:
        """Grade a submissao."""
        submissao = await self.get_by_id(submissao_id)
        if not submissao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Submissao not found'
            )

        # Update submission
        result = await self.repository.update_points(submissao_id, points, feedback)

        # Add points to user
        if points > 0:
            await self.pontuacao_repo.add_points(
                aluno_id=submissao.aluno_id,
                pontos=points,
                fonte='desafio',
                referencia_id=submissao.desafio_id,
                descricao=f'Pontos por submissao avaliada'
            )

            # Update user total points
            from services import UserService
            user_service = UserService()
            await user_service.add_points(submissao.aluno_id, points)

        return result

    async def get_student_submissions(self, aluno_id: UUID) -> List[SubmissaoWithDetails]:
        """Get all submissions for a student."""
        submissoes = await self.repository.get_by_aluno(aluno_id)
        return [await self.repository.get_with_details(s.id) for s in submissoes]


class VotoService(BaseService[VotoResponse, VotoRepository]):
    """Service for voto operations."""

    def __init__(self):
        super().__init__(VotoRepository())
        self.submissao_repo = SubmissaoRepository()

    async def cast_vote(self, data: VotoCreate) -> VotoResponse:
        """Cast a vote on a submission."""
        # Check if already voted
        has_voted = await self.repository.has_voted(data.submissao_id, data.aluno_id)
        if has_voted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You have already voted for this submission'
            )

        # Create vote
        voto = await self.create(data.model_dump())

        # Update submission vote count
        submissao = await self.submissao_repo.get_by_id(data.submissao_id)
        if submissao:
            await self.submissao_repo.update(
                data.submissao_id,
                {'votos': submissao.votos + 1}
            )

        return voto

    async def get_submission_votes(self, submissao_id: UUID) -> List[VotoResponse]:
        """Get all votes for a submission."""
        return await self.repository.get_by_submissao(submissao_id)
