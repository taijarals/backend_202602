"""
Schemas (Pydantic Models) do módulo de Gamificação.

Este arquivo concentra todos os modelos de entrada (Request) e saída (Response)
utilizados pelos endpoints do módulo de Gamificação. Toda a lógica de negócio
e o acesso ao banco de dados (Supabase) são de responsabilidade da camada
`services`, já implementada por outro membro da equipe. Aqui validamos apenas
o contrato de dados da API (camada de apresentação).
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TipoAtividade(str, Enum):
    """Tipos de atividade que geram pontuação no sistema de gamificação."""

    DESAFIO_CONCLUIDO = "desafio_concluido"
    MINI_PROVA_APROVADA = "mini_prova_aprovada"
    FEEDBACK_ENVIADO = "feedback_enviado"
    MISSAO_CONCLUIDA = "missao_concluida"
    PARTICIPACAO_EQUIPE = "participacao_equipe"


class PontuacaoCreate(BaseModel):
    """Payload de entrada para atribuir pontos a um usuário (POST)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "uid": "a1b2c3d4-0000-1111-2222-333344445555",
                "tipo_atividade": "desafio_concluido",
            }
        }
    )

    uid: str = Field(..., min_length=1, description="ID único do usuário (UUID do Supabase Auth).")
    tipo_atividade: TipoAtividade = Field(..., description="Tipo de atividade que originou a pontuação.")


class HistoricoPontosItem(BaseModel):
    """Representa um único lançamento no histórico de pontos do usuário."""

    id: Optional[int] = Field(None, description="Identificador do registro no histórico.")
    tipo_atividade: str = Field(..., description="Tipo de atividade que gerou os pontos.")
    pontos_ganhos: int = Field(..., ge=0, description="Quantidade de pontos ganhos na atividade.")
    data_registro: datetime = Field(..., description="Data e hora em que os pontos foram concedidos.")


class PontuacaoResponse(BaseModel):
    """Retorno após a atribuição de pontos, confirmando o lançamento."""

    uid: str = Field(..., description="ID do usuário que recebeu os pontos.")
    pontos_ganhos: int = Field(..., ge=0, description="Pontos concedidos nesta atividade.")
    pontos_totais: int = Field(..., ge=0, description="Total acumulado de pontos do usuário após o lançamento.")
    mensagem: str = Field(default="Pontos atribuídos com sucesso.", description="Mensagem de confirmação.")


class HistoricoUsuarioResponse(BaseModel):
    """Histórico completo de pontuações de um usuário."""

    uid: str
    historico: List[HistoricoPontosItem] = Field(default_factory=list)


class MedalhaCreate(BaseModel):
    """Payload de entrada para criação de uma nova medalha (POST)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Mestre dos Desafios",
                "descricao": "Concedida ao concluir 10 desafios.",
                "criterio_pontos": 500,
                "icone_url": "https://exemplo.com/icones/mestre.png",
            }
        }
    )

    nome: str = Field(..., min_length=3, max_length=80, description="Nome de exibição da medalha.")
    descricao: str = Field(..., min_length=5, max_length=255, description="Descrição do critério/conquista.")
    criterio_pontos: int = Field(..., ge=0, description="Pontuação mínima necessária para conquistar a medalha.")
    icone_url: Optional[str] = Field(None, description="URL da imagem/ícone da medalha.")


class MedalhaResponse(BaseModel):
    """Representação de uma medalha retornada pela API."""

    id: int = Field(..., description="Identificador único da medalha.")
    nome: str
    descricao: str
    criterio_pontos: int
    icone_url: Optional[str] = None
    data_criacao: Optional[datetime] = None


class MedalhaUsuarioResponse(BaseModel):
    """Medalha conquistada por um usuário específico, com data de conquista."""

    medalha: MedalhaResponse
    data_conquista: datetime = Field(..., description="Data em que o usuário conquistou a medalha.")


class MedalhasUsuarioListResponse(BaseModel):
    """Lista de medalhas conquistadas por um usuário."""

    uid: str
    total_medalhas: int = Field(..., ge=0)
    medalhas: List[MedalhaUsuarioResponse] = Field(default_factory=list)


class NivelResponse(BaseModel):
    """Representa um nível do sistema de gamificação."""

    id: int
    nome: str = Field(..., description="Nome do nível (ex: 'Bronze', 'Prata', 'Ouro').")
    pontos_necessarios: int = Field(..., ge=0, description="Pontuação mínima para alcançar este nível.")


class PerfilGamificacaoResponse(BaseModel):
    """Perfil de gamificação consolidado de um usuário (pontos, nível e progresso)."""

    uid: str
    nome_usuario: Optional[str] = Field(None, description="Nome de exibição do usuário, se disponível.")
    pontos_totais: int = Field(..., ge=0)
    nivel_atual: NivelResponse
    proximo_nivel: Optional[NivelResponse] = Field(None, description="Próximo nível a ser alcançado, se houver.")
    pontos_para_proximo_nivel: Optional[int] = Field(
        None, ge=0, description="Quantos pontos faltam para o próximo nível."
    )
    total_medalhas: int = Field(0, ge=0)


class RankingItem(BaseModel):
    """Uma posição (linha) no ranking geral de pontuação."""

    posicao: int = Field(..., ge=1, description="Posição do usuário no ranking.")
    uid: str
    nome_usuario: Optional[str] = None
    pontos_totais: int = Field(..., ge=0)
    nivel_atual: Optional[str] = Field(None, description="Nome do nível atual do usuário.")


class RankingResponse(BaseModel):
    """Lista do ranking geral (Top N), ordenada por pontuação decrescente."""

    total_exibido: int = Field(..., ge=0)
    ranking: List[RankingItem] = Field(default_factory=list)

class ErrorResponse(BaseModel):
    """Modelo padrão de resposta de erro da API."""

    detail: str = Field(..., description="Mensagem descritiva do erro ocorrido.")


from fastapi import APIRouter, HTTPException
import uuid


from services import (
    inserir_pontos,
    buscar_top_ranking
)


router = APIRouter(prefix="/gamificacao", tags=["Gamificação"])

@router.post("/pontos", summary="Atribuir pontos a um usuário")
def dar_pontos(payload: PontuacaoCreate):
    try:
        
        user_id = uuid.UUID(payload.uid)
        
        
        resultado = inserir_pontos(user_id, payload.tipo_atividade)
        
        return {"status": "sucesso", "mensagem": "Pontos inseridos no banco!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao inserir pontos: {str(e)}")

@router.get("/ranking", summary="Ver o Ranking Global")
def ver_ranking():
    try:
        
        ranking = buscar_top_ranking()
        return {"status": "sucesso", "ranking": ranking}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking: {str(e)}")