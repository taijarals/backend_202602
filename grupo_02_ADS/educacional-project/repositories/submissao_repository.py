from providers.sqlite_provider import SQLiteProvider

class SubmissaoRepository:

    def __init__(self):
        self.provider = SQLiteProvider()

    def criar(
        self,
        aluno_id,
        desafio_id,
        resposta
    ):

        self.provider.criar_submissao(
            aluno_id,
            desafio_id,
            resposta
        )