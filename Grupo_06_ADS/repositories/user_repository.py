"""
User repository implementation.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from models.user import UserCreate, UserUpdate, UserResponse, UserStats
from .base import BaseRepository


class UserRepository(BaseRepository[UserResponse]):
    """Repository for user operations."""

    def __init__(self):
        super().__init__('profiles', UserResponse)

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserResponse]:
        """Get profile by auth user ID."""
        return await self.get_one({'user_id': str(user_id)})

    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        return await self.get_one({'email': email})

    async def get_professors(self) -> List[UserResponse]:
        """Get all professors."""
        return await self.get_all(filters={'role': 'professor'})

    async def get_students(self) -> List[UserResponse]:
        """Get all students."""
        return await self.get_all(filters={'role': 'student'})

    async def get_ranking(self, limit: int = 10) -> List[UserResponse]:
        """Get users ranked by points."""
        return await self.get_all(
            filters={'role': 'student'},
            order_by='-pontuacao_total',
            limit=limit
        )

    async def update_points(self, id: UUID, points: int) -> Optional[UserResponse]:
        """Update user's total points."""
        user = await self.get_by_id(id)
        if user:
            new_total = user.pontuacao_total + points
            return await self.update(id, {'pontuacao_total': new_total})
        return None

    async def get_stats(self, id: UUID) -> Dict[str, Any]:
        """Get user statistics."""
        results = await self.db.call_rpc('get_user_stats', {'user_id': str(id)})
        return results or {}

    async def search(self, query: str, role: Optional[str] = None) -> List[UserResponse]:
        """Search users by name or email."""
        filters = {}
        if role:
            filters['role'] = role
        # Use ilike for case-insensitive search
        results = await self.db.get_all(
            self.table,
            filters=filters,
            select='*,nome.ilike.%{},email.ilike.%{}'.format(query, query)
        )
        return [self.model.model_validate(r) for r in results if r]


class AuthRepository:
    """Repository for authentication operations."""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            from database import get_db
            self._db = get_db()
        return self._db

    async def sign_up(self, email: str, password: str, nome: str, role: str = 'student') -> Dict[str, Any]:
        """Sign up a new user."""
        response = self._db.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'nome': nome,
                    'role': role
                }
            }
        })
        return response.model_dump() if response else {}

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user."""
        response = self._db.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        return response.model_dump() if response else {}

    async def sign_out(self) -> bool:
        """Sign out current user."""
        try:
            self._db.auth.sign_out()
            return True
        except Exception:
            return False

    async def get_session(self) -> Optional[Dict[str, Any]]:
        """Get current session."""
        session = self._db.auth.get_session()
        return session.model_dump() if session else None

    async def refresh_session(self) -> Optional[Dict[str, Any]]:
        """Refresh session token."""
        session = self._db.auth.refresh_session()
        return session.model_dump() if session else None
