# EduGame Platform

**Plataforma Educacional Gamificada**

Uma plataforma educacional completa baseada em metodologias ativas de aprendizagem, com suporte a desafios, mini-provas, gamificacao, formacao de equipes e missoes educacionais.

## Arquitetura

```
Frontend (Streamlit)
        |
        v
    HTTP/JSON
        |
        v
    FastAPI (Backend)
        |
        v
    Services Layer
        |
        v
    Provider Pattern
        |
        v
    Repositories Layer
        |
        v
    Supabase/PostgreSQL
```

## Estrutura do Projeto

```
project/
├── api/                    # REST API endpoints (FastAPI)
│   ├── auth.py            # Autenticacao
│   ├── users.py           # Usuarios
│   ├── disciplinas.py     # Disciplinas
│   ├── turmas.py          # Turmas/Classes
│   ├── desafios.py        # Desafios/Submissoes
│   ├── miniprovas.py      # Mini Provas
│   ├── gamificacao.py     # Gamificacao
│   ├── equipes.py         # Equipes
│   ├── missoes.py         # Missoes
│   └── enquetes.py        # Enquetes/Polls
├── database/              # Configuracao do banco
│   └── config.py
├── docs/                  # Documentacao
├── models/                # Pydantic models
│   ├── user.py
│   ├── disciplina.py
│   ├── turma.py
│   ├── desafio.py
│   ├── miniprova.py
│   ├── gamificacao.py
│   ├── equipe.py
│   ├── missao.py
│   └── enquete.py
├── pages/                 # Streamlit pages
│   ├── styles.py         # CSS Dark Theme
│   ├── components.py     # UI Components
│   ├── dashboard.py
│   ├── challenges_page.py
│   ├── gamification_page.py
│   ├── miniprovas_page.py
│   ├── teams_page.py
│   ├── missions_page.py
│   └── polls_page.py
├── providers/             # Provider Pattern
│   └── base.py
├── repositories/         # Data access layer
│   ├── user_repository.py
│   ├── disciplina_repository.py
│   ├── turma_repository.py
│   ├── desafio_repository.py
│   ├── miniprova_repository.py
│   ├── gamificacao_repository.py
│   ├── equipe_repository.py
│   ├── missao_repository.py
│   └── enquete_repository.py
├── services/              # Business logic
│   ├── auth_service.py
│   ├── user_service.py
│   ├── disciplina_service.py
│   ├── turma_service.py
│   ├── desafio_service.py
│   ├── miniprova_service.py
│   ├── gamificacao_service.py
│   ├── equipe_service.py
│   ├── missao_service.py
│   └── enquete_service.py
├── utils/                 # Utilities
│   ├── helpers.py
│   └── exceptions.py
├── Home.py                # Streamlit entry point
├── main.py                # FastAPI entry point
└── requirements.txt
```

## Tecnologias

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Banco de Dados**: PostgreSQL (Supabase)
- **Autenticacao**: Supabase Auth + JWT
- **API**: REST

## Modulos

### 1. Sistema de Desafios
- Criacao e gestao de desafios
- Submissoes de alunos
- Sistema de votacao entre pares
- Rankings por desafio

### 2. Mini-Provas
- Provas rapidas com cronometro
- Correcao automatica
- Multiplas tentativas
- Historico de tentativas

### 3. Gamificacao
- Sistema de pontos
- Medalhas e conquistas
- Niveis de progressao
- Leaderboards

### 4. Feedback Instantaneo
- Enquetes em tempo real
- Votacao anonima ou identificada
- Estatisticas e graficos

### 5. Formacao de Equipes
- Criacao manual ou automatica
- Distribuicao equilibrada
- Gerenciamento de membros

### 6. Missoes Educacionais
- Jornadas de aprendizado
- Etapas progressivas
- Recompensas por conclusao

## Instalacao

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais Supabase

# Executar backend
uvicorn main:app --reload

# Executar frontend (em outro terminal)
streamlit run Home.py
```

## Variaveis de Ambiente

```
SUPABASE_URL=sua_url_supabase
SUPABASE_ANON_KEY=sua_chave_anon
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service
SECRET_KEY=sua_chave_secreta
```

## API Endpoints

### Autenticacao
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Usuario atual

### Usuarios
- `GET /api/v1/users` - Listar usuarios
- `GET /api/v1/users/{id}` - Obter usuario
- `PUT /api/v1/users/{id}` - Atualizar usuario
- `GET /api/v1/users/{id}/stats` - Estatisticas

### Disciplinas
- `POST /api/v1/disciplinas` - Criar disciplina
- `GET /api/v1/disciplinas` - Listar disciplinas
- `GET /api/v1/disciplinas/{id}` - Obter disciplina
- `PUT /api/v1/disciplinas/{id}` - Atualizar

### Turmas
- `POST /api/v1/turmas` - Criar turma
- `GET /api/v1/turmas` - Listar turmas
- `POST /api/v1/turmas/join/{codigo}` - Entrar com codigo
- `GET /api/v1/turmas/{id}/students` - Listar alunos

### Desafios
- `POST /api/v1/desafios` - Criar desafio
- `GET /api/v1/desafios` - Listar desafios
- `POST /api/v1/desafios/submissoes` - Submeter
- `POST /api/v1/desafios/submissoes/{id}/grade` - Avaliar

### Mini Provas
- `POST /api/v1/mini-provas` - Criar prova
- `GET /api/v1/mini-provas` - Listar provas
- `POST /api/v1/mini-provas/{id}/start` - Iniciar tentativa
- `POST /api/v1/mini-provas/tentativas/{id}/finish` - Finalizar

### Gamificacao
- `GET /api/v1/gamificacao/leaderboard` - Ranking
- `GET /api/v1/gamificacao/stats` - Estatisticas
- `GET /api/v1/gamificacao/levels` - Niveis
- `GET /api/v1/gamificacao/medalhas` - Medalhas

### Equipes
- `POST /api/v1/equipes` - Criar equipe
- `GET /api/v1/equipes/turma/{id}` - Equipes da turma
- `POST /api/v1/equipes/auto-create` - Formacao automatica
- `POST /api/v1/equipes/{id}/members` - Adicionar membro

### Missoes
- `POST /api/v1/missoes` - Criar missao
- `GET /api/v1/missoes/available` - Missoes disponiveis
- `POST /api/v1/missoes/{id}/etapas/{etapa_id}/complete` - Completar etapa

### Enquetes
- `POST /api/v1/enquetes` - Criar enquete
- `GET /api/v1/enquetes/active` - Enquetes ativas
- `POST /api/v1/enquetes/{id}/vote` - Votar
- `GET /api/v1/enquetes/{id}/stats` - Estatisticas

## Documentacao da API

Acesse `http://localhost:8000/api/v1/docs` para a documentacao interativa (Swagger UI).

## Licenca

MIT License
