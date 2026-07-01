"""Disciplina (Subject) models."""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class DisciplinaBase(BaseModel):
    """Base disciplina model."""
    nome: str = Field(..., min_length=2, max_length=255)
    descricao: Optional[str] = None
    codigo: Optional[str] = Field(None, max_length=50)
    cor: str = Field(default='#3B82F6', max_length=20)


class DisciplinaCreate(DisciplinaBase):
    """Model for creating a disciplina."""
    professor_id: UUID


class DisciplinaUpdate(BaseModel):
    """Model for updating a disciplina."""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    descricao: Optional[str] = None
    codigo: Optional[str] = None
    cor: Optional[str] = None
    ativa: Optional[bool] = None


class DisciplinaResponse(IDMixin, TimestampMixin):
    """Disciplina response model."""
    nome: str
    descricao: Optional[str] = None
    codigo: Optional[str] = None
    cor: str
    professor_id: UUID
    ativa: bool = True


class DisciplinaWithDetails(DisciplinaResponse):
    """Disciplina with additional details."""
    professor_nome: Optional[str] = None
    total_turmas: int = 0
    total_alunos: int = 0
    total_desafios: int = 0
