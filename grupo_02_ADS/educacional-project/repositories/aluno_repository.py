from providers.sqlite_provider import SQLiteProvider

class AlunoRepository:

    def __init__(self):
        self.provider = SQLiteProvider()

    def listar(self):
        return self.provider.listar_alunos()

    def criar(self, nome):
        self.provider.criar_aluno(nome)