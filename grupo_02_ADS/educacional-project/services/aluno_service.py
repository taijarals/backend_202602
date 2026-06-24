from repositories.aluno_repository import AlunoRepository

class AlunoService:

    def __init__(self):
        self.repo = AlunoRepository()

    def listar(self):
        return self.repo.listar()

    def criar(self, nome):
        self.repo.criar(nome)