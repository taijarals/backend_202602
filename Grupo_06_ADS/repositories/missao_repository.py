"""
Missao repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from models.missao import (
    MissaoEtapaResponse,
    MissaoResponse, MissaoWithEtapas, MissaoProgress,
    ProgressoEtapaResponse, UserMissionStats
)
from .base import BaseRepository


class MissaoRepository(BaseRepository[MissaoResponse]):
    """Repository for missao operations."""

    def __init__(self):
        super().__init__('missoes', MissaoResponse)

    async def get_by_professor(self, professor_id: UUID) -> List[MissaoResponse]:
        """Get missoes by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)}, order_by='-created_at')

    async def get_by_turma(self, turma_id: UUID) -> List[MissaoResponse]:
        """Get missoes for a turma."""
        return await self.get_all(filters={'turma_id': str(turma_id), 'ativa': True})

    async def get_by_disciplina(self, disciplina_id: UUID) -> List[MissaoResponse]:
        """Get missoes for a disciplina."""
        return await self.get_all(filters={'disciplina_id': str(disciplina_id), 'ativa': True})

    async def get_with_etapas(self, id: UUID) -> Optional[MissaoWithEtapas]:
        """Get missao with etapas."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,disciplinas(nome),turmas(nome)'
        )
        if result:
            data = result
            data['disciplina_nome'] = result.get('disciplinas', {}).get('nome') if result.get('disciplinas') else None
            data['turma_nome'] = result.get('turmas', {}).get('nome') if result.get('turmas') else None
            # Get etapas
            etapas = await self.db.get_all(
                'missoes_etapas',
                filters={'missao_id': str(id)},
                order_by='ordem'
            )
            data['etapas'] = [MissaoEtapaResponse.model_validate(e) for e in etapas]
            data['total_etapas'] = len(etapas)
            return MissaoWithEtapas.model_validate(data)
        return None

    async def get_for_aluno(self, id: UUID, aluno_id: UUID) -> Optional[MissaoProgress]:
        """Get missao with aluno progress."""
        missao = await self.get_with_etapas(id)
        if not missao:
            return None

        data = missao.model_dump()
        # Get progress for each etapa
        progressos = await self.db.get_all(
            'progresso_missao',
            filters={'missao_id': str(id), 'aluno_id': str(aluno_id)}
        )

        progress_map = {p['etapa_id']: p for p in progressos}
        completed = 0
        total_points = 0

        for etapa in data.get('etapas', []):
            progress = progress_map.get(str(etapa['id']))
            if progress and progress.get('status') == 'completa':
                completed += 1
                total_points += progress.get('pontos_obtidos', 0)
            etapa['progresso'] = progress

        data['etapas_completas'] = completed
        data['pontos_obtidos'] = total_points
        data['progresso_atual'] = int((completed / len(data.get('etapas', [])) * 100)) if data.get('etapas') else 0
        data['status'] = 'completa' if completed == len(data.get('etapas', [])) else ('em_progresso' if completed > 0 else 'nao_iniciada')

        return MissaoProgress.model_validate(data)

    async def get_available_for_aluno(self, aluno_id: UUID) -> List[MissaoProgress]:
        """Get all available missoes with progress for aluno."""
        missoes = await self.get_all(filters={'ativa': True})
        results = []
        for m in missoes:
            progress = await self.get_for_aluno(m.id, aluno_id)
            if progress:
                results.append(progress)
        return results


class MissaoEtapaRepository(BaseRepository[MissaoEtapaResponse]):
    """Repository for missao etapa operations."""

    def __init__(self):
        super().__init__('missoes_etapas', MissaoEtapaResponse)

    async def get_by_missao(self, missao_id: UUID) -> List[MissaoEtapaResponse]:
        """Get etapas for a missao."""
        return await self.get_all(filters={'missao_id': str(missao_id)}, order_by='ordem')


class ProgressoMissaoRepository(BaseRepository[ProgressoEtapaResponse]):
    """Repository for progresso missao operations."""

    def __init__(self):
        super().__init__('progresso_missao', ProgressoEtapaResponse)

    async def get_by_aluno(self, aluno_id: UUID, missao_id: Optional[UUID] = None) -> List[ProgressoEtapaResponse]:
        """Get progress by aluno."""
        filters = {'aluno_id': str(aluno_id)}
        if missao_id:
            filters['missao_id'] = str(missao_id)
        return await self.get_all(filters=filters)

    async def get_etapa_progress(self, etapa_id: UUID, aluno_id: UUID) -> Optional[ProgressoEtapaResponse]:
        """Get progress for specific etapa."""
        return await self.get_one({'etapa_id': str(etapa_id), 'aluno_id': str(aluno_id)})

    async def start_etapa(self, missao_id: UUID, etapa_id: UUID, aluno_id: UUID) -> ProgressoEtapaResponse:
        """Start working on an etapa."""
        existing = await self.get_etapa_progress(etapa_id, aluno_id)
        if existing:
            return await self.update(existing.id, {'status': 'em_progresso'})
        return await self.create({
            'missao_id': str(missao_id),
            'etapa_id': str(etapa_id),
            'aluno_id': str(aluno_id),
            'status': 'em_progresso'
        })

    async def complete_etapa(
        self,
        missao_id: UUID,
        etapa_id: UUID,
        aluno_id: UUID,
        points: int
    ) -> ProgressoEtapaResponse:
        """Complete an etapa."""
        existing = await self.get_etapa_progress(etapa_id, aluno_id)
        if existing:
            return await self.update(existing.id, {
                'status': 'completa',
                'pontos_obtidos': points,
                'completada_em': datetime.utcnow().isoformat()
            })
        return await self.create({
            'missao_id': str(missao_id),
            'etapa_id': str(etapa_id),
            'aluno_id': str(aluno_id),
            'status': 'completa',
            'pontos_obtidos': points,
            'completada_em': datetime.utcnow().isoformat()
        })

    async def get_missao_stats(self, aluno_id: UUID) -> UserMissionStats:
        """Get mission statistics for aluno."""
        progressos = await self.get_by_aluno(aluno_id)
        missoes_ids = set(p.missao_id for p in progressos)

        missoes_iniciadas = len(missoes_ids)
        missoes_completadas = 0
        pontos_totais = 0

        for missao_id in missoes_ids:
            missao_progress = [p for p in progressos if p.missao_id == missao_id]
            etapa_repo = MissaoEtapaRepository()
            etapas = await etapa_repo.get_by_missao(missao_id)

            if len(missao_progress) == len(etapas) and all(p.status == 'completa' for p in missao_progress):
                missoes_completadas += 1

            pontos_totais += sum(p.pontos_obtidos for p in missao_progress)

        taxa = (missoes_completadas / missoes_iniciadas * 100) if missoes_iniciadas > 0 else 0

        return UserMissionStats(
            missoes_iniciadas=missoes_iniciadas,
            missoes_completadas=missoes_completadas,
            pontos_totais=pontos_totais,
            taxa_conclusao=taxa
        )
