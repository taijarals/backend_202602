# Plataforma Educacional - Módulo de Gamificação e Mini-Provas

## 1. Objetivo

Este projeto tem como objetivo desenvolver um backend educacional baseado em metodologias ativas, utilizando arquitetura em camadas, API REST, banco de dados relacional e frontend integrado.

O módulo implementado pelo grupo é focado em **Gamificação**, incluindo cadastro de alunos, professores, disciplinas, turmas, pontuação, níveis, medalhas, rankings, dashboards e um sistema de **mini-provas gamificadas**.

A proposta do sistema é incentivar a participação dos alunos por meio de recompensas, pontuação e acompanhamento de desempenho.

---

## 2. Tecnologias Utilizadas

* Python
* FastAPI
* Streamlit
* PostgreSQL
* Supabase
* Pydantic
* Psycopg2
* Pandas
* Requests
* Git/GitHub

---

## 3. Arquitetura do Projeto

O projeto segue uma arquitetura organizada em camadas, separando responsabilidades entre interface, API, regras de negócio, acesso a dados e persistência.

```text
Streamlit
    ↓
FastAPI
    ↓
Services
    ↓
Repositories
    ↓
Providers
    ↓
Supabase/PostgreSQL
```

### Fluxo da Aplicação

```text
Usuário
  ↓
Frontend Streamlit
  ↓
Requisição HTTP/JSON
  ↓
API FastAPI
  ↓
Camada de Services
  ↓
Camada de Repositories
  ↓
Provider de Banco
  ↓
Supabase/PostgreSQL
```

---

## 4. Estrutura de Pastas

```text
project/
│
├── api/
│   └── main.py
│
├── database/
│   └── schema.sql
│
├── docs/
│   └── README.md
│
├── models/
│   ├── gamificacao_models.py
│   └── provas_models.py
│
├── pages/
│   └── app.py
│
├── providers/
│   ├── base.py
│   ├── factory.py
│   └── sql_provider.py
│
├── repositories/
│   ├── gamificacao_repository.py
│   └── provas_repository.py
│
├── services/
│   ├── gamificacao_service.py
│   └── provas_service.py
│
├── utils/
│
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 5. Organização em Camadas

### pages/

Contém a interface do usuário feita com Streamlit.

Responsável por:

* Cadastro de alunos
* Registro de atividades
* Dashboard do aluno
* Gestão acadêmica
* Mini-provas
* Ranking
* Estatísticas administrativas

---

### api/

Contém a API REST feita com FastAPI.

Responsável por receber requisições HTTP e retornar respostas em JSON.

---

### services/

Contém as regras de negócio do sistema.

Exemplos:

* Cálculo de pontuação
* Cálculo de nível
* Liberação de medalhas
* Correção de mini-provas
* Validação de vínculos entre aluno, turma, professor e disciplina

---

### repositories/

Contém as consultas SQL e o acesso aos dados.

Essa camada se comunica com o banco por meio do Provider.

---

### providers/

Implementa o Provider Pattern.

Essa camada permite trocar a estratégia de persistência sem alterar as demais partes do sistema.

---

### models/

Contém os modelos de entrada da API usando Pydantic.

Exemplos:

* Cadastro de aluno
* Cadastro de professor
* Cadastro de disciplina
* Cadastro de turma
* Registro de pontuação
* Cadastro de prova
* Cadastro de questão
* Envio de respostas da prova

---

### database/

Contém o script SQL para criação das tabelas no Supabase/PostgreSQL.

---

## 6. Provider Pattern

O projeto utiliza o **Provider Pattern** para desacoplar o acesso ao banco de dados.

A API e os serviços não acessam diretamente o banco. Eles usam o repositório, que usa o Provider.

```text
Service
  ↓
Repository
  ↓
Provider
  ↓
