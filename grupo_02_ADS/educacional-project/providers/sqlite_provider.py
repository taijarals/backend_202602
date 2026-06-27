from database.database import conn, cursor

class SQLiteProvider:

    def listar_alunos(self):

        cursor.execute(
            "SELECT * FROM alunos"
        )

        return cursor.fetchall()

    def criar_aluno(self, nome):

        cursor.execute(
            "INSERT INTO alunos(nome) VALUES(?)",
            (nome,)
        )

        conn.commit()

    def listar_desafios(self):

        cursor.execute(
        "SELECT * FROM desafios"
    )

        return cursor.fetchall()

    def criar_desafio(self, titulo, pontos):

        cursor.execute(
            "INSERT INTO desafios(titulo,pontos) VALUES(?,?)",
            (titulo, pontos)
        )

    def registrar_pontuacao(self, aluno_id, pontos):

        cursor.execute(
            "INSERT INTO pontuacoes(aluno_id, pontos) VALUES (?, ?)",
            (aluno_id, pontos)
        )

        conn.commit()

    def obter_ranking(self):

        cursor.execute("""
            SELECT
                alunos.nome,
                SUM(pontuacoes.pontos) as total
            FROM pontuacoes
            JOIN alunos
                ON alunos.id = pontuacoes.aluno_id
            GROUP BY alunos.nome
            ORDER BY total DESC
        """)

        return cursor.fetchall()

        conn.commit()

    def criar_submissao(self, aluno_id, desafio_id,resposta):

        cursor.execute(
            """
            INSERT INTO submissoes
            (aluno_id, desafio_id, resposta)
            VALUES (?, ?, ?)
            """,
            (
                aluno_id,
                desafio_id,
                resposta
            )
        )

        conn.commit()