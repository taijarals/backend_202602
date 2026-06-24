from repositories.desafio_repository import DesafioRepository

class DesafioService:

    def __init__(self):
        self.repo = DesafioRepository()

    def listar(self):
        return self.repo.listar()

    def criar(self, titulo, pontos):
        self.repo.criar(
            titulo,
            pontos
        )