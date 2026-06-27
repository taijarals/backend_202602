from repositories.submissao_repository import (
    SubmissaoRepository
)

class SubmissaoService:

    def __init__(self):
        self.repo = SubmissaoRepository()

    def criar(
        self,
        aluno_id,
        desafio_id,
        resposta
    ):

        self.repo.criar(
            aluno_id,
            desafio_id,
            resposta
        )