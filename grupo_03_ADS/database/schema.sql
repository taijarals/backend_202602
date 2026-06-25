-- Script SQL completo para PostgreSQL / Supabase
CREATE TABLE alunos (
 id SERIAL PRIMARY KEY,
 nome VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE NOT NULL
);
CREATE TABLE niveis (
 id SERIAL PRIMARY KEY,
 nivel INT UNIQUE NOT NULL,
 pontos_minimos INT NOT NULL,
 titulo VARCHAR(50) NOT NULL
);
CREATE TABLE medalhas (
 id SERIAL PRIMARY KEY,
 codigo VARCHAR(30) UNIQUE NOT NULL,
 nome VARCHAR(100) NOT NULL,
 descricao TEXT NOT NULL,
 pontos_bonus INT DEFAULT 0
);
CREATE TABLE progresso_alunos (
 aluno_id INT PRIMARY KEY REFERENCES alunos(id) ON DELETE CASCADE,
 pontos_totais INT DEFAULT 0,
 nivel_atual INT DEFAULT 1 REFERENCES niveis(nivel),
 streak_atual INT DEFAULT 0,
 ultima_atividade TIMESTAMP
);
CREATE TABLE historico_pontos (
 id SERIAL PRIMARY KEY,
 aluno_id INT REFERENCES alunos(id) ON DELETE CASCADE,
 atividade VARCHAR(100) NOT NULL,
 pontos_ganhos INT NOT NULL,
 data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE conquistas_medalhas (
 id SERIAL PRIMARY KEY,
 aluno_id INT REFERENCES alunos(id) ON DELETE CASCADE,
 medalha_id INT REFERENCES medalhas(id) ON DELETE CASCADE,
 data_conquista TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT unique_aluno_medalha UNIQUE(aluno_id, medalha_id)
);
-- Dados base necessários
INSERT INTO niveis (nivel, pontos_minimos, titulo) VALUES
(1, 0, 'Iniciante'), (2, 100, 'Explorador'), (3, 300, 'Veterano'), (4, 600, 'Mestre'), (5,
1000, 'Lenda');
INSERT INTO medalhas (codigo, nome, descricao, pontos_bonus) VALUES
('STREAK_5', 'Inabalável', 'Manteve uma ofensiva de 5 dias seguidos', 50),
('FIRST_BLOOD', 'Primeiro Passo', 'Iniciou sua jornada', 10);


CREATE TABLE IF NOT EXISTS professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS disciplinas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS turmas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    professor_id INT REFERENCES professores(id) ON DELETE SET NULL,
    disciplina_id INT REFERENCES disciplinas(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS turma_alunos (
    id SERIAL PRIMARY KEY,
    turma_id INT REFERENCES turmas(id) ON DELETE CASCADE,
    aluno_id INT REFERENCES alunos(id) ON DELETE CASCADE,
    CONSTRAINT unique_turma_aluno UNIQUE(turma_id, aluno_id)
);

CREATE TABLE IF NOT EXISTS provas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT,
    professor_id INT REFERENCES professores(id) ON DELETE SET NULL,
    disciplina_id INT REFERENCES disciplinas(id) ON DELETE SET NULL,
    duracao_minutos INT DEFAULT 10,
    pontos_por_questao INT DEFAULT 10,
    ativa BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questoes_prova (
    id SERIAL PRIMARY KEY,
    prova_id INT REFERENCES provas(id) ON DELETE CASCADE,
    enunciado TEXT NOT NULL,
    alternativa_a TEXT NOT NULL,
    alternativa_b TEXT NOT NULL,
    alternativa_c TEXT NOT NULL,
    alternativa_d TEXT NOT NULL,
    resposta_correta CHAR(1) NOT NULL CHECK (resposta_correta IN ('A', 'B', 'C', 'D')),
    ordem INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tentativas_prova (
    id SERIAL PRIMARY KEY,
    prova_id INT REFERENCES provas(id) ON DELETE CASCADE,
    aluno_id INT REFERENCES alunos(id) ON DELETE CASCADE,
    total_questoes INT NOT NULL,
    acertos INT NOT NULL,
    pontos_base INT NOT NULL,
    pontos_gamificados INT NOT NULL,
    percentual NUMERIC(5,2) NOT NULL,
    data_realizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS respostas_tentativa (
    id SERIAL PRIMARY KEY,
    tentativa_id INT REFERENCES tentativas_prova(id) ON DELETE CASCADE,
    questao_id INT REFERENCES questoes_prova(id) ON DELETE CASCADE,
    resposta_aluno CHAR(1) NOT NULL,
    correta BOOLEAN NOT NULL
);