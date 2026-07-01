/*
# Educational Gamification Platform - Initial Schema

This migration creates the complete database schema for an educational gamification platform
with support for challenges, mini-tests, gamification, feedback, teams, and missions.

## 1. Users and Profiles
- `profiles` - User profiles with role (student/professor)
- Links to Supabase auth.users

## 2. Academic Structure
- `disciplinas` - Subjects/Courses
- `turmas` - Classes/Groups
- `turma_alunos` - Student-class enrollment

## 3. Challenges System
- `desafios` - Challenges created by professors
- `submissoes` - Student submissions for challenges
- `votos` - Peer voting on submissions

## 4. Mini-Tests
- `mini_provas` - Quick tests with timer
- `questoes` - Questions for mini-tests
- `tentativas_prova` - Student test attempts
- `respostas_tentativa` - Individual answers

## 5. Gamification
- `pontuacoes` - Point tracking per student
- `medalhas` - Achievement definitions
- `conquistas` - Student achievements earned
- `niveis` - Level progression system

## 6. Instant Feedback
- `enquetes` - Quick polls
- `opcoes_enquete` - Poll options
- `votos_enquete` - Student poll votes

## 7. Teams
- `equipes` - Student teams
- `equipe_membros` - Team membership

## 8. Missions
- `missoes` - Learning journeys
- `missoes_etapas` - Mission objectives
- `progresso_missao` - Student progress on missions

## Security
- RLS enabled on all tables
- Owner-scoped policies with auth.uid()
- Role-based access control
*/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'professor', 'admin')),
    avatar_url TEXT,
    bio TEXT,
    pontuacao_total INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Disciplinas (Subjects)
CREATE TABLE IF NOT EXISTS disciplinas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    codigo VARCHAR(50) UNIQUE,
    cor VARCHAR(20) DEFAULT '#3B82F6',
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Turmas (Classes)
CREATE TABLE IF NOT EXISTS turmas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    disciplina_id UUID NOT NULL REFERENCES disciplinas(id) ON DELETE CASCADE,
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    codigo_convite VARCHAR(20) UNIQUE,
    ano INTEGER,
    semestre INTEGER,
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Turma-Alunos (Enrollment)
CREATE TABLE IF NOT EXISTS turma_alunos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    turma_id UUID NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    entrou_em TIMESTAMPTZ DEFAULT now(),
    UNIQUE(turma_id, aluno_id)
);

-- Desafios (Challenges)
CREATE TABLE IF NOT EXISTS desafios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE SET NULL,
    turma_id UUID REFERENCES turmas(id) ON DELETE SET NULL,
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    pontos_recompensa INTEGER DEFAULT 100,
    dificuldade VARCHAR(20) DEFAULT 'media' CHECK (dificuldade IN ('facil', 'media', 'dificil', 'expert')),
    prazo TIMESTAMPTZ,
    tipo VARCHAR(50) DEFAULT 'codigo' CHECK (tipo IN ('codigo', 'quiz', 'projeto', 'pesquisa', 'outro')),
    restricoes JSONB,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Submissoes (Submissions)
