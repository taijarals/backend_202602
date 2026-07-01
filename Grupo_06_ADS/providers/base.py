"""
Provider Pattern Implementation.

This module implements the Provider Pattern to allow switching
between different data persistence strategies without changing
business logic.

Provider Hierarchy:
- DatabaseProvider (Abstract Base)
  - SQLProvider (SQL-based implementations)
    - SupabaseProvider (Supabase/PostgreSQL implementation)
  - ProviderFactory (Factory for creating providers)
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from uuid import UUID
from datetime import datetime

T = TypeVar('T')


class DatabaseProvider(ABC, Generic[T]):
    """
    Abstract base provider for database operations.
    Defines the interface for all database operations.
    """

    @abstractmethod
    async def create(self, table: str, data: Dict[str, Any]) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    async def get_by_id(self, table: str, id: UUID) -> Optional[T]:
        """Get a record by ID."""
        pass

    @abstractmethod
    async def get_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """Get all records with optional filtering."""
        pass

    @abstractmethod
    async def update(self, table: str, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        pass

    @abstractmethod
    async def delete(self, table: str, id: UUID) -> bool:
        """Delete a record by ID."""
        pass

    @abstractmethod
    async def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        pass

    @abstractmethod
    async def execute_raw(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute raw query."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check database connection health."""
        pass


class SQLProvider(DatabaseProvider[T]):
    """
    SQL-based provider with common SQL operations.
    Subclasses implement specific database clients.
    """

    def __init__(self):
        self._default_select = "*"

    def _build_filters(self, filters: Dict[str, Any]) -> str:
        """Build SQL WHERE clause from filters."""
        if not filters:
            return ""
        conditions = []
        for key, value in filters.items():
            if isinstance(value, dict):
                for op, val in value.items():
                    if op == 'eq':
                        conditions.append(f"{key} = '{val}'")
                    elif op == 'neq':
                        conditions.append(f"{key} != '{val}'")
                    elif op == 'gt':
                        conditions.append(f"{key} > '{val}'")
                    elif op == 'gte':
                        conditions.append(f"{key} >= '{val}'")
                    elif op == 'lt':
                        conditions.append(f"{key} < '{val}'")
                    elif op == 'lte':
                        conditions.append(f"{key} <= '{val}'")
                    elif op == 'like':
                        conditions.append(f"{key} LIKE '%{val}%'")
                    elif op == 'in':
                        conditions.append(f"{key} IN ({','.join(map(str, val))})")
            elif value is None:
                conditions.append(f"{key} IS NULL")
            elif isinstance(value, bool):
                conditions.append(f"{key} = {str(value).lower()}")
            elif isinstance(value, (int, float)):
                conditions.append(f"{key} = {value}")
            else:
                conditions.append(f"{key} = '{value}'")
        return " AND ".join(conditions)


class SupabaseProvider(SQLProvider[T]):
    """
    Supabase/PostgreSQL provider implementation.
    Uses the Supabase Python client for database operations.
    """

    def __init__(self, client):
        super().__init__()
        self._client = client

    async def create(self, table: str, data: Dict[str, Any]) -> T:
        """Create a new record using Supabase."""
        response = self._client.table(table).insert(data).execute()
        if response.data:
            return response.data[0]
        raise Exception(f"Failed to create record in {table}")

    async def get_by_id(self, table: str, id: UUID) -> Optional[T]:
        """Get a record by ID."""
        response = self._client.table(table).select(self._default_select).eq('id', str(id)).maybe_single().execute()
        return response.data if response.data else None

    async def get_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        select: Optional[str] = None
    ) -> List[T]:
        """Get all records with optional filtering."""
        query = self._client.table(table).select(select or self._default_select)

        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    for op, val in value.items():
                        if op == 'eq':
                            query = query.eq(key, val)
                        elif op == 'neq':
                            query = query.neq(key, val)
                        elif op == 'gt':
                            query = query.gt(key, val)
                        elif op == 'gte':
                            query = query.gte(key, val)
                        elif op == 'lt':
                            query = query.lt(key, val)
                        elif op == 'lte':
                            query = query.lte(key, val)
                        elif op == 'like':
                            query = query.like(key, f'%{val}%')
                        elif op == 'ilike':
                            query = query.ilike(key, f'%{val}%')
                        elif op == 'in':
                            query = query.in_(key, val)
                elif value is None:
                    query = query.is_(key, 'null')
                else:
                    query = query.eq(key, value)

        if order_by:
            if order_by.startswith('-'):
                query = query.order(order_by[1:], desc=True)
            else:
                query = query.order(order_by)

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        response = query.execute()
        return response.data or []

    async def update(self, table: str, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update a record by ID."""
        response = self._client.table(table).update(data).eq('id', str(id)).execute()
        if response.data:
            return response.data[0]
        return None

    async def delete(self, table: str, id: UUID) -> bool:
        """Delete a record by ID."""
        response = self._client.table(table).delete().eq('id', str(id)).execute()
        return bool(response.data)

    async def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records."""
        query = self._client.table(table).select('id', count='exact')

        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    for op, val in value.items():
                        if op == 'eq':
                            query = query.eq(key, val)
                        elif op == 'neq':
                            query = query.neq(key, val)
                else:
                    query = query.eq(key, value)

        response = query.execute()
        return response.count or 0

    async def execute_raw(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute raw SQL via RPC."""
        response = self._client.rpc('execute_sql', {'query': query, 'params': params or {}}).execute()
        return response.data or []

    async def health_check(self) -> bool:
        """Check database connection."""
        try:
            response = self._client.table('profiles').select('id').limit(1).execute()
            return True
        except Exception:
            return False

    async def call_rpc(self, function_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call a Supabase RPC function."""
        response = self._client.rpc(function_name, params or {}).execute()
        return response.data


class ProviderFactory:
    """
    Factory for creating database providers.
    Allows switching between different persistence strategies.
    """

    _providers: Dict[str, Type[DatabaseProvider]] = {
        'supabase': SupabaseProvider,
    }
    _instances: Dict[str, DatabaseProvider] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[DatabaseProvider]):
        """Register a new provider type."""
        cls._providers[name] = provider_class

    @classmethod
    def create_provider(cls, name: str = 'supabase', **kwargs) -> DatabaseProvider:
        """Create or retrieve a provider instance."""
        if name in cls._instances:
            return cls._instances[name]

        provider_class = cls._providers.get(name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {name}. Available: {list(cls._providers.keys())}")

        provider = provider_class(**kwargs)
        cls._instances[name] = provider
        return provider

    @classmethod
    def get_default_provider(cls) -> DatabaseProvider:
        """Get the default provider."""
        return cls.create_provider('supabase')
