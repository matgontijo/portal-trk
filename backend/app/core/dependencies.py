# backend/app/core/dependencies.py
# Dependências FastAPI reutilizáveis em todas as rotas.
# Responsabilidades:
#   - get_db: fornece sessão async do banco
#   - get_redis: fornece conexão Redis
#   - get_current_user: extrai e valida JWT do header Authorization
#   - require_role: decorator de autorização baseado em role (RBAC)

from functools import wraps
from typing import Annotated, Callable
from uuid import UUID

import jwt
import redis.asyncio as aioredis
from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import verificar_token
from app.db.session import async_session_factory

# ════════════════════════════════════════════════════════════════
# BANCO DE DADOS
# ════════════════════════════════════════════════════════════════


async def get_db() -> AsyncSession:
    """
    Dependency que fornece uma sessão async do banco.
    A sessão é fechada automaticamente ao final da requisição.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ════════════════════════════════════════════════════════════════
# REDIS
# ════════════════════════════════════════════════════════════════

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """
    Dependency que fornece conexão Redis.
    Usa pool de conexões singleton para eficiência.
    """
    global _redis_pool
    if _redis_pool is None:
        settings = get_settings()
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


async def fechar_redis() -> None:
    """Fecha o pool Redis no shutdown da aplicação."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


# ════════════════════════════════════════════════════════════════
# AUTENTICAÇÃO — EXTRAIR USUÁRIO DO JWT
# ════════════════════════════════════════════════════════════════


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Extrai o usuário autenticado do header Authorization: Bearer <token>.
    Valida o JWT RS256 e busca o usuário no banco.
    Retorna o objeto User completo.
    """
    # Importação tardia para evitar circular
    from app.db.models.user import User

    # Extrair token do header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]

    try:
        payload = verificar_token(token, tipo_esperado="access")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem identificação de usuário",
        )

    # Buscar usuário no banco
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada — entre em contato com o administrador",
        )

    return user


# ════════════════════════════════════════════════════════════════
# AUTORIZAÇÃO — RBAC POR ROLE
# ════════════════════════════════════════════════════════════════


def require_role(roles_permitidas: list[str]):
    """
    Dependency factory que verifica se o usuário tem uma das roles permitidas.
    Uso: Depends(require_role(["admin", "gestor"]))

    Hierarquia implícita:
      admin > gestor > funcionario
    """

    async def _verificar_role(
        request: Request,
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in roles_permitidas:
            # Registrar tentativa de acesso não autorizado
            import structlog
            logger = structlog.get_logger()
            logger.warning(
                "acesso_negado",
                user_id=str(current_user.id),
                role=current_user.role,
                roles_necessarias=roles_permitidas,
                path=request.url.path,
                method=request.method,
                ip=request.client.host if request.client else "unknown",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso",
            )
        return current_user

    return _verificar_role


# ─── Type aliases para uso nas rotas ───
CurrentUser = Annotated[object, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisConn = Annotated[aioredis.Redis, Depends(get_redis)]
