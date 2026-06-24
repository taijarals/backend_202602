from fastapi import APIRouter

from services.aluno_service import AlunoService
from models.aluno import Aluno

router = APIRouter()

service = AlunoService()

@router.get("/alunos")
def listar():

    return service.listar()

@router.post("/alunos")
def criar(aluno: Aluno):

    service.criar(aluno.nome)

    return {
        "mensagem": "Aluno criado"
    }