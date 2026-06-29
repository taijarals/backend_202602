"""
Script de inicialização automática do Mini Provas.

Instala as dependências automaticamente e inicia o servidor.

Execução:
  python run.py

Ou clique duas vezes em:
  start.bat  (Windows)
  start.sh   (Linux/Mac)
"""

import subprocess
import sys
import os


def instalar_dependencias():
    print("Verificando dependências...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            stdout=subprocess.DEVNULL
        )
        print("Dependências OK.")
    except subprocess.CalledProcessError:
        print("Erro ao instalar dependências. Verifique o arquivo requirements.txt.")
        sys.exit(1)


def iniciar_servidor():
    print("\n Servidor iniciando em: http://127.0.0.1:8000")
    print("Abra o link acima no navegador.")
    print("Pressione CTRL+C para parar.\n")
    subprocess.call([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])


if __name__ == "__main__":
    # Garante execução sempre da pasta do projeto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    instalar_dependencias()
    iniciar_servidor()
