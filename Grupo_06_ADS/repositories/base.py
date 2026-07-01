"""
Base repository implementation.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from uuid import UUID
from pydantic import BaseModel
from database import get_db
from providers import SupabaseProvider

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Base repository with common CRUD operations.
    Subclasses can override or extend these methods.
    """

    def __init__(self, table: str, model: Type[T], provider: Optional[SupabaseProvider] = None):
        self.table = table
        self.model = model
        self._provider = provider
        self._db = None

    @property
    def db(self) -> SupabaseProvider:
        """Get database provider instance."""
        if self._provider:
            return self._provider
        if self._db is None:
            self._db = SupabaseProvider(get_db())
        return self._db

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new record."""
        result = await self.db.create(self.table, data)
        return self.model.model_validate(result)

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get a record by ID."""
        result = await self.db.get_by_id(self.table, id)
        if result:
            return self.model.model_validate(result)
        return None

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        select: Optional[str] = None
    ) -> List[T]:
        """Get all records with optional filtering."""
        results = await self.db.get_all(
            self.table,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            select=select
        )
        return [self.model.model_validate(r) for r in results]

    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        result = await self.db.update(self.table, id, data)
        if result:
            return self.model.model_validate(result)
        return None

    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        return await self.db.delete(self.table, id)

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        return await self.db.count(self.table, filters=filters)

    async def exists(self, id: UUID) -> bool:
        """Check if record exists."""
        result = await self.get_by_id(id)
        return result is not None

    async def get_one(self, filters: Dict[str, Any]) -> Optional[T]:
        """Get a single record by filters."""
        results = await self.get_all(filters=filters, limit=1)
        return results[0] if results else None
