"""
Enquete service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from models.enquete import (
    EnqueteCreate, EnqueteUpdate, EnqueteResponse, EnqueteWithOpcoes,
    VotoEnqueteResponse, EnqueteStats
)
from repositories import EnqueteRepository, OpcaoEnqueteRepository, VotoEnqueteRepository
from .base import BaseService


class EnqueteService(BaseService[EnqueteResponse, EnqueteRepository]):
    """Service for enquete operations."""

    def __init__(self):
        super().__init__(EnqueteRepository())
        self.opcao_repo = OpcaoEnqueteRepository()
        self.voto_repo = VotoEnqueteRepository()

    async def create_enquete(self, data: EnqueteCreate) -> EnqueteWithOpcoes:
        """Create enquete with opcoes."""
        enquete_data = data.model_dump(exclude={'opcoes'})
        enquete = await self.create(enquete_data)

        # Create opcoes
        await self.opcao_repo.create_many(enquete.id, data.opcoes)

        return await self.get_with_opcoes(enquete.id)

    async def update_enquete(self, id: UUID, data: EnqueteUpdate) -> EnqueteResponse:
        """Update enquete."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Enquete not found'
            )
        return result

    async def get_with_opcoes(self, id: UUID) -> EnqueteWithOpcoes:
        """Get enquete with opcoes and vote stats."""
        result = await self.repository.get_with_opcoes(id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Enquete not found'
            )
        return result

    async def get_by_turma(self, turma_id: UUID) -> List[EnqueteWithOpcoes]:
        """Get enquetes for a turma."""
        enquetes = await self.repository.get_by_turma(turma_id)
        return [await self.get_with_opcoes(e.id) for e in enquetes]

    async def cast_vote(self, enquete_id: UUID, opcao_id: UUID, aluno_id: UUID) -> VotoEnqueteResponse:
        """Cast a vote in enquete."""
        # Check if enquete is active
        enquete = await self.get_by_id(enquete_id)
        if not enquete or not enquete.ativa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Enquete is not active'
            )

        if enquete.fim and datetime.utcnow() > enquete.fim:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Enquete has ended'
            )

        # Check if already voted
        has_voted = await self.voto_repo.has_voted(enquete_id, aluno_id)
        if has_voted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='You have already voted'
            )

        # Verify opcao belongs to enquete
        opcao = await self.opcao_repo.get_by_id(opcao_id)
        if not opcao or opcao.enquete_id != enquete_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid option for this enquete'
            )

        return await self.voto_repo.cast_vote(enquete_id, opcao_id, aluno_id)

    async def get_stats(self, enquete_id: UUID, turma_id: Optional[UUID] = None) -> EnqueteStats:
        """Get enquete statistics."""
        enquete = await self.get_by_id(enquete_id)
        if not enquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Enquete not found'
            )

        return await self.voto_repo.get_stats(enquete_id, turma_id or enquete.turma_id)

    async def close_enquete(self, enquete_id: UUID) -> EnqueteResponse:
        """Close an enquete."""
        return await self.update(enquete_id, {'ativa': False, 'fim': datetime.utcnow()})

    async def get_active(self) -> List[EnqueteWithOpcoes]:
        """Get all active enquetes."""
        enquetes = await self.repository.get_active()
        return [await self.get_with_opcoes(e.id) for e in enquetes]
