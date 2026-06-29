"""
Responsável por criar a conexão com o Supabase.

Toda a aplicação utilizará esta conexão.

Ele funciona para outras coisas também, é claro com a alteração das variaveis, é otimo para integração geral, não pelo supabase, eu tentei colocar conexão por ia, bem, acho que ainda não entendi o suficiente (* ￣︿￣)(Carol)
"""

# Biblioteca para ler variáveis do arquivo .env
from dotenv import load_dotenv

# Biblioteca para acessar variáveis de ambiente
import os

# Cliente oficial do Supabase
from supabase import create_client, Client

# Carrega o arquivo .env
load_dotenv()

# =====================================
# Variáveis de ambiente
# =====================================

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

USUARIO_TESTE_ID = os.getenv("USUARIO_TESTE_ID")

# =====================================
# Validação
# =====================================

if not SUPABASE_URL:
    raise Exception("SUPABASE_URL não encontrada.")

if not SUPABASE_KEY:
    raise Exception("SUPABASE_KEY não encontrada.")

# =====================================
# Cliente do Supabase
# =====================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)