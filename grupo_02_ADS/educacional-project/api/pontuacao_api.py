from fastapi import APIRouter

from models.pontuacao import Pontuacao
from services.pontuacao_service import PontuacaoService

router = APIRouter()

service = PontuacaoService()

@router.post("/pontuacao")
def registrar(pontuacao: Pontuacao):

    service.registrar(
        pontuacao.aluno_id,
        pontuacao.pontos
    )

    return {
        "mensagem": "Pontuação registrada"
    }

@router.get("/ranking")
def ranking():

    return service.ranking()