"""
Disciplina service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from models.disciplina import DisciplinaCreate, DisciplinaUpdate, DisciplinaResponse, DisciplinaWithDetails
from repositories import DisciplinaRepository
from .base import BaseService


class DisciplinaService(BaseService[DisciplinaResponse, DisciplinaRepository]):
    """Service for disciplina operations."""

    def __init__(self):
        super().__init__(DisciplinaRepository())

    async def create_disciplina(self, data: DisciplinaCreate) -> DisciplinaResponse:
        """Create a new disciplina."""
        # Check if code exists
        if data.codigo:
            existing = await self.repository.get_by_code(data.codigo)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Disciplina codigo already exists'
                )

        return await self.create(data.model_dump())

    async def update_disciplina(self, id: UUID, data: DisciplinaUpdate) -> DisciplinaResponse:
        """Update disciplina."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Disciplina not found'
            )
        return result

    async def get_by_professor(self, professor_id: UUID) -> List[DisciplinaWithDetails]:
        """Get disciplinas by professor with details."""
        return await self.repository.get_all_with_details(professor_id)

    async def get_with_details(self, id: UUID) -> DisciplinaWithDetails:
        """Get disciplina with details."""
        result = await self.repository.get_with_details(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Disciplina not found'
            )
        return result

    async def get_active(self) -> List[DisciplinaResponse]:
        """Get all active disciplinas."""
        return await self.repository.get_active()

    async def deactivate(self, id: UUID) -> DisciplinaResponse:
        """Deactivate a disciplina."""
        result = await self.repository.deactivate(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Disciplina not found'
            )
        return result

    async def get_all_summary(self) -> List[DisciplinaWithDetails]:
        """Get all disciplinas with summary info."""
        return await self.repository.get_all_with_details()
