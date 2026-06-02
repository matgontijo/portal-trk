# backend/app/api/v1/routes/auth.py
# Rotas de autenticação do Portal TRK.
# Login, refresh, logout, esqueci a senha, reset de senha.

from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update

from app.core.config import get_settings
from app.core.dependencies import DbSession, RedisConn, get_current_user
from app.core.security import (
    criar_access_token,
    criar_refresh_token,
    gerar_token_reset,
    hash_senha,
    hash_token,
    verificar_senha,
    verificar_token,
)
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import SuccessMessage

router = APIRouter()
logger = structlog.get_logger()

# Tempo de lockout após falhas (em segundos)
LOCKOUT_DURATION = 900  # 15 minutos
MAX_FALHAS = 5


@router.post("/login", response_model=TokenResponse)
async def login(
    dados: LoginRequest,
    request: Request,
    response: Response,
    db: DbSession,
    redis: RedisConn,
):
    """
    Autentica usuário com e-mail e senha.
    Retorna access token no body e refresh token via cookie httpOnly.
    Rate limited: 5 tentativas por minuto (via middleware).
    Lockout: 5 falhas → conta bloqueada 15min.
    """
    settings = get_settings()

    # Verificar lockout
    lockout_key = f"lockout:{dados.email}"
    try:
        if await redis.get(lockout_key):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Conta temporariamente bloqueada. Tente novamente em 15 minutos.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("redis_error_lockout", error=str(e))

    # Buscar usuário
    result = await db.execute(select(User).where(User.email == dados.email))
    user = result.scalar_one_or_none()

    if user is None or not verificar_senha(dados.password, user.password_hash):
        # Incrementar falhas
        falhas_key = f"login_falhas:{dados.email}"
        try:
            falhas = await redis.incr(falhas_key)
            await redis.expire(falhas_key, LOCKOUT_DURATION)

            if falhas >= MAX_FALHAS:
                await redis.setex(lockout_key, LOCKOUT_DURATION, "1")
                logger.warning("conta_bloqueada", email=dados.email, ip=request.client.host)
        except Exception as e:
            logger.warning("redis_error_falhas", error=str(e))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada — entre em contato com o administrador",
        )

    # Limpar falhas
    try:
        await redis.delete(f"login_falhas:{dados.email}")
    except Exception:
        pass

    # Gerar tokens
    token_data = {"sub": str(user.id), "role": user.role, "name": user.name}
    access_token = criar_access_token(token_data)
    refresh_token = criar_refresh_token(token_data)

    # Salvar refresh token (hash) no banco
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.add(rt)

    # Definir cookie httpOnly com refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )

    logger.info("login_sucesso", user_id=str(user.id), ip=request.client.host)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: DbSession,
    redis: RedisConn,
):
    """
    Renova o access token usando o refresh token do cookie.
    Emite novo refresh token (rotation) para segurança.
    """
    settings = get_settings()

    # Obter refresh token do cookie
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token não encontrado")

    try:
        payload = verificar_token(token, tipo_esperado="refresh")
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    # Verificar se o token não foi revogado
    token_h = hash_token(token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_h,
            RefreshToken.revoked_at.is_(None),
        )
    )
    rt = result.scalar_one_or_none()

    if rt is None:
        raise HTTPException(status_code=401, detail="Refresh token revogado")

    # Revogar o token atual (rotation)
    rt.revoked_at = datetime.now(timezone.utc)

    # Buscar usuário
    result = await db.execute(select(User).where(User.id == rt.user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    # Emitir novos tokens
    token_data = {"sub": str(user.id), "role": user.role, "name": user.name}
    new_access = criar_access_token(token_data)
    new_refresh = criar_refresh_token(token_data)

    # Salvar novo refresh token
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.add(new_rt)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=new_access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=SuccessMessage)
async def logout(
    request: Request,
    response: Response,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Revoga o refresh token e limpa o cookie."""
    token = request.cookies.get("refresh_token")
    if token:
        token_h = hash_token(token)
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_h)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    response.delete_cookie("refresh_token", path="/api/v1/auth")
    logger.info("logout", user_id=str(current_user.id))
    return SuccessMessage(message="Logout realizado com sucesso")


@router.post("/forgot-password", response_model=SuccessMessage)
async def forgot_password(
    dados: ForgotPasswordRequest,
    db: DbSession,
    redis: RedisConn,
):
    """
    Envia token de reset de senha por e-mail.
    Retorna sucesso mesmo se o e-mail não existir (evita enumeration).
    """
    result = await db.execute(select(User).where(User.email == dados.email))
    user = result.scalar_one_or_none()

    if user:
        token = gerar_token_reset()
        # Salvar token no Redis (expira em 1h)
        await redis.setex(f"reset_senha:{token}", 3600, str(user.id))
        # TODO: Enviar e-mail com o token (implementar em services/email.py)
        logger.info("reset_senha_solicitado", email=dados.email)

    return SuccessMessage(message="Se o e-mail existir, você receberá instruções para redefinir sua senha")


@router.post("/reset-password", response_model=SuccessMessage)
async def reset_password(
    dados: ResetPasswordRequest,
    db: DbSession,
    redis: RedisConn,
):
    """Redefine a senha usando o token one-time recebido por e-mail."""
    # Verificar token no Redis
    user_id = await redis.get(f"reset_senha:{dados.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    # Atualizar senha
    from uuid import UUID
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.password_hash = hash_senha(dados.new_password)

    # Invalidar token
    await redis.delete(f"reset_senha:{dados.token}")

    logger.info("senha_redefinida", user_id=user_id)
    return SuccessMessage(message="Senha redefinida com sucesso")


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    from app.schemas.user import UserResponse
    return UserResponse.model_validate(current_user)
