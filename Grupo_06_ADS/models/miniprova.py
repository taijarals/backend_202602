"""Mini Prova (Quick Test) models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from .base import TimestampMixin, IDMixin


class QuestaoBase(BaseModel):
    """Base questao model."""
    enunciado: str = Field(..., min_length=5)
    tipo: str = Field(
        default='multipla_escolha',
        pattern='^(multipla_escolha|verdadeiro_falso|resposta_curta|codigo)$'
    )
    opcoes: Optional[Dict[str, Any]] = None
    resposta_correta: str
    pontos: int = Field(default=10, ge=1)
    ordem: int = Field(default=0, ge=0)


class QuestaoCreate(QuestaoBase):
    """Model for creating a questao."""
    mini_prova_id: UUID


class QuestaoResponse(IDMixin):
    """Questao response model."""
    mini_prova_id: UUID
    enunciado: str
    tipo: str
   opcoes: Optional[Dict[str, Any]] = None
    resposta_correta: str
    pontos: int
    ordem: int
    created_at: datetime


class QuestaoForStudent(BaseModel):
    """Questao without correct answer for students."""
    id: UUID
    enunciado: str
    tipo: str
    opcoes: Optional[Dict[str, Any]] = None
    pontos: int
    ordem: int


class MiniProvaBase(BaseModel):
    """Base mini prova model."""
    titulo: str = Field(..., min_length=3, max_length=255)
    descricao: Optional[str] = None
    duracao_minutos: int = Field(default=30, ge=5, le=180)
    tentativas_permitidas: int = Field(default=1, ge=1)
    pontos_maximos: int = Field(default=100, ge=1)
    aleatorizar_questoes: bool = False
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None


class MiniProvaCreate(MiniProvaBase):
    """Model for creating a mini prova."""
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID
    questoes: List[QuestaoBase] = []


class MiniProvaUpdate(BaseModel):
    """Model for updating a mini prova."""
    titulo: Optional[str] = Field(None, min_length=3, max_length=255)
    descricao: Optional[str] = None
    duracao_minutos: Optional[int] = Field(None, ge=5, le=180)
    tentativas_permitidas: Optional[int] = Field(None, ge=1)
    pontos_maximos: Optional[int] = Field(None, ge=1)
    aleatorizar_questoes: Optional[bool] = None
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None
    ativa: Optional[bool] = None


class MiniProvaResponse(IDMixin, TimestampMixin):
    """Mini prova response model."""
    titulo: str
    descricao: Optional[str] = None
    disciplina_id: Optional[UUID] = None
    turma_id: Optional[UUID] = None
    professor_id: UUID
    duracao_minutos: int
    tentativas_permitidas: int
    pontos_maximos: int
    aleatorizar_questoes: bool
    inicio: Optional[datetime] = None
    fim: Optional[datetime] = None
    ativa: bool = True


class MiniProvaWithQuestoes(MiniProvaResponse):
    """Mini prova with questoes."""
    questoes: List[QuestaoResponse] = []
    disciplina_nome: Optional[str] = None
    turma_nome: Optional[str] = None


class MiniProvaForStudent(MiniProvaResponse):
    """Mini prova for student view."""
    questoes: List[QuestaoForStudent] = []
    tentativas_realizadas: int = 0


class RespostaCreate(BaseModel):
    """Model for creating a resposta."""
    questao_id: UUID
    resposta: str


class TentativaCreate(BaseModel):
    """Model for starting a tentativa."""
    mini_prova_id: UUID
    aluno_id: UUID


class TentativaUpdate(BaseModel):
    """Model for updating tentativa."""
    respostas: List[RespostaCreate]


class TentativaResponse(IDMixin):
    """Tentativa response model."""
    mini_prova_id: UUID
    aluno_id: UUID
    inicio_em: datetime
    fim_em: Optional[datetime] = None
    tempo_gasto_segundos: Optional[int] = None
    pontos_obtidos: int = 0
    aprovada: Optional[bool] = None
    status: str = 'em_andamento'


class TentativaWithDetails(TentativaResponse):
    """Tentativa with respostas."""
    respostas: List[Dict[str, Any]] = []
    mini_prova_titulo: Optional[str] = None
