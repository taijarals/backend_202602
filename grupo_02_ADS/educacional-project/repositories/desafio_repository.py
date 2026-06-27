from providers.sqlite_provider import SQLiteProvider

class DesafioRepository:

    def __init__(self):
        self.provider = SQLiteProvider()

    def listar(self):
        return self.provider.listar_desafios()

    def criar(self, titulo, pontos):
        self.provider.criar_desafio(
            titulo,
            pontos
        )