CREATE TABLE IF NOT EXISTS submissoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    desafio_id UUID NOT NULL REFERENCES desafios(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    conteudo TEXT NOT NULL,
    anexos JSONB,
    pontos_obtidos INTEGER DEFAULT 0,
    feedback_professor TEXT,
    status VARCHAR(30) DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_revisao', 'aprovada', 'rejeitada', 'nota_atribuida')),
    votos INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Votos (Peer Voting)
CREATE TABLE IF NOT EXISTS votos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submissao_id UUID NOT NULL REFERENCES submissoes(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    pontuacao INTEGER NOT NULL CHECK (pontuacao >= 1 AND pontuacao <= 5),
    comentario TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(submissao_id, aluno_id)
);

-- Mini Provas (Quick Tests)
CREATE TABLE IF NOT EXISTS mini_provas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE SET NULL,
    turma_id UUID REFERENCES turmas(id) ON DELETE SET NULL,
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    duracao_minutos INTEGER DEFAULT 30,
    tentativas_permitidas INTEGER DEFAULT 1,
    pontos_maximos INTEGER DEFAULT 100,
    aleatorizar_questoes BOOLEAN DEFAULT false,
    ativa BOOLEAN DEFAULT true,
    inicio TIMESTAMP,
    fim TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Questoes (Questions)
CREATE TABLE IF NOT EXISTS questoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mini_prova_id UUID NOT NULL REFERENCES mini_provas(id) ON DELETE CASCADE,
    enunciado TEXT NOT NULL,
    tipo VARCHAR(30) DEFAULT 'multipla_escola' CHECK (tipo IN ('multipla_escolha', 'verdadeiro_falso', 'resposta_curta', 'codigo')),
    opcoes JSONB,
    resposta_correta TEXT NOT NULL,
    pontos INTEGER DEFAULT 10,
    ordem INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Tentativas Prova (Test Attempts)
CREATE TABLE IF NOT EXISTS tentativas_prova (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mini_prova_id UUID NOT NULL REFERENCES mini_provas(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    inicio_em TIMESTAMP NOT NULL DEFAULT now(),
    fim_em TIMESTAMP,
    tempo_gasto_segundos INTEGER,
    pontos_obtidos INTEGER DEFAULT 0,
    aprovada BOOLEAN,
    status VARCHAR(30) DEFAULT 'em_andamento' CHECK (status IN ('em_andamento', 'finalizada', 'expirada')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Respostas Tentativa (Attempt Answers)
CREATE TABLE IF NOT EXISTS respostas_tentativa (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tentativa_id UUID NOT NULL REFERENCES tentativas_prova(id) ON DELETE CASCADE,
    questao_id UUID NOT NULL REFERENCES questoes(id) ON DELETE CASCADE,
    resposta TEXT,
    correta BOOLEAN,
    pontos_obtidos INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Pontuacoes (Score Tracking)
CREATE TABLE IF NOT EXISTS pontuacoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    turma_id UUID REFERENCES turmas(id) ON DELETE SET NULL,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE SET NULL,
    pontos INTEGER DEFAULT 0,
    fonte VARCHAR(50) CHECK (fonte IN ('desafio', 'mini_prova', 'missao', 'medalha', 'bonus')),
    referencia_id UUID,
    descricao TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Medalhas (Achievement Definitions)
CREATE TABLE IF NOT EXISTS medalhas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    icone VARCHAR(100) DEFAULT 'medal',
    cor VARCHAR(20) DEFAULT '#FFD700',
    pontos_requeridos INTEGER,
    tipo VARCHAR(50) CHECK (tipo IN ('pontos', 'desafios', 'provas', 'missoes', 'especial')),
    nivel INTEGER DEFAULT 1,
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Conquistas (User Achievements)
CREATE TABLE IF NOT EXISTS conquistas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    medalha_id UUID NOT NULL REFERENCES medalhas(id) ON DELETE CASCADE,
    conquistada_em TIMESTAMPTZ DEFAULT now(),
    UNIQUE(aluno_id, medalha_id)
);

-- Niveis (Level System)
CREATE TABLE IF NOT EXISTS niveis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nivel INTEGER NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    pontos_necessarios INTEGER NOT NULL,
    titulo VARCHAR(255),
    recompensa TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enquetes (Polls)
CREATE TABLE IF NOT EXISTS enquetes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    turma_id UUID REFERENCES turmas(id) ON DELETE SET NULL,
    multipla_escolha BOOLEAN DEFAULT false,
    anonima BOOLEAN DEFAULT false,
    ativa BOOLEAN DEFAULT true,
   fim TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Opcoes Enquete (Poll Options)
CREATE TABLE IF NOT EXISTS opcoes_enquete (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enquete_id UUID NOT NULL REFERENCES enquetes(id) ON DELETE CASCADE,
    texto VARCHAR(500) NOT NULL,
    ordem INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Votos Enquete (Poll Votes)
CREATE TABLE IF NOT EXISTS votos_enquete (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enquete_id UUID NOT NULL REFERENCES enquetes(id) ON DELETE CASCADE,
    opcao_id UUID NOT NULL REFERENCES opcoes_enquete(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(enquete_id, aluno_id)
);

-- Equipes (Teams)
CREATE TABLE IF NOT EXISTS equipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    turma_id UUID NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
    cor VARCHAR(20) DEFAULT '#3B82F6',
    pontuacao INTEGER DEFAULT 0,
    max_membros INTEGER DEFAULT 5,
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Equipe Membros (Team Members)
CREATE TABLE IF NOT EXISTS equipe_membros (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    equipe_id UUID NOT NULL REFERENCES equipes(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    papel VARCHAR(30) DEFAULT 'membro' CHECK (papel IN ('lider', 'membro')),
    entrou_em TIMESTAMPTZ DEFAULT now(),
    UNIQUE(equipe_id, aluno_id)
);

-- Missoes (Missions)
CREATE TABLE IF NOT EXISTS missoes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    disciplina_id UUID REFERENCES disciplinas(id) ON DELETE SET NULL,
    turma_id UUID REFERENCES turmas(id) ON DELETE SET NULL,
    professor_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    pontos_recompensa INTEGER DEFAULT 500,
    nivel_dificuldade INTEGER DEFAULT 1,
    pre_requisitos UUID[],
    ativa BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Missoes Etapas (Mission Stages)
CREATE TABLE IF NOT EXISTS missoes_etapas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    missao_id UUID NOT NULL REFERENCES missoes(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    ordem INTEGER NOT NULL DEFAULT 0,
    pontos INTEGER DEFAULT 50,
    tipo VARCHAR(50) DEFAULT 'tarefa' CHECK (tipo IN ('tarefa', 'quiz', 'projeto', 'pesquisa')),
    requisitos JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Progresso Missao (Mission Progress)
CREATE TABLE IF NOT EXISTS progresso_missao (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    missao_id UUID NOT NULL REFERENCES missoes(id) ON DELETE CASCADE,
    etapa_id UUID NOT NULL REFERENCES missoes_etapas(id) ON DELETE CASCADE,
    aluno_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    status VARCHAR(30) DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_progresso', 'completa', 'falhou')),
    pontos_obtidos INTEGER DEFAULT 0,
    completada_em TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(etapa_id, aluno_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_desafios_disciplina ON desafios(disciplina_id);
CREATE INDEX IF NOT EXISTS idx_desafios_turma ON desafios(turma_id);
CREATE INDEX IF NOT EXISTS idx_desafios_professor ON desafios(professor_id);
CREATE INDEX IF NOT EXISTS idx_submissoes_desafio ON submissoes(desafio_id);
CREATE INDEX IF NOT EXISTS idx_submissoes_aluno ON submissoes(aluno_id);
CREATE INDEX IF NOT EXISTS idx_tentativas_aluno ON tentativas_prova(aluno_id);
CREATE INDEX IF NOT EXISTS idx_pontuacoes_aluno ON pontuacoes(aluno_id);
CREATE INDEX IF NOT EXISTS idx_conquistas_aluno ON conquistas(aluno_id);

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE disciplinas ENABLE ROW LEVEL SECURITY;
ALTER TABLE turmas ENABLE ROW LEVEL SECURITY;
ALTER TABLE turma_alunos ENABLE ROW LEVEL SECURITY;
ALTER TABLE desafios ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE votos ENABLE ROW LEVEL SECURITY;
ALTER TABLE mini_provas ENABLE ROW LEVEL SECURITY;
ALTER TABLE questoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tentativas_prova ENABLE ROW LEVEL SECURITY;
ALTER TABLE respostas_tentativa ENABLE ROW LEVEL SECURITY;
ALTER TABLE pontuacoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE medalhas ENABLE ROW LEVEL SECURITY;
ALTER TABLE conquistas ENABLE ROW LEVEL SECURITY;
ALTER TABLE niveis ENABLE ROW LEVEL SECURITY;
ALTER TABLE enquetes ENABLE ROW LEVEL SECURITY;
ALTER TABLE opcoes_enquete ENABLE ROW LEVEL SECURITY;
ALTER TABLE votos_enquete ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE equipe_membros ENABLE ROW LEVEL SECURITY;
ALTER TABLE missoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE missoes_etapas ENABLE ROW LEVEL SECURITY;
ALTER TABLE progresso_missao ENABLE ROW LEVEL SECURITY;

-- Profiles policies
DROP POLICY IF EXISTS "users_own_profile" ON profiles;
CREATE POLICY "users_own_profile" ON profiles FOR ALL
    TO authenticated USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "profiles_read_all_authenticated" ON profiles;
CREATE POLICY "profiles_read_all_authenticated" ON profiles FOR SELECT
    TO authenticated USING (true);

-- Disciplinas policies
DROP POLICY IF EXISTS "disciplinas_read_authenticated" ON disciplinas;
CREATE POLICY "disciplinas_read_authenticated" ON disciplinas FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "disciplinas_manage_professor" ON disciplinas;
CREATE POLICY "disciplinas_manage_professor" ON disciplinas FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id))
    WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Turmas policies
DROP POLICY IF EXISTS "turmas_read_authenticated" ON turmas;
CREATE POLICY "turmas_read_authenticated" ON turmas FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "turmas_manage_professor" ON turmas;
CREATE POLICY "turmas_manage_professor" ON turmas FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id))
    WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Turma Alunos policies
DROP POLICY IF EXISTS "turma_alunos_read_members" ON turma_alunos;
CREATE POLICY "turma_alunos_read_members" ON turma_alunos FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "turma_alunos_insert_student" ON turma_alunos;
CREATE POLICY "turma_alunos_insert_student" ON turma_alunos FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Desafios policies
DROP POLICY IF EXISTS "desafios_read_authenticated" ON desafios;
CREATE POLICY "desafios_read_authenticated" ON desafios FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "desafios_manage_professor" ON desafios;
CREATE POLICY "desafios_manage_professor" ON desafios FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Submissoes policies
DROP POLICY IF EXISTS "submissoes_read_own" ON submissoes;
CREATE POLICY "submissoes_read_own" ON submissoes FOR SELECT
    TO authenticated USING (
        auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id)
        OR auth.uid() IN (SELECT user_id FROM profiles p JOIN desafios d ON d.professor_id = p.id WHERE d.id = desafio_id)
    );

DROP POLICY IF EXISTS "submissoes_insert_student" ON submissoes;
CREATE POLICY "submissoes_insert_student" ON submissoes FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

DROP POLICY IF EXISTS "submissoes_update_professor" ON submissoes;
CREATE POLICY "submissoes_update_professor" ON submissoes FOR UPDATE
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles p JOIN desafios d ON d.professor_id = p.id WHERE d.id = submissoes.desafio_id));

-- Votos policies
DROP POLICY IF EXISTS "votos_read_all" ON votos;
CREATE POLICY "votos_read_all" ON votos FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "votos_insert_student" ON votos;
CREATE POLICY "votos_insert_student" ON votos FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Mini Provas policies
DROP POLICY IF EXISTS "mini_provas_read_authenticated" ON mini_provas;
CREATE POLICY "mini_provas_read_authenticated" ON mini_provas FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "mini_provas_manage_professor" ON mini_provas;
CREATE POLICY "mini_provas_manage_professor" ON mini_provas FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Questoes policies (inherit from mini_provas)
DROP POLICY IF EXISTS "questoes_read_authenticated" ON questoes;
CREATE POLICY "questoes_read_authenticated" ON questoes FOR SELECT
    TO authenticated USING (true);

-- Tentativas Prova policies
DROP POLICY IF EXISTS "tentativas_read_own" ON tentativas_prova;
CREATE POLICY "tentativas_read_own" ON tentativas_prova FOR SELECT
    TO authenticated USING (
        auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id)
        OR auth.uid() IN (SELECT user_id FROM profiles p JOIN mini_provas mp ON mp.professor_id = p.id WHERE mp.id = mini_prova_id)
    );

DROP POLICY IF EXISTS "tentativas_insert_student" ON tentativas_prova;
CREATE POLICY "tentativas_insert_student" ON tentativas_prova FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

DROP POLICY IF EXISTS "tentativas_update_student" ON tentativas_prova;
CREATE POLICY "tentativas_update_student" ON tentativas_prova FOR UPDATE
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Respostas Tentativa policies
DROP POLICY IF EXISTS "respostas_read_own" ON respostas_tentativa;
CREATE POLICY "respostas_read_own" ON respostas_tentativa FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "respostas_insert_student" ON respostas_tentativa;
CREATE POLICY "respostas_insert_student" ON respostas_tentativa FOR INSERT
    TO authenticated WITH CHECK (true);

-- Pontuacoes policies
DROP POLICY IF EXISTS "pontuacoes_read_own" ON pontuacoes;
CREATE POLICY "pontuacoes_read_own" ON pontuacoes FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "pontuacoes_insert_system" ON pontuacoes;
CREATE POLICY "pontuacoes_insert_system" ON pontuacoes FOR INSERT
    TO authenticated WITH CHECK (true);

-- Medalhas policies (public read)
DROP POLICY IF EXISTS "medalhas_read_all" ON medalhas;
CREATE POLICY "medalhas_read_all" ON medalhas FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "medalhas_manage_admin" ON medalhas;
CREATE POLICY "medalhas_manage_admin" ON medalhas FOR ALL
    TO authenticated USING (EXISTS (SELECT 1 FROM profiles WHERE user_id = auth.uid() AND role = 'admin'));

-- Conquistas policies
DROP POLICY IF EXISTS "conquistas_read_own" ON conquistas;
CREATE POLICY "conquistas_read_own" ON conquistas FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "conquistas_insert_own" ON conquistas;
CREATE POLICY "conquistas_insert_own" ON conquistas FOR INSERT
    TO authenticated WITH CHECK (true);

-- Niveis policies (public read)
DROP POLICY IF EXISTS "niveis_read_all" ON niveis;
CREATE POLICY "niveis_read_all" ON niveis FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "niveis_manage_admin" ON niveis;
CREATE POLICY "niveis_manage_admin" ON niveis FOR ALL
    TO authenticated USING (EXISTS (SELECT 1 FROM profiles WHERE user_id = auth.uid() AND role = 'admin'));

-- Enquetes policies
DROP POLICY IF EXISTS "enquetes_read_authenticated" ON enquetes;
CREATE POLICY "enquetes_read_authenticated" ON enquetes FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "enquetes_manage_professor" ON enquetes;
CREATE POLICY "enquetes_manage_professor" ON enquetes FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Opcoes Enquete policies
DROP POLICY IF EXISTS "opcoes_enquete_read_all" ON opcoes_enquete;
CREATE POLICY "opcoes_enquete_read_all" ON opcoes_enquete FOR SELECT
    TO authenticated USING (true);

-- Votos Enquete policies
DROP POLICY IF EXISTS "votos_enquete_read_all" ON votos_enquete;
CREATE POLICY "votos_enquete_read_all" ON votos_enquete FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "votos_enquete_insert_student" ON votos_enquete;
CREATE POLICY "votos_enquete_insert_student" ON votos_enquete FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Equipes policies
DROP POLICY IF EXISTS "equipes_read_authenticated" ON equipes;
CREATE POLICY "equipes_read_authenticated" ON equipes FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "equipes_manage_members" ON equipes;
CREATE POLICY "equipes_manage_members" ON equipes FOR ALL
    TO authenticated USING (
        EXISTS (SELECT 1 FROM equipe_membros em JOIN profiles p ON p.id = em.aluno_id WHERE em.equipe_id = equipes.id AND p.user_id = auth.uid() AND em.papel = 'lider')
        OR auth.uid() IN (SELECT user_id FROM profiles WHERE id IN (SELECT professor_id FROM turmas WHERE id = turma_id))
    );

-- Equipe Membros policies
DROP POLICY IF EXISTS "equipe_membros_read_all" ON equipe_membros;
CREATE POLICY "equipe_membros_read_all" ON equipe_membros FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "equipe_membros_insert_student" ON equipe_membros;
CREATE POLICY "equipe_membros_insert_student" ON equipe_membros FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Missoes policies
DROP POLICY IF EXISTS "missoes_read_authenticated" ON missoes;
CREATE POLICY "missoes_read_authenticated" ON missoes FOR SELECT
    TO authenticated USING (true);

DROP POLICY IF EXISTS "missoes_manage_professor" ON missoes;
CREATE POLICY "missoes_manage_professor" ON missoes FOR ALL
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = professor_id));

