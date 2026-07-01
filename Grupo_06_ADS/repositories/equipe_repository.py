"""
Equipe repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from models.equipe import (
    EquipeCreate, EquipeUpdate, EquipeResponse,
    EquipeMembroResponse, EquipeWithDetails
)
from .base import BaseRepository


class EquipeRepository(BaseRepository[EquipeResponse]):
    """Repository for equipe operations."""

    def __init__(self):
        super().__init__('equipes', EquipeResponse)

    async def get_by_turma(self, turma_id: UUID) -> List[EquipeResponse]:
        """Get equipes by turma."""
        return await self.get_all(filters={'turma_id': str(turma_id)}, order_by='nome')

    async def get_with_members(self, id: UUID) -> Optional[EquipeWithDetails]:
        """Get equipe with members."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,turmas(nome)'
        )
        if result:
            data = result
            data['turma_nome'] = result.get('turmas', {}).get('nome') if result.get('turmas') else None
            # Get members
            membros = await self.db.get_all(
                'equipe_membros',
                filters={'equipe_id': str(id)},
                select='*,profiles!aluno_id(nome,email,pontuacao_total)'
            )
            data['membros'] = []
            for m in membros:
                m['aluno_nome'] = m.get('profiles', {}).get('nome') if m.get('profiles') else None
                m['aluno_email'] = m.get('profiles', {}).get('email') if m.get('profiles') else None
                m['aluno_pontos'] = m.get('profiles', {}).get('pontuacao_total', 0) if m.get('profiles') else 0
                data['membros'].append(EquipeMembroResponse.model_validate(m))
            data['total_membros'] = len(data['membros'])
            return EquipeWithDetails.model_validate(data)
        return None

    async def update_points(self, id: UUID, points: int) -> Optional[EquipeResponse]:
        """Update equipe total points."""
        equipe = await self.get_by_id(id)
        if equipe:
            new_total = equipe.pontuacao + points
            return await self.update(id, {'pontuacao': new_total})
        return None


class EquipeMembroRepository(BaseRepository[EquipeMembroResponse]):
    """Repository for equipe membro operations."""

    def __init__(self):
        super().__init__('equipe_membros', EquipeMembroResponse)

    async def add_member(self, equipe_id: UUID, aluno_id: UUID, papel: str = 'membro') -> EquipeMembroResponse:
        """Add member to equipe."""
        return await self.create({
            'equipe_id': str(equipe_id),
            'aluno_id': str(aluno_id),
            'papel': papel
        })

    async def remove_member(self, equipe_id: UUID, aluno_id: UUID) -> bool:
        """Remove member from equipe."""
        result = await self.get_one({'equipe_id': str(equipe_id), 'aluno_id': str(aluno_id)})
        if result:
            return await self.delete(result.id)
        return False

    async def get_members(self, equipe_id: UUID) -> List[EquipeMembroResponse]:
        """Get all members of equipe."""
        results = await self.db.get_all(
            self.table,
            filters={'equipe_id': str(equipe_id)},
            select='*,profiles!aluno_id(nome,email,pontuacao_total)'
        )
        items = []
        for r in results:
            r['aluno_nome'] = r.get('profiles', {}).get('nome') if r.get('profiles') else None
            r['aluno_email'] = r.get('profiles', {}).get('email') if r.get('profiles') else None
            r['aluno_pontos'] = r.get('profiles', {}).get('pontuacao_total', 0) if r.get('profiles') else 0
            items.append(EquipeMembroResponse.model_validate(r))
        return items

    async def get_aluno_equipe(self, aluno_id: UUID, turma_id: Optional[UUID] = None) -> Optional[EquipeMembroResponse]:
        """Get equipe membership for aluno."""
        filters = {'aluno_id': str(aluno_id)}
        if turma_id:
            # Need to join with equipes to filter by turma
            results = await self.db.get_all(
                self.table,
                filters={'aluno_id': str(aluno_id)},
                select='*,equipes!equipe_id(turma_id)'
            )
            for r in results:
                equipe = r.get('equipes', {})
                if equipe and equipe.get('turma_id') == str(turma_id):
                    r['aluno_nome'] = None
                    r['aluno_email'] = None
                    r['aluno_pontos'] = 0
                    return EquipeMembroResponse.model_validate(r)
            return None
        return await self.get_one(filters)

    async def is_member(self, equipe_id: UUID, aluno_id: UUID) -> bool:
        """Check if aluno is member of equipe."""
        result = await self.get_one({'equipe_id': str(equipe_id), 'aluno_id': str(aluno_id)})
        return result is not None

    async def get_member_count(self, equipe_id: UUID) -> int:
        """Get number of members in equipe."""
        return await self.count({'equipe_id': str(equipe_id)})
