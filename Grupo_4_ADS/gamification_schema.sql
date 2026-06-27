-- =============================================================================
-- MÓDULO DE GAMIFICAÇÃO — Schema Completo para Supabase/PostgreSQL
-- =============================================================================
-- Ordem de criação respeita dependências de FK:
--   nivel → usuarios (externo) → medalha → conquista
--                                        → historico_pontos → ranking
-- =============================================================================

-- -----------------------------------------------------------------------------
-- EXTENSÕES
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- =============================================================================
-- TABELA: nivel
-- Armazena os níveis disponíveis no sistema e seus limiares de XP.
-- =============================================================================
CREATE TABLE IF NOT EXISTS nivel (
    id           SERIAL        PRIMARY KEY,
    nome         VARCHAR(50)   NOT NULL UNIQUE,          -- Ex: "Iniciante", "Avançado"
    xp_minimo    INTEGER       NOT NULL DEFAULT 0,       -- XP mínimo para atingir este nível
    xp_maximo    INTEGER,                                -- NULL = nível máximo (sem teto)
    icone_url    TEXT,                                   -- URL do ícone representativo
    criado_em    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT nivel_xp_check CHECK (xp_minimo >= 0),
    CONSTRAINT nivel_faixa_check CHECK (xp_maximo IS NULL OR xp_maximo > xp_minimo)
);

COMMENT ON TABLE  nivel             IS 'Faixas de nível com limiares de XP que determinam a progressão do usuário.';
COMMENT ON COLUMN nivel.xp_minimo  IS 'XP acumulado mínimo para alcançar este nível (inclusive).';
COMMENT ON COLUMN nivel.xp_maximo  IS 'XP acumulado máximo deste nível (exclusive). NULL indica nível máximo.';


-- =============================================================================
-- TABELA: medalha
-- Catálogo de medalhas que podem ser concedidas aos usuários.
-- =============================================================================
CREATE TABLE IF NOT EXISTS medalha (
    id           UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome         VARCHAR(100)  NOT NULL UNIQUE,
    descricao    TEXT,
    icone_url    TEXT,
    tipo         VARCHAR(30)   NOT NULL DEFAULT 'conquista',  -- 'conquista' | 'streak' | 'ranking' | 'especial'
    criado_em    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT medalha_tipo_check CHECK (tipo IN ('conquista', 'streak', 'ranking', 'especial'))
);

COMMENT ON TABLE  medalha      IS 'Catálogo central de medalhas disponíveis no sistema de gamificação.';
COMMENT ON COLUMN medalha.tipo IS 'Categoria da medalha: conquista, streak, ranking ou especial.';


