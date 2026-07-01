"""Team models."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class EquipeBase(BaseModel):
    """Base equipe model."""
    nome: str = Field(..., min_length=2, max_length=255)
    descricao: Optional[str] = None
    cor: str = Field(default='#3B82F6')
    max_membros: int = Field(default=5, ge=2, le=10)


class EquipeCreate(EquipeBase):
    """Model for creating an equipe."""
    turma_id: UUID


class EquipeUpdate(BaseModel):
    """Model for updating an equipe."""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    descricao: Optional[str] = None
    cor: Optional[str] = None
    ativa: Optional[bool] = None


class EquipeResponse(IDMixin, TimestampMixin):
    """Equipe response model."""
    nome: str
    descricao: Optional[str] = None
    turma_id: UUID
    cor: str
    pontuacao: int = 0
    max_membros: int = 5
    ativa: bool = True


class EquipeMembroResponse(IDMixin):
    """Equipe membro response."""
    equipe_id: UUID
    aluno_id: UUID
    papel: str = 'membro'
    aluno_nome: Optional[str] = None
    aluno_email: Optional[str] = None
    aluno_pontos: int = 0
    entrou_em: datetime


class EquipeWithDetails(EquipeResponse):
    """Equipe with members."""
    membros: List[EquipeMembroResponse] = []
    total_membros: int = 0
    turma_nome: Optional[str] = None


class EquipeMembroCreate(BaseModel):
    """Model for adding member to team."""
    equipe_id: UUID
    aluno_id: UUID
    papel: str = Field(default='membro', pattern='^(lider|membro)$')


class TeamFormationRequest(BaseModel):
    """Request for automatic team formation."""
    turma_id: UUID
    numero_equipes: Optional[int] = None
    membros_por_equipe: int = Field(default=4, ge=2, le=6)
    criterio: str = Field(
        default='aleatorio',
        pattern='^(aleatorio|habilidade|pontuacao)$'
    )


class TeamFormationResult(BaseModel):
    """Result of team formation."""
    equipes_criadas: int
    equipes: List[EquipeWithDetails]
    alunos_sem_equipe: List[UUID] = []
