"""
Gamification repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from models.gamificacao import (
    PontuacaoResponse, MedalhaResponse, ConquistaResponse,
    NivelResponse, NivelProgress, LeaderboardEntry
)
from .base import BaseRepository


class PontuacaoRepository(BaseRepository[PontuacaoResponse]):
    """Repository for pontuacao operations."""

    def __init__(self):
        super().__init__('pontuacoes', PontuacaoResponse)

    async def get_by_aluno(self, aluno_id: UUID) -> List[PontuacaoResponse]:
        """Get pontuacoes by aluno."""
        return await self.get_all(filters={'aluno_id': str(aluno_id)}, order_by='-created_at')

    async def get_by_turma(self, turma_id: UUID) -> List[PontuacaoResponse]:
        """Get pontuacoes by turma."""
        return await self.get_all(filters={'turma_id': str(turma_id)})

    async def get_total_points(self, aluno_id: UUID) -> int:
        """Get total points for aluno."""
        pontuacoes = await self.get_by_aluno(aluno_id)
        return sum(p.pontos for p in pontuacoes)

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
        return await self.create({
            'aluno_id': str(aluno_id),
            'pontos': pontos,
            'fonte': fonte,
            'referencia_id': str(referencia_id) if referencia_id else None,
            'turma_id': str(turma_id) if turma_id else None,
            'disciplina_id': str(disciplina_id) if disciplina_id else None,
            'descricao': descricao
        })


class MedalhaRepository(BaseRepository[MedalhaResponse]):
    """Repository for medalha operations."""

    def __init__(self):
        super().__init__('medalhas', MedalhaResponse)

    async def get_active(self) -> List[MedalhaResponse]:
        """Get all active medals."""
        return await self.get_all(filters={'ativa': True})

    async def get_by_tipo(self, tipo: str) -> List[MedalhaResponse]:
        """Get medals by type."""
        return await self.get_all(filters={'tipo': tipo, 'ativa': True})


class ConquistaRepository(BaseRepository[ConquistaResponse]):
    """Repository for conquista operations."""

    def __init__(self):
        super().__init__('conquistas', ConquistaResponse)

    async def get_by_aluno(self, aluno_id: UUID) -> List[ConquistaResponse]:
        """Get conquistas by aluno."""
        results = await self.db.get_all(
            self.table,
            filters={'aluno_id': str(aluno_id)},
            select='*,medalhas(*)'
        )
        items = []
        for r in results:
            r['medalha'] = r.get('medalhas') if r.get('medalhas') else None
            items.append(ConquistaResponse.model_validate(r))
        return items

    async def has_conquista(self, aluno_id: UUID, medalha_id: UUID) -> bool:
        """Check if aluno has conquista."""
        result = await self.get_one({'aluno_id': str(aluno_id), 'medalha_id': str(medalha_id)})
        return result is not None

    async def award_medalha(self, aluno_id: UUID, medalha_id: UUID) -> ConquistaResponse:
        """Award medalha to aluno."""
        return await self.create({
            'aluno_id': str(aluno_id),
            'medalha_id': str(medalha_id)
        })


class NivelRepository(BaseRepository[NivelResponse]):
    """Repository for nivel operations."""

    def __init__(self):
        super().__init__('niveis', NivelResponse)

    async def get_all_ordered(self) -> List[NivelResponse]:
        """Get all levels ordered by pontos."""
        return await self.get_all(order_by='nivel')

    async def get_by_pontos(self, pontos: int) -> Optional[NivelResponse]:
        """Get level for given points."""
        niveis = await self.get_all_ordered()
        current_level = None
        for nivel in niveis:
            if pontos >= nivel.pontos_necessarios:
                current_level = nivel
            else:
                break
        return current_level

    async def get_next_level(self, nivel: int) -> Optional[NivelResponse]:
        """Get next level."""
        result = await self.get_one({'nivel': nivel + 1})
        return result

    async def get_progress(self, pontos: int) -> NivelProgress:
        """Get user level progress."""
        niveis = await self.get_all_ordered()
        current_level = None
        next_level = None

        for i, nivel in enumerate(niveis):
            if pontos >= nivel.pontos_necessarios:
                current_level = nivel
                next_level = niveis[i + 1] if i + 1 < len(niveis) else None
            else:
                break

        if not current_level:
            current_level = niveis[0]

        next_points = next_level.pontos_necessarios if next_level else current_level.pontos_necessarios
        current_points = current_level.pontos_necessarios

        progress = 0
        if next_level:
            total_range = next_points - current_points
            current_progress = pontos - current_points
            progress = min(100, max(0, (current_progress / total_range) * 100)) if total_range > 0 else 100

        return NivelProgress(
            nivel_atual=current_level.nivel,
            nivel_nome=current_level.nome,
            pontos_atuais=pontos,
            pontos_proximo_nivel=next_points,
            progresso_percentual=progress,
            proximo_nivel=next_level
        )


class LeaderboardRepository:
    """Repository for leaderboard operations."""

    def __init__(self):
        from database import get_db
        self._db = get_db()

    async def get_global_leaderboard(self, limit: int = 100) -> List[LeaderboardEntry]:
        """Get global leaderboard."""
        response = self._db.table('profiles').select(
            'id,nome,pontuacao_total,nivel'
        ).eq('role', 'student').order('pontuacao_total', desc=True).limit(limit).execute()

        entries = []
        for i, r in enumerate(response.data or [], 1):
            # Count medals
            conquistas = self._db.table('conquistas').select('id', count='exact').eq('aluno_id', r['id']).execute()
            entries.append(LeaderboardEntry(
                posicao=i,
                aluno_id=r['id'],
                aluno_nome=r['nome'],
                pontos=r['pontuacao_total'],
                nivel=r['nivel'],
                medalhas=conquistas.count or 0
            ))
        return entries

    async def get_turma_leaderboard(self, turma_id: UUID, limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard for a turma."""
        response = self._db.table('turma_alunos').select(
            'aluno_id,profiles!aluno_id(id,nome,pontuacao_total,nivel)'
        ).eq('turma_id', str(turma_id)).execute()

        students = []
        for r in response.data or []:
            profile = r.get('profiles', {})
            if profile:
                conquistas = self._db.table('conquistas').select('id', count='exact').eq('aluno_id', profile['id']).execute()
                students.append({
                    'id': profile['id'],
                    'nome': profile['nome'],
                    'pontos': profile['pontuacao_total'],
                    'nivel': profile['nivel'],
                    'medalhas': conquistas.count or 0
                })

        # Sort by points
        students.sort(key=lambda x: x['pontos'], reverse=True)
        return [
            LeaderboardEntry(posicao=i+1, **s)
            for i, s in enumerate(students[:limit])
        ]
