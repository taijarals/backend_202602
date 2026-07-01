"""
User service implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from models.user import UserCreate, UserUpdate, UserResponse, UserStats
from repositories import UserRepository
from .base import BaseService


class UserService(BaseService[UserResponse, UserRepository]):
    """Service for user operations."""

    def __init__(self):
        super().__init__(UserRepository())

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_professors(self) -> List[UserResponse]:
        """Get all professors."""
        return await self.repository.get_professors()

    async def get_students(self) -> List[UserResponse]:
        """Get all students."""
        return await self.repository.get_students()

    async def get_ranking(self, limit: int = 10) -> List[UserResponse]:
        """Get user ranking by points."""
        return await self.repository.get_ranking(limit)

    async def update_profile(self, id: UUID, data: UserUpdate) -> UserResponse:
        """Update user profile."""
        update_data = data.model_dump(exclude_unset=True)
        result = await self.update(id, update_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        return result

    async def add_points(self, user_id: UUID, points: int) -> UserResponse:
        """Add points to user and update level."""
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        # Update points
        updated_user = await self.repository.update_points(user_id, points)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to update points'
            )

        # Check level-up
        await self._check_level_up(updated_user)

        return updated_user

    async def _check_level_up(self, user: UserResponse) -> None:
        """Check and apply level-up if necessary."""
        from repositories import NivelRepository
        nivel_repo = NivelRepository()
        next_level = await nivel_repo.get_by_pontos(user.pontuacao_total)
        if next_level and next_level.nivel > user.nivel:
            await self.repository.update(user.id, {'nivel': next_level.nivel})

    async def get_stats(self, user_id: UUID) -> UserStats:
        """Get user statistics."""
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        stats_data = await self.repository.get_stats(user_id)

        return UserStats(
            total_pontos=user.pontuacao_total,
            nivel_atual=user.nivel,
            desafios_completados=stats_data.get('desafios', 0),
            provas_realizadas=stats_data.get('provas', 0),
            missoes_completadas=stats_data.get('missoes', 0),
            medalhas_conquistadas=stats_data.get('medalhas', 0),
            ranking_geral=stats_data.get('ranking')
        )

    async def search_users(self, query: str, role: Optional[str] = None) -> List[UserResponse]:
        """Search users by name or email."""
        return await self.repository.search(query, role)
