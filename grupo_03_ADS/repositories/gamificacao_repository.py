from providers.factory import ProviderFactory


class GamificacaoRepository:

    def __init__(self):
        self.db = ProviderFactory.create()

    # ==================================================
    # ALUNOS
    # ==================================================

    def obter_aluno(self, aluno_id: int):
        q = """
        SELECT *
        FROM alunos
        WHERE id = %(id)s
        """
        return self.db.fetch_one(q, {"id": aluno_id})

    def listar_alunos(self):
        q = """
        SELECT
            a.id,
            a.nome,
            a.email,
            COALESCE(p.pontos_totais, 0) AS pontos,
            COALESCE(p.nivel_atual, 1) AS nivel,
            COALESCE(n.titulo, 'Iniciante') AS titulo,
            COALESCE(p.streak_atual, 0) AS streak
        FROM alunos a
        LEFT JOIN progresso_alunos p
            ON a.id = p.aluno_id
        LEFT JOIN niveis n
            ON p.nivel_atual = n.nivel
        ORDER BY a.id ASC
        """
        return self.db.fetch_all(q)

    def cadastrar_aluno(self, nome: str, email: str):
        q = """
        INSERT INTO alunos (nome, email)
        VALUES (%(nome)s, %(email)s)
        RETURNING id, nome, email
        """
        return self.db.fetch_one(
            q,
            {
                "nome": nome,
                "email": email
            }
        )

    # ==================================================
    # PROFESSORES
    # ==================================================

    def obter_professor(self, professor_id: int):
        q = """
        SELECT *
        FROM professores
        WHERE id = %(id)s
        """
        return self.db.fetch_one(q, {"id": professor_id})

    def cadastrar_professor(self, nome: str, email: str):
        q = """
        INSERT INTO professores (nome, email)
        VALUES (%(nome)s, %(email)s)
        RETURNING id, nome, email
        """
        return self.db.fetch_one(
            q,
            {
                "nome": nome,
                "email": email
            }
        )

    def listar_professores(self):
        q = """
        SELECT
            id,
            nome,
            email
        FROM professores
        ORDER BY id ASC
        """
        return self.db.fetch_all(q)

    # ==================================================
    # DISCIPLINAS
    # ==================================================

    def obter_disciplina(self, disciplina_id: int):
        q = """
        SELECT *
        FROM disciplinas
        WHERE id = %(id)s
        """
        return self.db.fetch_one(q, {"id": disciplina_id})

    def cadastrar_disciplina(self, nome: str, descricao: str = None):
        q = """
        INSERT INTO disciplinas (nome, descricao)
        VALUES (%(nome)s, %(descricao)s)
        RETURNING id, nome, descricao
        """
        return self.db.fetch_one(
            q,
            {
                "nome": nome,
                "descricao": descricao
            }
        )

    def listar_disciplinas(self):
        q = """
        SELECT
            id,
            nome,
            descricao
        FROM disciplinas
        ORDER BY id ASC
        """
        return self.db.fetch_all(q)

    # ==================================================
    # TURMAS
    # ==================================================

    def obter_turma(self, turma_id: int):
        q = """
        SELECT *
        FROM turmas
        WHERE id = %(id)s
        """
        return self.db.fetch_one(q, {"id": turma_id})

    def cadastrar_turma(
        self,
        nome: str,
        professor_id: int,
        disciplina_id: int
    ):
        q = """
        INSERT INTO turmas
        (
            nome,
            professor_id,
            disciplina_id
        )
        VALUES
        (
            %(nome)s,
            %(professor_id)s,
            %(disciplina_id)s
        )
        RETURNING
            id,
            nome,
            professor_id,
            disciplina_id
        """
        return self.db.fetch_one(
            q,
            {
                "nome": nome,
                "professor_id": professor_id,
                "disciplina_id": disciplina_id
            }
        )

    def listar_turmas(self):
        q = """
        SELECT
            t.id,
            t.nome,
            t.professor_id,
            p.nome AS professor,
            t.disciplina_id,
            d.nome AS disciplina,
            COUNT(ta.aluno_id) AS total_alunos
        FROM turmas t
        LEFT JOIN professores p
            ON t.professor_id = p.id
        LEFT JOIN disciplinas d
            ON t.disciplina_id = d.id
        LEFT JOIN turma_alunos ta
            ON t.id = ta.turma_id
        GROUP BY
            t.id,
            t.nome,
            t.professor_id,
            p.nome,
            t.disciplina_id,
            d.nome
        ORDER BY t.id ASC
        """
        return self.db.fetch_all(q)

    def vincular_aluno_turma(
        self,
        turma_id: int,
        aluno_id: int
    ):
        q = """
        INSERT INTO turma_alunos
        (
            turma_id,
            aluno_id
        )
        VALUES
        (
            %(turma_id)s,
            %(aluno_id)s
        )
        ON CONFLICT DO NOTHING
        RETURNING id, turma_id, aluno_id
        """
        return self.db.fetch_one(
            q,
            {
                "turma_id": turma_id,
                "aluno_id": aluno_id
            }
        )

    def listar_alunos_da_turma(self, turma_id: int):
        q = """
        SELECT
            a.id,
            a.nome,
            a.email
        FROM turma_alunos ta
        JOIN alunos a
            ON ta.aluno_id = a.id
        WHERE ta.turma_id = %(turma_id)s
        ORDER BY a.nome ASC
        """
        return self.db.fetch_all(
            q,
            {
                "turma_id": turma_id
            }
        )

    # ==================================================
    # GAMIFICAÇÃO
    # ==================================================

    def obter_progresso(self, aluno_id: int):
        q = """
        SELECT p.*, n.titulo
        FROM progresso_alunos p
        JOIN niveis n
            ON p.nivel_atual = n.nivel
        WHERE p.aluno_id = %(id)s
        """
        return self.db.fetch_one(q, {"id": aluno_id})

    def inicializar_progresso(self, aluno_id: int):
        q = """
        INSERT INTO progresso_alunos (aluno_id)
        VALUES (%(id)s)
        ON CONFLICT DO NOTHING
        """
        self.db.execute(q, {"id": aluno_id})

    def salvar_historico(
        self,
        aluno_id: int,
        atividade: str,
        pontos: int
    ):
        q = """
        INSERT INTO historico_pontos
        (
            aluno_id,
            atividade,
            pontos_ganhos
        )
        VALUES
        (
            %(id)s,
            %(a)s,
            %(p)s
        )
        """

        self.db.execute(
            q,
            {
                "id": aluno_id,
                "a": atividade,
                "p": pontos
            }
        )

    def atualizar_progresso(
        self,
        aluno_id: int,
        pontos: int,
        nivel: int,
        streak: int
    ):
        q = """
        UPDATE progresso_alunos
        SET
            pontos_totais = %(p)s,
            nivel_atual = %(n)s,
            streak_atual = %(s)s,
            ultima_atividade = CURRENT_TIMESTAMP
        WHERE aluno_id = %(id)s
        """

        self.db.execute(
            q,
            {
                "id": aluno_id,
                "p": pontos,
                "n": nivel,
                "s": streak
            }
        )

    def obter_niveis(self):
        return self.db.fetch_all(
            """
            SELECT *
            FROM niveis
            ORDER BY nivel ASC
            """
        )

    def atribuir_medalha(
        self,
        aluno_id: int,
        codigo: str
    ):
        q = """
        INSERT INTO conquistas_medalhas
        (
            aluno_id,
            medalha_id
        )
        SELECT
            %(id)s,
            id
        FROM medalhas
        WHERE codigo = %(c)s
        ON CONFLICT DO NOTHING
        """

        self.db.execute(
            q,
            {
                "id": aluno_id,
                "c": codigo
            }
        )

    def obter_medalhas_aluno(self, aluno_id: int):
        q = """
        SELECT
            m.codigo,
            m.nome,
            m.descricao,
            m.pontos_bonus,
            c.data_conquista
        FROM conquistas_medalhas c
        JOIN medalhas m
            ON c.medalha_id = m.id
        WHERE c.aluno_id = %(id)s
        ORDER BY c.data_conquista DESC
        """

        return self.db.fetch_all(
            q,
            {
                "id": aluno_id
            }
        )

    def obter_ranking(self, geral=True):

        if geral:

            q = """
            SELECT
                a.id,
                a.nome,
                p.pontos_totais AS pontos,
                p.nivel_atual AS nivel
            FROM progresso_alunos p
            JOIN alunos a
                ON p.aluno_id = a.id
            ORDER BY p.pontos_totais DESC
            """

        else:

            q = """
            SELECT
                a.id,
                a.nome,
                SUM(h.pontos_ganhos) AS pontos,
                p.nivel_atual AS nivel
            FROM historico_pontos h
            JOIN alunos a
                ON h.aluno_id = a.id
            JOIN progresso_alunos p
                ON a.id = p.aluno_id
            WHERE h.data_registro >=
                CURRENT_TIMESTAMP - INTERVAL '7 days'
            GROUP BY
                a.id,
                a.nome,
                p.nivel_atual
            ORDER BY pontos DESC
            """

        return self.db.fetch_all(q)

    # ==================================================
    # ESTATÍSTICAS ADMIN
    # ==================================================

    def obter_estatisticas_admin(self):
        q = """
        SELECT
            (
                SELECT COUNT(*)
                FROM alunos
            ) AS total_alunos,

            (
                SELECT COUNT(*)
                FROM professores
            ) AS total_professores,

            (
                SELECT COUNT(*)
                FROM disciplinas
            ) AS total_disciplinas,

            (
                SELECT COUNT(*)
                FROM turmas
            ) AS total_turmas,

            (
                SELECT COALESCE(SUM(pontos_totais), 0)
                FROM progresso_alunos
            ) AS total_pontos,

            (
                SELECT COUNT(*)
                FROM conquistas_medalhas
            ) AS quantidade_medalhas,

            (
                SELECT COALESCE(MAX(pontos_totais), 0)
                FROM progresso_alunos
            ) AS maior_pontuacao
        """

        return self.db.fetch_one(q)

    def obter_aluno_maior_pontuacao(self):
        q = """
        SELECT
            a.id,
            a.nome,
            p.pontos_totais AS pontos
        FROM progresso_alunos p
        JOIN alunos a
            ON p.aluno_id = a.id
        ORDER BY p.pontos_totais DESC
        LIMIT 1
        """

        return self.db.fetch_one(q)