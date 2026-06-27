from pydantic import BaseModel

class Pontuacao(BaseModel):
    aluno_id: int
    pontos: int