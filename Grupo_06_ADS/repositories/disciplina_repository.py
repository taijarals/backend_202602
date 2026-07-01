"""
Disciplina repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from models.disciplina import DisciplinaCreate, DisciplinaUpdate, DisciplinaResponse, DisciplinaWithDetails
from .base import BaseRepository


class DisciplinaRepository(BaseRepository[DisciplinaResponse]):
    """Repository for disciplina operations."""

    def __init__(self):
        super().__init__('disciplinas', DisciplinaResponse)

    async def get_by_professor(self, professor_id: UUID) -> List[DisciplinaResponse]:
        """Get disciplinas by professor."""
        return await self.get_all(filters={'professor_id': str(professor_id)})

    async def get_with_details(self, id: UUID) -> Optional[DisciplinaWithDetails]:
        """Get disciplina with details."""
        result = await self.db.get_by_id(
            self.table,
            id,
            select='*,profiles!professor_id(nome)'
        )
        if result:
            data = result
            data['professor_nome'] = result.get('profiles', {}).get('nome') if result.get('profiles') else None
            return DisciplinaWithDetails.model_validate(data)
        return None

    async def get_all_with_details(self, professor_id: Optional[UUID] = None) -> List[DisciplinaWithDetails]:
        """Get all disciplinas with details."""
        filters = {}
        if professor_id:
            filters['professor_id'] = str(professor_id)

        results = await self.db.get_all(
            self.table,
            filters=filters,
            order_by='-created_at',
            select='*,profiles!professor_id(nome)'
        )

        items = []
        for r in results:
            r['professor_nome'] = r.get('profiles', {}).get('nome') if r.get('profiles') else None
            items.append(DisciplinaWithDetails.model_validate(r))
        return items

    async def get_active(self) -> List[DisciplinaResponse]:
        """Get all active disciplinas."""
        return await self.get_all(filters={'ativa': True}, order_by='nome')

    async def get_by_code(self, codigo: str) -> Optional[DisciplinaResponse]:
        """Get disciplina by code."""
        return await self.get_one({'codigo': codigo})

    async def deactivate(self, id: UUID) -> Optional[DisciplinaResponse]:
        """Deactivate a disciplina."""
        return await self.update(id, {'ativa': False})
