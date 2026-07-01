"""
Authentication service implementation.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse, AuthUser
from repositories import UserRepository, AuthRepository
from database import settings


class AuthService:
    """Service for authentication operations."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.auth_repo = AuthRepository()
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def _hash_password(self, password: str) -> str:
        """Hash password."""
        return self.pwd_context.hash(password)

    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def register(self, user_data: UserCreate) -> TokenResponse:
        """Register new user."""
        # Check if user exists
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email already registered'
            )

        # Create auth user
        auth_result = await self.auth_repo.sign_up(
            email=user_data.email,
            password=user_data.password,
            nome=user_data.nome,
            role=user_data.role
        )

        if not auth_result.get('user'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed to create user account'
            )

        user_id = auth_result['user']['id']

        # Create profile
        profile_data = {
            'user_id': user_id,
            'nome': user_data.nome,
            'email': user_data.email,
            'role': user_data.role,
            'avatar_url': user_data.avatar_url,
            'bio': user_data.bio
        }
        profile = await self.user_repo.create(profile_data)

        # Create token
        access_token = self._create_access_token(
            {'sub': str(user_id), 'email': user_data.email, 'role': user_data.role}
        )

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.model_validate(profile)
        )

    async def login(self, credentials: UserLogin) -> TokenResponse:
        """Login user."""
        # Authenticate with Supabase
        auth_result = await self.auth_repo.sign_in(
            email=credentials.email,
            password=credentials.password
        )

        if not auth_result.get('user'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid credentials'
            )

        user_id = auth_result['user']['id']

        # Get profile
        profile = await self.user_repo.get_by_user_id(UUID(user_id))
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User profile not found'
            )

        # Create token
        access_token = auth_result.get('session', {}).get('access_token') or self._create_access_token(
            {'sub': user_id, 'email': profile.email, 'role': profile.role}
        )

        return TokenResponse(
            access_token=access_token,
            user=profile
        )

    async def logout(self) -> bool:
        """Logout user."""
        return await self.auth_repo.sign_out()

    async def get_current_user(self, user_id: UUID) -> Optional[AuthUser]:
        """Get current authenticated user."""
        profile = await self.user_repo.get_by_user_id(user_id)
        if profile:
            return AuthUser(
                id=profile.id,
                email=profile.email,
                nome=profile.nome,
                role=profile.role,
                pontuacao_total=profile.pontuacao_total,
                nivel=profile.nivel
            )
        return None

    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None

    async def refresh_session(self) -> Optional[Dict[str, Any]]:
        """Refresh user session."""
        return await self.auth_repo.refresh_session()
