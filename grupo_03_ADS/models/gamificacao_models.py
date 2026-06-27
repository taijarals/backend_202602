from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class RegistroPontuacao(BaseModel):
    aluno_id: int = Field(..., gt=0)
    atividade: str = Field(..., min_length=3)
    pontos_ganhos: int = Field(..., gt=0)


class CadastroAluno(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr


class CadastroProfessor(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr


class CadastroDisciplina(BaseModel):
    nome: str = Field(..., min_length=3)
    descricao: Optional[str] = None


class CadastroTurma(BaseModel):
    nome: str = Field(..., min_length=2)
    professor_id: int = Field(..., gt=0)
    disciplina_id: int = Field(..., gt=0)


class VincularAlunoTurma(BaseModel):
    turma_id: int = Field(..., gt=0)
    aluno_id: int = Field(..., gt=0)


class RankingItem(BaseModel):
    posicao: int
    aluno_id: int
    nome: str
    pontos: int
    nivel: int


class RespostaPontuacao(BaseModel):
    sucesso: bool
    mensagem: str
    pontos_finais: int
    nivel_atualizado: int
    subiu_de_nivel: bool
    medalhas_desbloqueadas: List[str]