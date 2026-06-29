"""
Refatoranção parcial, alterei alguns imports, tem um serio problmea de reconhecimento antes.
Cuidado quando passar, precisa primeiro ser testado.
alterei formato de envio, antes era independente, agora passa de uma coisa para outra diretamente.
(Carol)
"""

"""
Modelos utilizados na aplicação.

Todos os modelos abaixo representam tanto os dados
utilizados pelo sistema quanto os registros do banco.
"""

from uuid import UUID
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ======================================
# ALTERNATIVA
# ======================================

class Alternativa(BaseModel):
    """
    Representa uma alternativa de uma questão.
    """

    id: UUID

    questao_id: UUID

    texto: str

    ordem: int

    correta: bool


# ======================================
# QUESTÃO
# ======================================

class Questao(BaseModel):
    """
    Representa uma questão da prova.
    """

    id: UUID

    prova_id: UUID

    enunciado: str

    ordem: int

    peso: float = 1.0

    alternativas: List[Alternativa] = []


# ======================================
# PROVA
# ======================================

class Prova(BaseModel):
    """
    Representa uma prova completa.
    """

    id: UUID

    titulo: str

    descricao: Optional[str] = None

    tempo_limite: int = 300

    nota_maxima: float = 10.0

    questoes: List[Questao] = []


# ======================================
# TENTATIVA
# ======================================

class Tentativa(BaseModel):
    """
    Representa uma tentativa do usuário.
    """

    id: Optional[UUID] = None

    usuario_id: UUID

    prova_id: UUID

    iniciado_em: Optional[datetime] = None

    finalizado_em: Optional[datetime] = None

    nota: Optional[float] = None

    dentro_do_prazo: bool = True

    status: str = "EM_ANDAMENTO"


# ======================================
# RESPOSTA
# ======================================

class Resposta(BaseModel):
    """
    Representa a resposta de uma questão.
    """

    tentativa_id: UUID

    questao_id: UUID

    alternativa_escolhida: int

    acertou: Optional[bool] = None


# ======================================
# DTO FINALIZAR PROVA
# ======================================

class EntregaProva(BaseModel):
    """
    Dados enviados pelo frontend
    quando o aluno finaliza a prova.
    """

    tentativa_id: UUID

    respostas: dict[UUID, int]