from fastapi import APIRouter

from services.desafio_service import DesafioService
from models.desafio import Desafio

router = APIRouter()

service = DesafioService()

@router.get("/desafios")
def listar():

    return service.listar()

@router.post("/desafios")
def criar(desafio: Desafio):

    service.criar(
        desafio.titulo,
        desafio.pontos
    )

    return {
        "mensagem": "Desafio criado"
    }