Banco de Dados
```

Com isso, se no futuro o projeto trocar PostgreSQL por outro tipo de persistência, a alteração fica concentrada na camada de Provider.

---

## 7. Entidades Globais

O roteiro da atividade exige as seguintes entidades globais:

```text
Aluno
Professor
Disciplina
Turma
Pontuação
```

Todas foram representadas no projeto.

### Aluno

Tabela responsável por armazenar os alunos cadastrados.

Campos principais:

```text
id
nome
email
```

---

### Professor

Tabela responsável por armazenar os professores.

Campos principais:

```text
id
nome
email
```

---

### Disciplina

Tabela responsável por armazenar as disciplinas.

Campos principais:

```text
id
nome
descricao
```

---

### Turma

Tabela responsável por relacionar professor e disciplina.

Campos principais:

```text
id
nome
professor_id
disciplina_id
```

---

### Pontuação

A pontuação é controlada pelas tabelas:

```text
progresso_alunos
historico_pontos
conquistas_medalhas
```

Essas tabelas armazenam os pontos totais, nível atual, streak, histórico de atividades e medalhas conquistadas.

---

## 8. Banco de Dados

O banco de dados utilizado é PostgreSQL hospedado no Supabase.

### Tabelas principais

```text
alunos
professores
disciplinas
turmas
turma_alunos
niveis
medalhas
progresso_alunos
historico_pontos
conquistas_medalhas
provas
questoes_prova
tentativas_prova
respostas_tentativa
```

---

## 9. Módulo de Gamificação

O módulo de gamificação permite:

* Cadastrar alunos
* Registrar atividades
* Atribuir pontos
* Calcular pontos totais
* Calcular nível do aluno
* Controlar streak de atividades
* Desbloquear medalhas
* Exibir ranking geral
* Exibir ranking semanal
* Exibir dashboard individual do aluno
* Exibir estatísticas administrativas

---

## 10. Sistema de Níveis

O sistema utiliza níveis baseados na pontuação total do aluno.

Exemplo:

```text
Nível 1 - Iniciante
Nível 2 - Explorador
Nível 3 - Veterano
Nível 4 - Mestre
Nível 5 - Lenda
```

Quando o aluno acumula pontos suficientes, ele sobe de nível automaticamente.

---

## 11. Sistema de Medalhas

O projeto possui medalhas que são desbloqueadas conforme o comportamento do aluno.

Exemplos:

```text
Primeiro Passo
Inabalável
```

A medalha **Primeiro Passo** é liberada quando o aluno registra sua primeira pontuação.

A medalha **Inabalável** é liberada quando o aluno atinge uma sequência de atividades.

---

## 12. Mini-Provas Gamificadas

Além da gamificação por atividades, o sistema possui um módulo de **mini-provas gamificadas**.

Esse módulo permite:

* Criar provas
* Cadastrar questões
* Definir alternativas A, B, C e D
* Definir resposta correta
* Permitir que o aluno responda a prova
* Corrigir automaticamente
* Calcular acertos
* Calcular percentual de desempenho
* Converter acertos em pontos
* Enviar os pontos para o sistema de gamificação
* Registrar tentativas do aluno
* Exibir estatísticas das provas

---

## 13. Fluxo das Mini-Provas

```text
Professor cria uma prova
        ↓
Professor cadastra questões
        ↓
Aluno responde a prova
        ↓
Sistema corrige automaticamente
        ↓
Sistema calcula acertos
        ↓
Acertos viram pontos
        ↓
Pontos entram na gamificação
        ↓
Ranking e dashboard são atualizados
```

---

## 14. Segurança e Qualidade

O projeto possui mecanismos simples de segurança e qualidade.

### Autenticação

A API utiliza um token simples via header:

```text
X-API-Token
```

O valor esperado é:

```text
chave-secreta-123
```

---

### Validação

A validação dos dados é feita com Pydantic.

Exemplos:

* Email válido
* Pontuação maior que zero
* Nome com tamanho mínimo
* IDs maiores que zero
* Resposta correta limitada a A, B, C ou D

---

### Logs

O sistema utiliza o módulo `logging` para registrar operações importantes.

Exemplos de ações registradas:

* Cadastro de aluno
* Cadastro de professor
* Cadastro de disciplina
* Cadastro de turma
* Registro de pontuação
* Evolução de nível
* Conquista de medalhas
* Criação de provas
* Resposta de mini-provas
* Consulta de rankings
* Consulta de estatísticas

---

### Tratamento de Erros

A API possui tratamento de erros para evitar respostas quebradas ou exposição direta de falhas internas.

Exemplo de resposta controlada:

```json
{
  "erro": "Erro interno",
  "mensagem": "Ocorreu um erro inesperado no servidor."
}
```

---

## 15. Endpoints da API

### Alunos

```http
POST /api/alunos
GET /api/alunos
GET /api/aluno/{aluno_id}
```

---

### Professores

```http
POST /api/professores
GET /api/professores
```

---

### Disciplinas

```http
POST /api/disciplinas
GET /api/disciplinas
```

---

### Turmas

```http
POST /api/turmas
GET /api/turmas
POST /api/turmas/alunos
GET /api/turmas/{turma_id}/alunos
```

---

### Pontuação

```http
POST /api/pontuar
```

---

### Ranking

```http
GET /api/ranking/geral
GET /api/ranking/semanal
```

---

### Mini-Provas

```http
POST /api/provas
GET /api/provas
POST /api/provas/questoes
GET /api/provas/{prova_id}/questoes
POST /api/provas/responder
GET /api/alunos/{aluno_id}/tentativas
GET /api/provas/estatisticas
```

---

### Estatísticas Administrativas

```http
GET /api/admin/estatisticas
```

---

## 16. Como Rodar o Projeto

### 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd NOME_DO_PROJETO
```

