from pydantic import BaseModel

class Submissao(BaseModel):
    aluno_id: int
    desafio_id: int
    resposta: str