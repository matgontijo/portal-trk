# trk-universe/backend/app/routers/usuarios.py
# Gestão de usuários e da MATRIZ DE PERMISSÕES (o gestor define o que cada um vê/edita).

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Departamento, User
from ..permissions import (
    MODULOS, modulos_acessiveis, permissoes_efetivas, require_permission,
)
from ..schemas import UserIn, UserOut, UserUpdate
from ..security import hash_senha
from .auth import _user_out

router = APIRouter()

EDITAR = require_permission("usuarios", "editar")
VER = require_permission("usuarios", "ver")


@router.get("", response_model=list[UserOut])
def listar(db: Session = Depends(get_db), _=Depends(VER)):
    users = db.execute(select(User).order_by(User.nome)).scalars().all()
    return [_user_out(u) for u in users]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def criar(dados: UserIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    if db.execute(select(User).where(User.email == dados.email)).scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")
    dep = db.get(Departamento, dados.departamento_id) if dados.departamento_id else None
    # Se não vierem permissões explícitas, herda do departamento
    permissoes = dados.permissoes if dados.permissoes is not None else (dict(dep.permissoes_padrao) if dep else {})
    user = User(
        nome=dados.nome, email=dados.email, senha_hash=hash_senha(dados.senha),
        cargo=dados.cargo, departamento_id=dados.departamento_id,
        permissoes=permissoes, avatar_cor=dep.cor if dep else "#171717",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_out(user)


@router.get("/{user_id}/permissoes")
def obter_permissoes(user_id: str, db: Session = Depends(get_db), _=Depends(VER)):
    """Permissões efetivas de um usuário + catálogo de módulos (para a matriz)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return {
        "usuario": _user_out(user),
        "permissoes": permissoes_efetivas(user),
        "modulos": MODULOS,
        "bloqueado_edicao": user.cargo == "diretor",  # diretor tem acesso total fixo
    }


@router.put("/{user_id}", response_model=UserOut)
def atualizar(user_id: str, dados: UserUpdate, db: Session = Depends(get_db), _=Depends(EDITAR)):
    """Atualiza dados e/ou a MATRIZ de permissões do usuário."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    if dados.nome is not None:
        user.nome = dados.nome
    if dados.cargo is not None:
        user.cargo = dados.cargo
    if dados.departamento_id is not None:
        user.departamento_id = dados.departamento_id
    if dados.permissoes is not None:
        user.permissoes = dados.permissoes
    if dados.ativo is not None:
        user.ativo = dados.ativo
    if dados.senha:
        user.senha_hash = hash_senha(dados.senha)
    db.commit()
    db.refresh(user)
    return _user_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(user_id: str, db: Session = Depends(get_db), _=Depends(EDITAR)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    db.delete(user)
    db.commit()


@router.get("/{user_id}/preview-acesso")
def preview_acesso(user_id: str, db: Session = Depends(get_db), _=Depends(VER)):
    """Mostra como ficaria o menu do usuário (transparência do bloqueio por setor)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return {"modulos_acessiveis": modulos_acessiveis(user)}
