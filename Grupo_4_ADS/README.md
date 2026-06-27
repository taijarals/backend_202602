# Plataforma Educacional - Módulo de Gamificação

API desenvolvida com **FastAPI** para o gerenciamento de pontos, medalhas e ranking em um sistema universitário.

## 🚀 Como rodar o projeto

1. **Clone o repositório:**
   ```bash
   git clone <link-do-repositorio>
   cd Grupo_4_ADS

2. **Crie e ative um ambiente virtual (recomendado):**

    Bash
    python -m venv venv
    venv\Scripts\activate
    Instale as dependências:

3. **Instale as dependências:**
    Bash
    pip install -r requirements.txt
    Configure o ambiente:

Copie o arquivo .env.exemplo para um novo arquivo chamado .env e preencha com as credenciais.

4. **Inicie o servidor:**

    Bash
    python -m uvicorn main:app --reload