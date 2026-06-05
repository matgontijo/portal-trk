# trk-universe/backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..permissions import get_current_user, modulos_acessiveis, permissoes_efetivas
from ..schemas import LoginIn, MeOut, TokenOut, UserOut
from ..security import criar_token, verificar_senha

router = APIRouter()


def _user_out(u: User) -> UserOut:
    return UserOut(
        id=u.id, nome=u.nome, email=u.email, cargo=u.cargo,
        departamento_id=u.departamento_id,
        departamento_nome=u.departamento.nome if u.departamento else None,
        avatar_cor=u.avatar_cor, ativo=u.ativo, created_at=u.created_at,
    )


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == dados.email)).scalar_one_or_none()
    if not user or not verificar_senha(dados.senha, user.senha_hash) or not user.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    token = criar_token({"sub": user.id, "cargo": user.cargo})
    return TokenOut(
        token=token, usuario=_user_out(user),
        permissoes=permissoes_efetivas(user), modulos_acessiveis=modulos_acessiveis(user),
    )


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(
        usuario=_user_out(user),
        permissoes=permissoes_efetivas(user),
        modulos_acessiveis=modulos_acessiveis(user),
    )
