import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS desafios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    pontos INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pontuacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    pontos INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS submissoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    desafio_id INTEGER,
    resposta TEXT
)
""")

conn.commit()