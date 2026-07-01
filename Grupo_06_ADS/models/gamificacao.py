"""Gamification models."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class PontuacaoCreate(BaseModel):
    """Model for creating a pontuacao."""
    aluno_id: UUID
    turma_id: Optional[UUID] = None
    disciplina_id: Optional[UUID] = None
    pontos: int = Field(..., ge=0)
    fonte: Optional[str] = None
    referencia_id: Optional[UUID] = None
    descricao: Optional[str] = None


class PontuacaoResponse(IDMixin):
    """Pontuacao response model."""
    aluno_id: UUID
    turma_id: Optional[UUID] = None
    disciplina_id: Optional[UUID] = None
    pontos: int
    fonte: Optional[str] = None
    referencia_id: Optional[UUID] = None
    descricao: Optional[str] = None
    created_at: datetime


class MedalhaBase(BaseModel):
    """Base medalha model."""
    nome: str = Field(..., min_length=2, max_length=255)
    descricao: str = Field(..., min_length=5)
    icone: str = Field(default='medal')
    cor: str = Field(default='#FFD700')
    tipo: str = Field(
        default='pontos',
        pattern='^(pontos|desafios|provas|missoes|especial)$'
    )
    nivel: int = Field(default=1, ge=1)
    pontos_requeridos: Optional[int] = None


class MedalhaCreate(MedalhaBase):
    """Model for creating a medalha."""
    pass


class MedalhaResponse(IDMixin):
    """Medalha response model."""
    nome: str
    descricao: str
    icone: str
    cor: str
    tipo: str
    nivel: int
    pontos_requeridos: Optional[int] = None
    ativa: bool = True
    created_at: datetime


class ConquistaResponse(IDMixin):
    """Conquista response model."""
    aluno_id: UUID
    medalha_id: UUID
    medalha: Optional[MedalhaResponse] = None
    conquistada_em: datetime


class NivelResponse(IDMixin):
    """Nivel response model."""
    nivel: int
    nome: str
    pontos_necessarios: int
    titulo: Optional[str] = None
    recompensa: Optional[str] = None


class NivelProgress(BaseModel):
    """User level progress."""
    nivel_atual: int
    nivel_nome: str
    pontos_atuais: int
    pontos_proximo_nivel: int
    progresso_percentual: float
    proximo_nivel: Optional[NivelResponse] = None


class UserGamificationStats(BaseModel):
    """Complete gamification stats for user."""
    pontos_totais: int = 0
    nivel_atual: NivelProgress
    medalhas: List[ConquistaResponse] = []
    ranking_posicao: Optional[int] = None
    desafios_completados: int = 0
    provas_completadas: int = 0
    missoes_completadas: int = 0
    sequencia_dias: int = 0


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    posicao: int
    aluno_id: UUID
    aluno_nome: str
    pontos: int
    nivel: int
    medalhas: int
