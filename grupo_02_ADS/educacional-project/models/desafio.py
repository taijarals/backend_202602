from pydantic import BaseModel

class Desafio(BaseModel):
    titulo: str
    pontos: int