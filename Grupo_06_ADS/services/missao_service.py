"""
Missao service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from models.missao import (
    MissaoEtapaCreate, MissaoEtapaResponse,
    MissaoCreate, MissaoUpdate, MissaoResponse, MissaoWithEtapas, MissaoProgress,
    ProgressoEtapaCreate, ProgressoEtapaResponse, UserMissionStats
)
from repositories import MissaoRepository, MissaoEtapaRepository, ProgressoMissaoRepository
from .base import BaseService


class MissaoService(BaseService[MissaoResponse, MissaoRepository]):
    """Service for missao operations."""

    def __init__(self):
        super().__init__(MissaoRepository())
        self.etapa_repo = MissaoEtapaRepository()
        self.progresso_repo = ProgressoMissaoRepository()

    async def create_missao(self, data: MissaoCreate) -> MissaoWithEtapas:
        """Create missao with etapas."""
        missao_data = data.model_dump(exclude={'etapas'})
        missao = await self.create(missao_data)

        # Create etapas
        for i, etapa in enumerate(data.etapas):
            etapa_data = etapa.model_dump()
            etapa_data['missao_id'] = str(missao.id)
            etapa_data['ordem'] = i
            await self.etapa_repo.create(etapa_data)

        return await self.get_with_etapas(missao.id)

    async def update_missao(self, id: UUID, data: MissaoUpdate) -> MissaoResponse:
        """Update missao."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Missao not found'
            )
        return result

    async def get_with_etapas(self, id: UUID) -> MissaoWithEtapas:
        """Get missao with etapas."""
        result = await self.repository.get_with_etapas(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Missao not found'
            )
        return result

    async def get_for_aluno(self, id: UUID, aluno_id: UUID) -> MissaoProgress:
        """Get missao with aluno progress."""
        result = await self.repository.get_for_aluno(id, aluno_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Missao not found'
            )
        return result

    async def get_available_for_aluno(self, aluno_id: UUID) -> List[MissaoProgress]:
        """Get all available missoes with progress for aluno."""
        return await self.repository.get_available_for_aluno(aluno_id)

    async def start_etapa(self, missao_id: UUID, etapa_id: UUID, aluno_id: UUID) -> ProgressoEtapaResponse:
        """Start working on an etapa."""
        # Verify etapa belongs to missao
        etapa = await self.etapa_repo.get_by_id(etapa_id)
        if not etapa or etapa.missao_id != missao_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid etapa'
            )

        # Check prerequisites (previous etapas)
        etapas = await self.etapa_repo.get_by_missao(missao_id)
        etapa_index = next((i for i, e in enumerate(etapas) if e.id == etapa_id), -1)

        if etapa_index > 0:
            prev_etapa = etapas[etapa_index - 1]
            prev_progress = await self.progresso_repo.get_etapa_progress(prev_etapa.id, aluno_id)
            if not prev_progress or prev_progress.status != 'completa':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Previous etapa not completed'
                )

        return await self.progresso_repo.start_etapa(missao_id, etapa_id, aluno_id)

    async def complete_etapa(
        self,
        missao_id: UUID,
        etapa_id: UUID,
        aluno_id: UUID,
        points: Optional[int] = None
    ) -> ProgressoEtapaResponse:
        """Complete an etapa."""
        # Get etapa for default points
        etapa = await self.etapa_repo.get_by_id(etapa_id)
        if not etapa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Etapa not found'
            )

        awarded_points = points if points is not None else etapa.pontos
        progresso = await self.progresso_repo.complete_etapa(
            missao_id, etapa_id, aluno_id, awarded_points
        )

        # Award points to user
        if awarded_points > 0:
            from services import GamificacaoService
            gamificacao = GamificacaoService()
            await gamificacao.add_points(
                aluno_id=aluno_id,
                pontos=awarded_points,
                fonte='missao',
                referencia_id=etapa_id,
                descricao=f'Etapa completada: {etapa.titulo}'
            )

        # Check if missao is complete
        await self._check_missao_completion(missao_id, aluno_id)

        return progresso

    async def _check_missao_completion(self, missao_id: UUID, aluno_id: UUID) -> None:
        """Check if missao is complete and award bonus."""
        missao = await self.get_with_etapas(missao_id)
        if not missao:
            return

        progressos = await self.progresso_repo.get_by_aluno(aluno_id, missao_id)
        all_complete = all(
            any(p.etapa_id == e.id and p.status == 'completa' for p in progressos)
            for e in missao.etapas
        )

        if all_complete:
            # Award missao completion bonus
            missao_progress = await self.repository.get_for_aluno(missao_id, aluno_id)
            if missao_progress and missao_progress.pontos_recompensa > 0:
                from services import GamificacaoService
                gamificacao = GamificacaoService()
                await gamificacao.add_points(
                    aluno_id=aluno_id,
                    pontos=missao_progress.pontos_recompensa,
                    fonte='missao',
                    referencia_id=missao_id,
                    descricao=f'Missao completada: {missao_progress.titulo}'
                )

    async def get_student_stats(self, aluno_id: UUID) -> UserMissionStats:
        """Get mission statistics for aluno."""
        return await self.progresso_repo.get_missao_stats(aluno_id)

    async def get_by_turma(self, turma_id: UUID) -> List[MissaoWithEtapas]:
        """Get missoes for a turma."""
        missoes = await self.repository.get_by_turma(turma_id)
        results = []
        for m in missoes:
            with_etapas = await self.get_with_etapas(m.id)
            if with_etapas:
                results.append(with_etapas)
        return results


class MissaoEtapaService(BaseService[MissaoEtapaResponse, MissaoEtapaRepository]):
    """Service for missao etapa operations."""

    def __init__(self):
        super().__init__(MissaoEtapaRepository())

    async def get_by_missao(self, missao_id: UUID) -> List[MissaoEtapaResponse]:
        """Get etapas for a missao."""
        return await self.repository.get_by_missao(missao_id)
