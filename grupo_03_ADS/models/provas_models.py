from pydantic import BaseModel, Field
from typing import List, Optional


class CadastroProva(BaseModel):
    titulo: str = Field(..., min_length=3)
    descricao: Optional[str] = None
    professor_id: int = Field(..., gt=0)
    disciplina_id: int = Field(..., gt=0)
    duracao_minutos: int = Field(10, gt=0)
    pontos_por_questao: int = Field(10, gt=0)
    ativa: bool = True


class CadastroQuestaoProva(BaseModel):
    prova_id: int = Field(..., gt=0)
    enunciado: str = Field(..., min_length=5)
    alternativa_a: str = Field(..., min_length=1)
    alternativa_b: str = Field(..., min_length=1)
    alternativa_c: str = Field(..., min_length=1)
    alternativa_d: str = Field(..., min_length=1)
    resposta_correta: str = Field(..., min_length=1, max_length=1)
    ordem: int = Field(1, gt=0)


class RespostaQuestaoProva(BaseModel):
    questao_id: int = Field(..., gt=0)
    resposta: str = Field(..., min_length=1, max_length=1)


class EnviarRespostasProva(BaseModel):
    aluno_id: int = Field(..., gt=0)
    prova_id: int = Field(..., gt=0)
    respostas: List[RespostaQuestaoProva]