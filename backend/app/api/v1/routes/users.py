# backend/app/api/v1/routes/users.py
# Rotas de gestão de usuários do Portal TRK.
# Gestor+ pode criar/editar/desativar funcionários.
# Admin pode criar/editar gestores.

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import DbSession, require_role
from app.core.security import hash_senha
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_model=list[UserResponse])
async def listar_usuarios(
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Lista todos os usuários (gestor+ apenas)."""
    result = await db.execute(select(User).order_by(User.name))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    dados: UserCreate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """
    Cria novo usuário.
    Gestor pode criar apenas funcionários.
    Admin pode criar gestores e funcionários.
    """
    # Verificar permissão de criação de role
    if dados.role == "admin":
        raise HTTPException(status_code=403, detail="Não é possível criar outro admin")
    if dados.role == "gestor" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode criar gestores")

    # Verificar e-mail duplicado
    result = await db.execute(select(User).where(User.email == dados.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = User(
        name=dados.name,
        email=dados.email,
        password_hash=hash_senha(dados.password),
        role=dados.role,
        phone_whatsapp=dados.phone_whatsapp,
        sector=dados.sector,
    )
    db.add(user)
    await db.flush()

    logger.info("usuario_criado", user_id=str(user.id), role=user.role, por=str(current_user.id))
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def obter_usuario(
    user_id: UUID,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Obtém detalhes de um usuário específico."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def atualizar_usuario(
    user_id: UUID,
    dados: UserUpdate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Atualiza dados de um usuário."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Gestor não pode editar admins ou outros gestores
    if current_user.role == "gestor" and user.role in ["admin", "gestor"]:
        raise HTTPException(status_code=403, detail="Sem permissão para editar este usuário")

    # Aplicar atualizações
    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(user, campo, valor)

    await db.flush()
    logger.info("usuario_atualizado", user_id=str(user_id), por=str(current_user.id))
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/desativar")
async def desativar_usuario(
    user_id: UUID,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Desativa um usuário (soft delete funcional)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível desativar a si mesmo")

    user.is_active = False
    logger.info("usuario_desativado", user_id=str(user_id), por=str(current_user.id))
    return {"message": "Usuário desativado com sucesso"}