---

### 2. Criar ambiente virtual

```bash
python -m venv .venv
```

---

### 3. Ativar ambiente virtual

No Windows:

```bash
.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

---

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

Caso não exista o `requirements.txt`, instalar manualmente:

```bash
pip install fastapi uvicorn streamlit requests pandas psycopg2-binary python-dotenv email-validator pydantic
```

---

### 5. Configurar banco de dados

Criar um projeto no Supabase e executar o script SQL presente em:

```text
database/schema.sql
```

---

### 6. Configurar variável de ambiente

Criar um arquivo `.env` com base no `.env.example`.

Exemplo:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@db.SEUPROJETO.supabase.co:5432/postgres
DB_STRATEGY=sql
```

---

### 7. Rodar o backend

Na raiz do projeto:

```bash
uvicorn api.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

A documentação automática do FastAPI ficará disponível em:

```text
http://localhost:8000/docs
```

---

### 8. Rodar o frontend

Em outro terminal:

```bash
streamlit run pages/app.py
```

O Streamlit ficará disponível em:

```text
http://localhost:8501
```

---

## 17. Como Testar o Sistema

### Fluxo recomendado para demonstração

1. Cadastrar um professor.
2. Cadastrar uma disciplina.
3. Cadastrar uma turma.
4. Cadastrar um aluno.
5. Vincular o aluno à turma.
6. Registrar uma atividade para o aluno.
7. Verificar o dashboard do aluno.
8. Consultar o ranking.
9. Criar uma mini-prova.
10. Cadastrar questões na mini-prova.
11. Responder a prova como aluno.
12. Verificar os pontos recebidos.
13. Consultar tentativas da prova.
14. Consultar estatísticas administrativas.

---

## 18. Interface Streamlit

A interface possui as seguintes abas:

```text
Cadastrar Aluno
Registrar Atividade
Dashboard do Aluno
Alunos
Gestão Acadêmica
Mini-Provas
Ranking
Estatísticas
```

---

## 19. Diagrama Geral

```text
┌────────────────────┐
│     Streamlit      │
│    Frontend UI     │
└─────────┬──────────┘
          │ HTTP/JSON
          ↓
┌────────────────────┐
│      FastAPI       │
│      API REST      │
└─────────┬──────────┘
          ↓
┌────────────────────┐
│      Services      │
│ Regras de Negócio  │
└─────────┬──────────┘
          ↓
┌────────────────────┐
│    Repositories    │
│  Consultas SQL     │
└─────────┬──────────┘
          ↓
┌────────────────────┐
│     Providers      │
│ Provider Pattern   │
└─────────┬──────────┘
          ↓
┌────────────────────┐
│ Supabase/PostgreSQL│
│   Banco de Dados   │
└────────────────────┘
```

---

## 20. Critérios Atendidos

| Critério                | Situação                           |
| ----------------------- | ---------------------------------- |
| Arquitetura             | Atendido                           |
| Banco de Dados          | Atendido                           |
| Backend                 | Atendido                           |
| APIs REST               | Atendido                           |
| Organização             | Atendido                           |
| Documentação            | Atendido                           |
| Git/GitHub              | Atendido ao versionar corretamente |
| Segurança               | Parcialmente atendido com token    |
| Validação               | Atendido com Pydantic              |
| Logs                    | Atendido com logging               |
| Tratamento de Erros     | Atendido                           |
| Provider Pattern        | Atendido                           |
| Entidades Globais       | Atendido                           |
| Mini-Provas Gamificadas | Atendido                           |

---

## 21. Conclusão

Este projeto demonstra que backend não é apenas CRUD.

O sistema aplica conceitos de:

```text
Arquitetura em camadas
API REST
HTTP/JSON
Banco relacional
Supabase
Provider Pattern
Validação de dados
Tratamento de erros
Logs
Documentação
Gamificação
Mini-provas
Ranking
Dashboards
```

A solução se aproxima de um ambiente real de desenvolvimento profissional, com separação de responsabilidades, organização de código, integração com banco externo e funcionalidades completas para uma plataforma educacional gamificada.
