"""
Base service implementation.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from uuid import UUID
from pydantic import BaseModel
from repositories.base import BaseRepository

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R', bound=BaseRepository)


class BaseService(Generic[T, R]):
    """
    Base service with common operations.
    Services contain business logic and coordinate between repositories.
    """

    def __init__(self, repository: R):
        self.repository = repository

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new entity."""
        return await self.repository.create(data)

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        return await self.repository.get_by_id(id)

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all entities with pagination."""
        offset = (page - 1) * page_size
        items = await self.repository.get_all(
            filters=filters,
            order_by=order_by,
            limit=page_size,
            offset=offset
        )
        total = await self.repository.count(filters=filters)
        total_pages = (total + page_size - 1) // page_size
        return {
            'items': items,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages
        }

    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID."""
        return await self.repository.update(id, data)

    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        return await self.repository.delete(id)

    async def exists(self, id: UUID) -> bool:
        """Check if entity exists."""
        return await self.repository.exists(id)
