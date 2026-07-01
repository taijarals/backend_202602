"""User-related models."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
from .base import TimestampMixin, IDMixin


class UserBase(BaseModel):
    """Base user model."""
    nome: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    role: str = Field(default='student', pattern='^(student|professor|admin)$')


class UserCreate(UserBase):
    """Model for creating a user."""
    password: str = Field(..., min_length=6)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """Model for updating a user."""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    pontuacao_total: Optional[int] = None
    nivel: Optional[int] = None


class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str


class UserResponse(IDMixin, TimestampMixin):
    """User response model."""
    user_id: Optional[UUID] = None
    nome: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    pontuacao_total: int = 0
    nivel: int = 1


class UserStats(BaseModel):
    """User statistics."""
    total_pontos: int = 0
    nivel_atual: int = 1
    desafios_completados: int = 0
    provas_realizadas: int = 0
    missoes_completadas: int = 0
    medalhas_conquistadas: int = 0
    ranking_geral: Optional[int] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthUser(BaseModel):
    """Authenticated user model."""
    id: UUID
    email: str
    nome: str
    role: str
    pontuacao_total: int = 0
    nivel: int = 1
