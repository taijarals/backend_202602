"""Mission models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class MissaoEtapaBase(BaseModel):
    """Base missao etapa model."""
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: str = Field(..., min_length=5)
    ordem: int = Field(default=0, ge=0)
    pontos: int = Field(default=50, ge=0)
    tipo: str = Field(
        default='tarefa',
        pattern='^(tarefa|quiz|projeto|pesquisa)$'
    )
    requisitos: Optional[Dict[str, Any]] = None


class MissaoEtapaCreate(MissaoEtapaBase):
    """Model for creating a missao etapa."""
    missao_id: UUID


class MissaoEtapaResponse(IDMixin):
    """Missao etapa response model."""
    missao_id: UUID
    titulo: str
    descricao: str
    ordem: int
    pontos: int
    tipo: str
    requisitos: Optional[Dict[str, Any]] = None
    created_at: datetime


class MissaoBase(BaseModel):
    """Base missao model."""
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: str = Field(..., min_length=10)
    pontos_recompensa: int = Field(default=500, ge=0)
    nivel_dificuldade: int = Field(default=1, ge=1, le=5)
    pre_requisitos: Optional[List[UUID]] = None


class MissaoCreate(MissaoBase):
    """Model for creating a missao."""
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID
    etapas: List[MissaoEtapaBase] = []


class MissaoUpdate(BaseModel):
    """Model for updating a missao."""
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = Field(None, min_length=10)
    pontos_recompensa: Optional[int] = Field(None, ge=0)
    nivel_dificuldade: Optional[int] = Field(None, ge=1, le=5)
    pre_requisitos: Optional[List[UUID]] = None
    ativa: Optional[bool] = None


class MissaoResponse(IDMixin, TimestampMixin):
    """Missao response model."""
    titulo: str
    descricao: str
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID
    pontos_recompensa: int
    nivel_dificuldade: int
    pre_requisitos: Optional[List[UUID]] = None
    ativa: bool = True


class MissaoWithEtapas(MissaoResponse):
    """Missao with etapas."""
    etapas: List[MissaoEtapaResponse] = []
    disciplina_nome: Optional[str] = None
    turma_nome: Optional[str] = None
    total_etapas: int = 0


class MissaoProgress(MissaoWithEtapas):
    """Missao with user progress."""
    progresso_atual: int = 0
    status: str = 'nao_iniciada'
    pontos_obtidos: int = 0
    etapas_completas: int = 0


class ProgressoEtapaCreate(BaseModel):
    """Model for creating/updating progresso."""
    missao_id: UUID
    etapa_id: UUID
    aluno_id: UUID
    status: str = Field(
        default='em_progresso',
        pattern='^(pendente|em_progresso|completa|falhou)$'
    )
    pontos_obtidos: int = Field(default=0, ge=0)


class ProgressoEtapaResponse(IDMixin):
    """Progresso etapa response model."""
    missao_id: UUID
    etapa_id: UUID
    aluno_id: UUID
    status: str
    pontos_obtidos: int
    completada_em: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserMissionStats(BaseModel):
    """User mission statistics."""
    missoes_iniciadas: int = 0
    missoes_completadas: int = 0
    pontos_totais: int = 0
    taxa_conclusao: float = 0.0
