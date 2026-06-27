from providers.factory import ProviderFactory


class ProvasRepository:

    def __init__(self):
        self.db = ProviderFactory.create()

    def cadastrar_prova(
        self,
        titulo: str,
        descricao: str,
        professor_id: int,
        disciplina_id: int,
        duracao_minutos: int,
        pontos_por_questao: int,
        ativa: bool
    ):
        q = """
        INSERT INTO provas
        (
            titulo,
            descricao,
            professor_id,
            disciplina_id,
            duracao_minutos,
            pontos_por_questao,
            ativa
        )
        VALUES
        (
            %(titulo)s,
            %(descricao)s,
            %(professor_id)s,
            %(disciplina_id)s,
            %(duracao_minutos)s,
            %(pontos_por_questao)s,
            %(ativa)s
        )
        RETURNING
            id,
            titulo,
            descricao,
            professor_id,
            disciplina_id,
            duracao_minutos,
            pontos_por_questao,
            ativa,
            data_criacao
        """

        return self.db.fetch_one(
            q,
            {
                "titulo": titulo,
                "descricao": descricao,
                "professor_id": professor_id,
                "disciplina_id": disciplina_id,
                "duracao_minutos": duracao_minutos,
                "pontos_por_questao": pontos_por_questao,
                "ativa": ativa
            }
        )

    def listar_provas(self):
        q = """
        SELECT
            p.id,
            p.titulo,
            p.descricao,
            p.professor_id,
            prof.nome AS professor,
            p.disciplina_id,
            d.nome AS disciplina,
            p.duracao_minutos,
            p.pontos_por_questao,
            p.ativa,
            p.data_criacao,
            COUNT(qp.id) AS total_questoes
        FROM provas p
        LEFT JOIN professores prof
            ON p.professor_id = prof.id
        LEFT JOIN disciplinas d
            ON p.disciplina_id = d.id
        LEFT JOIN questoes_prova qp
            ON p.id = qp.prova_id
        GROUP BY
            p.id,
            p.titulo,
            p.descricao,
            p.professor_id,
            prof.nome,
            p.disciplina_id,
            d.nome,
            p.duracao_minutos,
            p.pontos_por_questao,
            p.ativa,
            p.data_criacao
        ORDER BY p.id ASC
        """

        return self.db.fetch_all(q)

    def obter_prova(self, prova_id: int):
        q = """
        SELECT *
        FROM provas
        WHERE id = %(id)s
        """

        return self.db.fetch_one(
            q,
            {
                "id": prova_id
            }
        )

    def cadastrar_questao(
        self,
        prova_id: int,
        enunciado: str,
        alternativa_a: str,
        alternativa_b: str,
        alternativa_c: str,
        alternativa_d: str,
        resposta_correta: str,
        ordem: int
    ):
        q = """
        INSERT INTO questoes_prova
        (
            prova_id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            resposta_correta,
            ordem
        )
        VALUES
        (
            %(prova_id)s,
            %(enunciado)s,
            %(alternativa_a)s,
            %(alternativa_b)s,
            %(alternativa_c)s,
            %(alternativa_d)s,
            %(resposta_correta)s,
            %(ordem)s
        )
        RETURNING
            id,
            prova_id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            resposta_correta,
            ordem
        """

        return self.db.fetch_one(
            q,
            {
                "prova_id": prova_id,
                "enunciado": enunciado,
                "alternativa_a": alternativa_a,
                "alternativa_b": alternativa_b,
                "alternativa_c": alternativa_c,
                "alternativa_d": alternativa_d,
                "resposta_correta": resposta_correta,
                "ordem": ordem
            }
        )

    def listar_questoes_com_resposta(self, prova_id: int):
        q = """
        SELECT
            id,
            prova_id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            resposta_correta,
            ordem
        FROM questoes_prova
        WHERE prova_id = %(prova_id)s
        ORDER BY ordem ASC, id ASC
        """

        return self.db.fetch_all(
            q,
            {
                "prova_id": prova_id
            }
        )

    def listar_questoes_para_aluno(self, prova_id: int):
        q = """
        SELECT
            id,
            prova_id,
            enunciado,
            alternativa_a,
            alternativa_b,
            alternativa_c,
            alternativa_d,
            ordem
        FROM questoes_prova
        WHERE prova_id = %(prova_id)s
        ORDER BY ordem ASC, id ASC
        """

        return self.db.fetch_all(
            q,
            {
                "prova_id": prova_id
            }
        )

    def registrar_tentativa(
        self,
        prova_id: int,
        aluno_id: int,
        total_questoes: int,
        acertos: int,
        pontos_base: int,
        pontos_gamificados: int,
        percentual: float
    ):
        q = """
        INSERT INTO tentativas_prova
        (
            prova_id,
            aluno_id,
            total_questoes,
            acertos,
            pontos_base,
            pontos_gamificados,
            percentual
        )
        VALUES
        (
            %(prova_id)s,
            %(aluno_id)s,
            %(total_questoes)s,
            %(acertos)s,
            %(pontos_base)s,
            %(pontos_gamificados)s,
            %(percentual)s
        )
        RETURNING
            id,
            prova_id,
            aluno_id,
            total_questoes,
            acertos,
            pontos_base,
            pontos_gamificados,
            percentual,
            data_realizacao
        """

        return self.db.fetch_one(
            q,
            {
                "prova_id": prova_id,
                "aluno_id": aluno_id,
                "total_questoes": total_questoes,
                "acertos": acertos,
                "pontos_base": pontos_base,
                "pontos_gamificados": pontos_gamificados,
                "percentual": percentual
            }
        )

    def registrar_resposta_tentativa(
        self,
        tentativa_id: int,
        questao_id: int,
        resposta_aluno: str,
        correta: bool
    ):
        q = """
        INSERT INTO respostas_tentativa
        (
            tentativa_id,
            questao_id,
            resposta_aluno,
            correta
        )
        VALUES
        (
            %(tentativa_id)s,
            %(questao_id)s,
            %(resposta_aluno)s,
            %(correta)s
        )
        """

        return self.db.execute(
            q,
            {
                "tentativa_id": tentativa_id,
                "questao_id": questao_id,
                "resposta_aluno": resposta_aluno,
                "correta": correta
            }
        )

    def listar_tentativas_aluno(self, aluno_id: int):
        q = """
        SELECT
            t.id,
            t.prova_id,
            p.titulo AS prova,
            t.aluno_id,
            a.nome AS aluno,
            t.total_questoes,
            t.acertos,
            t.pontos_base,
            t.pontos_gamificados,
            t.percentual,
            t.data_realizacao
        FROM tentativas_prova t
        JOIN provas p
            ON t.prova_id = p.id
        JOIN alunos a
            ON t.aluno_id = a.id
        WHERE t.aluno_id = %(aluno_id)s
        ORDER BY t.data_realizacao DESC
        """

        return self.db.fetch_all(
            q,
            {
                "aluno_id": aluno_id
            }
        )

    def obter_estatisticas_provas(self):
        q = """
        SELECT
            (
                SELECT COUNT(*)
                FROM provas
            ) AS total_provas,

            (
                SELECT COUNT(*)
                FROM questoes_prova
            ) AS total_questoes,

            (
                SELECT COUNT(*)
                FROM tentativas_prova
            ) AS total_tentativas,

            (
                SELECT COALESCE(AVG(percentual), 0)
                FROM tentativas_prova
            ) AS media_percentual
        """

        return self.db.fetch_one(q)