-- =============================================================================
-- TABELA: historico_pontos
-- Registro imutável de cada evento que gera ou remove pontos de um usuário.
-- =============================================================================
CREATE TABLE IF NOT EXISTS historico_pontos (
    id              UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id      UUID          NOT NULL,               -- FK para auth.users do Supabase
    pontos          INTEGER       NOT NULL,               -- Positivo = ganho, Negativo = perda
    tipo_atividade  VARCHAR(50)   NOT NULL,               -- 'quiz_completo', 'login_diario', etc.
    descricao       TEXT,                                 -- Detalhe legível do evento
    referencia_id   UUID,                                 -- ID do objeto origem (ex: id do quiz)
    criado_em       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT historico_pontos_usuario_fk
        FOREIGN KEY (usuario_id) REFERENCES auth.users(id) ON DELETE CASCADE,

    CONSTRAINT historico_tipo_check CHECK (
        tipo_atividade IN (
            'quiz_completo', 'login_diario', 'streak_bonus',
            'conquista_desbloqueada', 'nivel_atingido', 'penalidade', 'outro'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_historico_usuario    ON historico_pontos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_historico_criado_em  ON historico_pontos(criado_em DESC);
CREATE INDEX IF NOT EXISTS idx_historico_atividade  ON historico_pontos(tipo_atividade);

COMMENT ON TABLE  historico_pontos                IS 'Log imutável de todos os eventos de pontuação. Nunca deve ser deletado ou alterado.';
COMMENT ON COLUMN historico_pontos.pontos         IS 'Delta de pontos do evento. Pode ser negativo (penalidade).';
COMMENT ON COLUMN historico_pontos.referencia_id  IS 'ID opcional do recurso que originou o evento (quiz, desafio, etc.).';


-- =============================================================================
-- TABELA: ranking
-- Snapshot da pontuação total de cada usuário, atualizado por trigger.
-- =============================================================================
CREATE TABLE IF NOT EXISTS ranking (
    id              UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id      UUID          NOT NULL UNIQUE,        -- Um registro por usuário
    total_pontos    INTEGER       NOT NULL DEFAULT 0,
    nivel_id        INTEGER       NOT NULL DEFAULT 1,
    streak_atual    INTEGER       NOT NULL DEFAULT 0,     -- Dias consecutivos de atividade
    streak_maximo   INTEGER       NOT NULL DEFAULT 0,     -- Maior streak histórico
    ultimo_login    DATE,                                 -- Data do último evento de login
    posicao         INTEGER,                              -- Calculada via View/Function
    atualizado_em   TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    CONSTRAINT ranking_usuario_fk
        FOREIGN KEY (usuario_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    CONSTRAINT ranking_nivel_fk
        FOREIGN KEY (nivel_id)   REFERENCES nivel(id)      ON DELETE RESTRICT,

    CONSTRAINT ranking_total_pontos_check  CHECK (total_pontos  >= 0),
    CONSTRAINT ranking_streak_atual_check  CHECK (streak_atual  >= 0),
    CONSTRAINT ranking_streak_maximo_check CHECK (streak_maximo >= streak_atual)
);

CREATE INDEX IF NOT EXISTS idx_ranking_total_pontos ON ranking(total_pontos DESC);
CREATE INDEX IF NOT EXISTS idx_ranking_nivel        ON ranking(nivel_id);

COMMENT ON TABLE  ranking               IS 'Tabela de placar: mantém pontos totais, nível e streak de cada usuário.';
COMMENT ON COLUMN ranking.posicao       IS 'Posição no ranking global. Calculada dinamicamente via view vw_ranking_top.';
COMMENT ON COLUMN ranking.streak_atual  IS 'Número de dias consecutivos com ao menos uma atividade registrada.';


-- =============================================================================
-- TABELA: conquista
-- Instâncias de medalhas concedidas a usuários específicos.
-- =============================================================================
CREATE TABLE IF NOT EXISTS conquista (
    id           UUID          PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id   UUID          NOT NULL,
    medalha_id   UUID          NOT NULL,
    conquistado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT conquista_usuario_fk
        FOREIGN KEY (usuario_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    CONSTRAINT conquista_medalha_fk
        FOREIGN KEY (medalha_id) REFERENCES medalha(id)    ON DELETE RESTRICT,

    -- Cada medalha só pode ser concedida uma vez por usuário
    CONSTRAINT conquista_usuario_medalha_unique UNIQUE (usuario_id, medalha_id)
);

CREATE INDEX IF NOT EXISTS idx_conquista_usuario ON conquista(usuario_id);

COMMENT ON TABLE  conquista                IS 'Registro de medalhas conquistadas por cada usuário.';
COMMENT ON COLUMN conquista.conquistado_em IS 'Timestamp exato em que a medalha foi concedida.';


-- =============================================================================
-- VIEW: vw_ranking_top
-- Ranking global com posição calculada dinamicamente via RANK().
-- =============================================================================
CREATE OR REPLACE VIEW vw_ranking_top AS
SELECT
    r.usuario_id,
    u.email                                          AS email_usuario,
    r.total_pontos,
    r.streak_atual,
    r.streak_maximo,
    n.nome                                           AS nivel_nome,
    n.icone_url                                      AS nivel_icone,
    RANK() OVER (ORDER BY r.total_pontos DESC)       AS posicao
FROM
    ranking      r
    JOIN auth.users u ON u.id = r.usuario_id
    JOIN nivel    n ON n.id = r.nivel_id;

COMMENT ON VIEW vw_ranking_top IS 'Visão do ranking global com posição calculada por RANK(). Usar para Top-N queries.';


-- =============================================================================
-- FUNCTION + TRIGGER: fn_atualizar_ranking_ao_inserir_pontos
-- Ao inserir em historico_pontos, atualiza automaticamente ranking.total_pontos
-- e recalcula o nível do usuário.
-- =============================================================================
CREATE OR REPLACE FUNCTION fn_atualizar_ranking_ao_inserir_pontos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_novo_total  INTEGER;
    v_novo_nivel  INTEGER;
BEGIN
    -- 1. Garante que existe uma linha em ranking para o usuário
    INSERT INTO ranking (usuario_id, total_pontos, nivel_id)
    VALUES (NEW.usuario_id, 0, 1)
    ON CONFLICT (usuario_id) DO NOTHING;

    -- 2. Atualiza o total de pontos somando o delta do evento
    UPDATE ranking
    SET
        total_pontos  = GREATEST(0, total_pontos + NEW.pontos),
        atualizado_em = NOW()
    WHERE usuario_id = NEW.usuario_id
    RETURNING total_pontos INTO v_novo_total;

    -- 3. Determina o nível correspondente ao novo total de XP
    SELECT id INTO v_novo_nivel
    FROM nivel
    WHERE xp_minimo <= v_novo_total
      AND (xp_maximo IS NULL OR xp_maximo > v_novo_total)
    ORDER BY xp_minimo DESC
    LIMIT 1;

    -- 4. Atualiza o nível (se um nível válido foi encontrado)
    IF v_novo_nivel IS NOT NULL THEN
        UPDATE ranking
        SET nivel_id = v_novo_nivel
        WHERE usuario_id = NEW.usuario_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_atualizar_ranking
AFTER INSERT ON historico_pontos
FOR EACH ROW
EXECUTE FUNCTION fn_atualizar_ranking_ao_inserir_pontos();

COMMENT ON FUNCTION fn_atualizar_ranking_ao_inserir_pontos IS
    'Trigger: ao inserir em historico_pontos, recalcula total_pontos e nivel_id em ranking.';


-- =============================================================================
-- FUNCTION + TRIGGER: fn_atualizar_streak
-- Atualiza o streak diário quando um evento de 'login_diario' é inserido.
-- =============================================================================
CREATE OR REPLACE FUNCTION fn_atualizar_streak()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_ultimo_login  DATE;
    v_hoje          DATE := CURRENT_DATE;
BEGIN
    -- Só processa eventos de login diário
    IF NEW.tipo_atividade <> 'login_diario' THEN
        RETURN NEW;
    END IF;

    -- Recupera o último login registrado
    SELECT ultimo_login INTO v_ultimo_login
    FROM ranking
    WHERE usuario_id = NEW.usuario_id;

    -- Se já fez login hoje, não altera o streak
    IF v_ultimo_login = v_hoje THEN
        RETURN NEW;
    END IF;

    UPDATE ranking
    SET
        -- Streak continua apenas se o último login foi ontem
        streak_atual  = CASE
                            WHEN v_ultimo_login = v_hoje - INTERVAL '1 day'
                            THEN streak_atual + 1
                            ELSE 1
                        END,
        -- Atualiza o recorde histórico se necessário
        streak_maximo = GREATEST(
                            streak_maximo,
                            CASE
                                WHEN v_ultimo_login = v_hoje - INTERVAL '1 day'
                                THEN streak_atual + 1
                                ELSE 1
                            END
                        ),
        ultimo_login  = v_hoje,
        atualizado_em = NOW()
    WHERE usuario_id = NEW.usuario_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_atualizar_streak
AFTER INSERT ON historico_pontos
FOR EACH ROW
EXECUTE FUNCTION fn_atualizar_streak();

COMMENT ON FUNCTION fn_atualizar_streak IS
    'Trigger: ao registrar login_diario, incrementa streak_atual ou reseta para 1 se houve quebra.';


-- =============================================================================
-- DADOS INICIAIS: Níveis e Medalhas padrão
-- =============================================================================

-- Níveis
INSERT INTO nivel (nome, xp_minimo, xp_maximo, icone_url) VALUES
    ('Iniciante',    0,    499,  '/icons/nivel/iniciante.svg'),
    ('Aprendiz',     500,  1499, '/icons/nivel/aprendiz.svg'),
    ('Intermediário',1500, 3999, '/icons/nivel/intermediario.svg'),
    ('Avançado',     4000, 7999, '/icons/nivel/avancado.svg'),
    ('Expert',       8000, NULL, '/icons/nivel/expert.svg')
ON CONFLICT (nome) DO NOTHING;

-- Medalhas padrão
INSERT INTO medalha (nome, descricao, tipo, icone_url) VALUES
    ('Primeira Conquista',   'Complete sua primeira atividade.',              'conquista', '/icons/medalha/primeira.svg'),
    ('Semana Perfeita',      'Mantenha um streak de 7 dias consecutivos.',    'streak',    '/icons/medalha/semana.svg'),
    ('Mês Dedicado',         'Mantenha um streak de 30 dias consecutivos.',   'streak',    '/icons/medalha/mes.svg'),
    ('Top 10',               'Alcance o Top 10 no ranking geral.',            'ranking',   '/icons/medalha/top10.svg'),
    ('Líder Supremo',        'Alcance a 1ª posição no ranking geral.',        'ranking',   '/icons/medalha/lider.svg'),
    ('Centurião',            'Acumule 100 pontos ou mais.',                   'especial',  '/icons/medalha/centuriao.svg')
ON CONFLICT (nome) DO NOTHING;
