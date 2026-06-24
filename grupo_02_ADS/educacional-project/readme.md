# 🏆 Sistema de Desafios Educacionais

## 📖 Descrição

Projeto desenvolvido utilizando arquitetura em camadas com FastAPI e SQLite.

O sistema permite que professores criem desafios educacionais e que alunos participem das atividades, recebam pontuações e acompanhem sua posição no ranking geral.

O objetivo é simular uma plataforma educacional gamificada utilizando conceitos modernos de desenvolvimento backend.

---

## 🎯 Funcionalidades

### 👨‍🏫 Professor

- Cadastrar desafios
- Visualizar desafios
- Acompanhar ranking dos alunos

### 👨‍🎓 Aluno

- Cadastrar aluno
- Visualizar desafios disponíveis
- Enviar respostas para desafios
- Receber pontuação
- Acompanhar ranking geral

### ⚙️ Sistema

- Registro de pontuação
- Ranking automático
- Armazenamento em banco de dados SQLite
- API REST documentada automaticamente

---

## 🏗️ Arquitetura

O projeto foi desenvolvido utilizando arquitetura em camadas.

```text
Cliente
   ↓
FastAPI
   ↓
Services
   ↓
Repositories
   ↓
Providers
   ↓
SQLite
```

### Camadas

#### API

Responsável pelos endpoints da aplicação.

#### Services

Contém as regras de negócio.

#### Repositories

Responsável pela comunicação entre as regras de negócio e os provedores de dados.

#### Providers

Implementa a estratégia de acesso ao banco de dados.

#### Database

Responsável pela persistência dos dados.

---

## 📁 Estrutura do Projeto

```text
projeto_educacional/

├── api/
├── services/
├── repositories/
├── providers/
├── models/
├── database/
├── docs/
├── pages/

├── main.py
└── README.md
```

---

## 🗄️ Entidades Implementadas

### Aluno

```json
{
  "nome": "Breno"
}
```

### Desafio

```json
{
  "titulo": "Lista de Cálculo",
  "pontos": 50
}
```

### Pontuação

```json
{
  "aluno_id": 1,
  "pontos": 50
}
```

### Submissão

```json
{
  "aluno_id": 1,
  "desafio_id": 1,
  "resposta": "Minha solução para o desafio"
}
```

---

## 🌐 Endpoints Disponíveis

### Alunos

| Método | Endpoint |
|----------|----------|
| GET | /alunos |
| POST | /alunos |

### Desafios

| Método | Endpoint |
|----------|----------|
| GET | /desafios |
| POST | /desafios |

### Submissões

| Método | Endpoint |
|----------|----------|
| POST | /submissoes |

### Pontuação

| Método | Endpoint |
|----------|----------|
| POST | /pontuacao |

### Ranking

| Método | Endpoint |
|----------|----------|
| GET | /ranking |

---

## 🚀 Como Executar

### Instalar dependências

```bash
pip install fastapi
pip install uvicorn
pip install pydantic
pip install streamlit
```

### Executar API

```bash
uvicorn main:app --reload
```

### Acessar documentação

```text
http://127.0.0.1:8000/docs
```

---

## 💾 Banco de Dados

Banco utilizado:

- SQLite

O banco é criado automaticamente ao iniciar a aplicação.

---

## 🔄 Provider Pattern

O projeto utiliza o padrão Provider Pattern para abstrair o acesso ao banco de dados.

Atualmente foi implementado o SQLiteProvider, permitindo futura substituição por outras tecnologias como PostgreSQL ou Supabase sem alterar as demais camadas da aplicação.

---

## 🛠️ Tecnologias Utilizadas

- Python
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- Streamlit

---

## 👨‍💻 Autor

Projeto desenvolvido para a disciplina de Desenvolvimento Backend.