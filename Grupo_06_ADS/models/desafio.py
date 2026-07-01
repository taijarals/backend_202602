"""Desafio (Challenge) models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class DesafioBase(BaseModel):
    """Base desafio model."""
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: str = Field(..., min_length=10)
    pontos_recompensa: int = Field(default=100, ge=0)
    dificuldade: str = Field(
        default='media',
        pattern='^(facil|media|dificil|expert)$'
    )
    tipo: str = Field(
        default='codigo',
        pattern='^(codigo|quiz|projeto|pesquisa|outro)$'
    )
    prazo: Optional[datetime] = None
    restricoes: Optional[Dict[str, Any]] = None


class DesafioCreate(DesafioBase):
    """Model for creating a desafio."""
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID


class DesafioUpdate(BaseModel):
    """Model for updating a desafio."""
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = Field(None, min_length=10)
    pontos_recompensa: Optional[int] = Field(None, ge=0)
    dificuldade: Optional[str] = None
    tipo: Optional[str] = None
    prazo: Optional[datetime] = None
    restricoes: Optional[Dict[str, Any]] = None
    ativo: Optional[bool] = None


class DesafioResponse(IDMixin, TimestampMixin):
    """Desafio response model."""
    titulo: str
    descricao: str
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID
    pontos_recompensa: int
    dificuldade: str
    tipo: str
    prazo: Optional[datetime] = None
    restricoes: Optional[Dict[str, Any]] = None
    ativo: bool = True


class DesafioWithDetails(DesafioResponse):
    """Desafio with additional details."""
    disciplina_nome: Optional[str] = None
    turma_nome: Optional[str] = None
    professor_nome: Optional[str] = None
    total_submissoes: int = 0
    meu_status: Optional[str] = None


class SubmissaoBase(BaseModel):
    """Base submissao model."""
    conteudo: str = Field(..., min_length=1)
    anexos: Optional[Dict[str, Any]] = None


class SubmissaoCreate(SubmissaoBase):
    """Model for creating a submissao."""
    desafio_id: UUID
    aluno_id: UUID


class SubmissaoUpdate(BaseModel):
    """Model for updating submissao status."""
    status: Optional[str] = None
    pontos_obtidos: Optional[int] = None
    feedback_professor: Optional[str] = None


class SubmissaoResponse(IDMixin, TimestampMixin):
    """Submissao response model."""
    desafio_id: UUID
    aluno_id: UUID
    conteudo: str
    anexos: Optional[Dict[str, Any]] = None
    pontos_obtidos: int = 0
    feedback_professor: Optional[str] = None
    status: str = 'pendente'
    votos: int = 0


class SubmissaoWithDetails(SubmissaoResponse):
    """Submissao with additional details."""
    desafio_titulo: Optional[str] = None
    aluno_nome: Optional[str] = None
    aluno_email: Optional[str] = None


class VotoCreate(BaseModel):
    """Model for creating a vote."""
    submissao_id: UUID
    aluno_id: UUID
    pontuacao: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None


class VotoResponse(IDMixin):
    """Voto response model."""
    submissao_id: UUID
    aluno_id: UUID
    pontuacao: int
    comentario: Optional[str] = None
    created_at: datetime


class RankingEntry(BaseModel):
    """Ranking entry model."""
    posicao: int
    aluno_id: UUID
    aluno_nome: str
    pontos: int
    desafios_completados: int
