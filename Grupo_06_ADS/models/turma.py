"""Turma (Class) models."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class TurmaBase(BaseModel):
    """Base turma model."""
    nome: str = Field(..., min_length=2, max_length=255)
    descricao: Optional[str] = None
    ano: Optional[int] = None
    semestre: Optional[int] = None


class TurmaCreate(TurmaBase):
    """Model for creating a turma."""
    disciplina_id: UUID
    professor_id: UUID
    codigo_convite: Optional[str] = Field(None, max_length=20)


class TurmaUpdate(BaseModel):
    """Model for updating a turma."""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    descricao: Optional[str] = None
    codigo_convite: Optional[str] = None
    ativa: Optional[bool] = None


class TurmaResponse(IDMixin, TimestampMixin):
    """Turma response model."""
    nome: str
    descricao: Optional[str] = None
    disciplina_id: UUID
    professor_id: UUID
    codigo_convite: Optional[str] = None
    ano: Optional[int] = None
    semestre: Optional[int] = None
    ativa: bool = True


class TurmaWithDetails(TurmaResponse):
    """Turma with additional details."""
    disciplina_nome: Optional[str] = None
    professor_nome: Optional[str] = None
    total_alunos: int = 0
    total_desafios: int = 0


class TurmaAlunoCreate(BaseModel):
    """Model for enrolling student in turma."""
    turma_id: UUID
    aluno_id: UUID


class TurmaAlunoResponse(IDMixin):
    """Turma aluno response."""
    turma_id: UUID
    aluno_id: UUID
    aluno_nome: Optional[str] = None
    aluno_email: Optional[str] = None
    entrou_em: datetime
