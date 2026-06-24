from providers.sqlite_provider import SQLiteProvider

class PontuacaoRepository:

    def __init__(self):
        self.provider = SQLiteProvider()

    def registrar(self, aluno_id, pontos):

        self.provider.registrar_pontuacao(
            aluno_id,
            pontos
        )

    def ranking(self):

        return self.provider.obter_ranking()