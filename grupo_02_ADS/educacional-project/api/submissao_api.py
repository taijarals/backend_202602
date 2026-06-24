from fastapi import APIRouter

from models.submissao import Submissao
from services.submissao_service import (
    SubmissaoService
)

router = APIRouter()

service = SubmissaoService()

@router.post("/submissoes")
def criar(submissao: Submissao):

    service.criar(
        submissao.aluno_id,
        submissao.desafio_id,
        submissao.resposta
    )

    return {
        "mensagem": "Resposta enviada"
    }