-- Missoes Etapas policies
DROP POLICY IF EXISTS "missoes_etapas_read_authenticated" ON missoes_etapas;
CREATE POLICY "missoes_etapas_read_authenticated" ON missoes_etapas FOR SELECT
    TO authenticated USING (true);

-- Progresso Missao policies
DROP POLICY IF EXISTS "progresso_missao_read_own" ON progresso_missao;
CREATE POLICY "progresso_missao_read_own" ON progresso_missao FOR SELECT
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

DROP POLICY IF EXISTS "progresso_missao_insert_student" ON progresso_missao;
CREATE POLICY "progresso_missao_insert_student" ON progresso_missao FOR INSERT
    TO authenticated WITH CHECK (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

DROP POLICY IF EXISTS "progresso_missao_update_student" ON progresso_missao;
CREATE POLICY "progresso_missao_update_student" ON progresso_missao FOR UPDATE
    TO authenticated USING (auth.uid() IN (SELECT user_id FROM profiles WHERE id = aluno_id));

-- Insert default levels
INSERT INTO niveis (nivel, nome, pontos_necessarios, titulo) VALUES
(1, 'Iniciante', 0, 'Aprendiz'),
(2, 'Aprendiz', 100, 'Estudante'),
(3, 'Estudante', 300, 'Conhecedor'),
(4, 'Conhecedor', 600, 'Expert'),
(5, 'Expert', 1000, 'Mestre'),
(6, 'Mestre', 1500, 'Grão-Mestre'),
(7, 'Grão-Mestre', 2500, 'Lenda'),
(8, 'Lenda', 4000, 'Campeão'),
(9, 'Campeão', 6000, 'Veterano'),
(10, 'Veterano', 10000, 'Supremo')
ON CONFLICT (nivel) DO NOTHING;

-- Insert default medals
INSERT INTO medalhas (nome, descricao, icone, cor, tipo, nivel) VALUES
('Primeira Contribuição', 'Completou seu primeiro desafio', 'trophy', '#FFD700', 'desafios', 1),
('Velocista', 'Completou um desafio em menos de 1 hora', 'zap', '#FF6B6B', 'especial', 1),
('Perfeição', 'Obteve 100% em uma mini-prova', 'star', '#4ECDC4', 'provas', 1),
('Explorador', 'Completou 3 missões', 'compass', '#A855F7', 'missoes', 1),
('Colaborador', 'Fez parte de uma equipe vencedora', 'users', '#3B82F6', 'especial', 1),
('Mestre dos Desafios', 'Completou 10 desafios', 'award', '#FFD700', 'desafios', 2),
('Einstein', 'Obteve 100% em 3 mini-provas', 'lightbulb', '#4ECDC4', 'provas', 2),
('Veterano', 'Acumule 1000 pontos', 'medal', '#A855F7', 'pontos', 2),
('Lenda', 'Complete todas as missões de uma disciplina', 'crown', '#FF6B6B', 'missoes', 3)
ON CONFLICT DO NOTHING;

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers for updated_at
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT unnest(ARRAY['profiles', 'disciplinas', 'turmas', 'desafios', 'submissoes', 'mini_provas', 'equipes', 'missoes', 'progresso_missao'])
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%s_updated_at ON %s', t, t);
        EXECUTE format('CREATE TRIGGER update_%s_updated_at BEFORE UPDATE ON %s FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$;