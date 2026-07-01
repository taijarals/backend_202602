"""
Gamification service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from models.gamificacao import (
    PontuacaoCreate, PontuacaoResponse,
    MedalhaCreate, MedalhaResponse, ConquistaResponse,
    NivelResponse, NivelProgress, UserGamificationStats, LeaderboardEntry
)
from repositories import (
    PontuacaoRepository, MedalhaRepository,
    ConquistaRepository, NivelRepository, LeaderboardRepository
)
from .base import BaseService


class GamificacaoService:
    """Service for gamification operations."""

    def __init__(self):
        self.pontuacao_repo = PontuacaoRepository()
        self.medalha_repo = MedalhaRepository()
        self.conquista_repo = ConquistaRepository()
        self.nivel_repo = NivelRepository()
        self.leaderboard_repo = LeaderboardRepository()

    async def add_points(
        self,
        aluno_id: UUID,
        pontos: int,
        fonte: str,
        referencia_id: Optional[UUID] = None,
        turma_id: Optional[UUID] = None,
        disciplina_id: Optional[UUID] = None,
        descricao: Optional[str] = None
    ) -> PontuacaoResponse:
        """Add points to aluno."""
        pontuacao = await self.pontuacao_repo.add_points(
            aluno_id=aluno_id,
            pontos=pontos,
            fonte=fonte,
            referencia_id=referencia_id,
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            descricao=descricao
        )

        # Check for medals
        await self._check_medalhas(aluno_id)

        return pontuacao

    async def _check_medalhas(self, aluno_id: UUID) -> None:
        """Check and award medals based on progress."""
        total_points = await self.pontuacao_repo.get_total_points(aluno_id)
        medalhas = await self.medalha_repo.get_active()

        for medalha in medalhas:
            # Check if already has this medalha
            has_medalha = await self.conquista_repo.has_conquista(aluno_id, medalha.id)
            if has_medalha:
                continue

            # Check criteria
            should_award = False
            if medalha.tipo == 'pontos' and medalha.pontos_requeridos:
                should_award = total_points >= medalha.pontos_requeridos
            elif medalha.tipo == 'desafios':
                # Count completed desafios
                from repositories import SubmissaoRepository
                sub_repo = SubmissaoRepository()
                submissoes = await sub_repo.get_by_aluno(aluno_id)
                completados = len([s for s in submissoes if s.status == 'nota_atribuida' and s.pontos_obtidos > 0])
                if medalha.nome == 'Primeira Contribuição' and completados >= 1:
                    should_award = True
                elif medalha.nome == 'Mestre dos Desafios' and completados >= 10:
                    should_award = True

            if should_award:
                await self.conquista_repo.award_medalha(aluno_id, medalha.id)
                # Award bonus points
                await self.pontuacao_repo.add_points(
                    aluno_id=aluno_id,
                    pontos=50,
                    fonte='medalha',
                    referencia_id=medalha.id,
                    descricao=f'Medalha conquistada: {medalha.nome}'
                )

    async def get_user_stats(self, aluno_id: UUID) -> UserGamificationStats:
        """Get complete gamification stats for user."""
        pontos_totais = await self.pontuacao_repo.get_total_points(aluno_id)
        nivel_progress = await self.nivel_repo.get_progress(pontos_totais)
        conquistas = await self.conquista_repo.get_by_aluno(aluno_id)

        # Get global ranking position
        leaderboard = await self.leaderboard_repo.get_global_leaderboard(1000)
        posicao = next(
            (i + 1 for i, entry in enumerate(leaderboard) if entry.aluno_id == aluno_id),
            None
        )

        # Count stats
        from repositories import SubmissaoRepository, TentativaRepository, ProgressoMissaoRepository
        sub_repo = SubmissaoRepository()
        tentativa_repo = TentativaRepository()
        progresso_repo = ProgressoMissaoRepository()

        submissoes = await sub_repo.get_by_aluno(aluno_id)
        desafios_completados = len([s for s in submissoes if s.status == 'nota_atribuida'])

        tentativas = await tentativa_repo.get_by_aluno(aluno_id)
        provas_completadas = len([t for t in tentativas if t.status == 'finalizada'])

        missao_stats = await progresso_repo.get_missao_stats(aluno_id)

        return UserGamificationStats(
            pontos_totais=pontos_totais,
            nivel_atual=nivel_progress,
            medalhas=conquistas,
            ranking_posicao=posicao,
            desafios_completados=desafios_completados,
            provas_completadas=provas_completadas,
            missoes_completadas=missao_stats.missoes_completadas,
            sequencia_dias=0  # TODO: implement streak tracking
        )

    async def get_leaderboard(self, turma_id: Optional[UUID] = None, limit: int = 100) -> List[LeaderboardEntry]:
        """Get leaderboard."""
        if turma_id:
            return await self.leaderboard_repo.get_turma_leaderboard(turma_id, limit)
        return await self.leaderboard_repo.get_global_leaderboard(limit)

    async def get_levels(self) -> List[NivelResponse]:
        """Get all levels."""
        return await self.nivel_repo.get_all_ordered()

    async def get_medalhas(self) -> List[MedalhaResponse]:
        """Get all active medalhas."""
        return await self.medalha_repo.get_active()

    async def get_aluno_conquistas(self, aluno_id: UUID) -> List[ConquistaResponse]:
        """Get aluno's conquistas."""
        return await self.conquista_repo.get_by_aluno(aluno_id)


class MedalhaService(BaseService[MedalhaResponse, MedalhaRepository]):
    """Service for medalha operations."""

    def __init__(self):
        super().__init__(MedalhaRepository())

    async def create_medalha(self, data: MedalhaCreate) -> MedalhaResponse:
        """Create new medalha."""
        return await self.create(data.model_dump())

    async def get_active(self) -> List[MedalhaResponse]:
        """Get all active medalhas."""
        return await self.repository.get_active()
