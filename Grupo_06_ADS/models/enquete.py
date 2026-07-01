"""Poll/Feedback models."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class OpcaoEnqueteBase(BaseModel):
    """Base opcao enquete model."""
    texto: str = Field(..., min_length=1, max_length=500)
    ordem: int = Field(default=0, ge=0)


class OpcaoEnqueteCreate(OpcaoEnqueteBase):
    """Model for creating an opcao."""
    enquete_id: UUID


class OpcaoEnqueteResponse(IDMixin):
    """Opcao enquete response model."""
    enquete_id: UUID
    texto: str
    ordem: int
    votos: int = 0
    created_at: datetime


class EnqueteBase(BaseModel):
    """Base enquete model."""
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: Optional[str] = None
    multipla_escolha: bool = False
    anonima: bool = False
    fim: Optional[datetime] = None


class EnqueteCreate(EnqueteBase):
    """Model for creating an enquete."""
    professor_id: UUID
    turma_id: Optional[UUID] = None
   opcoes: List[str] = Field(..., min_items=2, max_items=10)


class EnqueteUpdate(BaseModel):
    """Model for updating an enquete."""
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    ativa: Optional[bool] = None
    fim: Optional[datetime] = None


class EnqueteResponse(IDMixin):
    """Enquete response model."""
    titulo: str
    descricao: Optional[str] = None
    professor_id: UUID
    turma_id: Optional[UUID] = None
    multipla_escolha: bool
    anonima: bool
    ativa: bool = True
    fim: Optional[datetime] = None
    created_at: datetime


class EnqueteWithOpcoes(EnqueteResponse):
    """Enquete with options and results."""
    opcoes: List[OpcaoEnqueteResponse] = []
    total_votos: int = 0
    professor_nome: Optional[str] = None
    turma_nome: Optional[str] = None


class VotoEnqueteCreate(BaseModel):
    """Model for creating a poll vote."""
    enquete_id: UUID
    opcao_id: UUID
    aluno_id: UUID


class VotoEnqueteResponse(IDMixin):
    """Voto enquete response model."""
    enquete_id: UUID
    opcao_id: UUID
    aluno_id: UUID
    created_at: datetime


class EnqueteStats(BaseModel):
    """Enquete statistics."""
    enquete_id: UUID
    total_votos: int
    participacao_percentual: float
   opcoes_stats: List[dict]
