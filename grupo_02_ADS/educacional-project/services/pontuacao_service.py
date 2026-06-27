from repositories.pontuacao_repository import PontuacaoRepository

class PontuacaoService:

    def __init__(self):
        self.repo = PontuacaoRepository()

    def registrar(self, aluno_id, pontos):

        self.repo.registrar(
            aluno_id,
            pontos
        )

    def ranking(self):

        return self.repo.ranking()