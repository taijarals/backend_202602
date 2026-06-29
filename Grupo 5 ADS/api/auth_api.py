"""
Rotas de autenticação: login e cadastro via Supabase Auth.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Body

from database.connection import supabase

router = APIRouter(prefix="/auth")


@router.post("/login")
def login(dados=Body(...)):
    try:
        resposta = supabase.auth.sign_in_with_password({
            "email": dados["email"],
            "password": dados["senha"]
        })

        return {
            "token": resposta.session.access_token,
            "usuario_id": resposta.user.id
        }

    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"erro": "Email ou senha incorretos."}
        )


@router.post("/cadastrar")
def cadastrar(dados=Body(...)):
    try:
        resposta = supabase.auth.sign_up({
            "email": dados["email"],
            "password": dados["senha"],
            "options": {
                "data": {"nome": dados.get("nome", "")}
            }
        })

        if not resposta.user:
            return JSONResponse(
                status_code=400,
                content={"erro": "Não foi possível criar a conta."}
            )

        return {"mensagem": "Conta criada com sucesso."}

    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"erro": str(e)}
        )
