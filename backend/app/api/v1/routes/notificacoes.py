# backend/app/api/v1/routes/notificacoes.py
# Rotas de notificações do Portal TRK.

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select, update

from app.core.dependencies import DbSession, get_current_user
from app.db.models.notificacao import Notificacao
from app.db.models.push_subscription import PushSubscription
from app.schemas.notificacao import (
    MarcarLidaRequest,
    NotificacaoResponse,
    PushSubscriptionRequest,
)

router = APIRouter()


@router.get("/", response_model=list[NotificacaoResponse])
async def listar_notificacoes(
    db: DbSession,
    current_user=Depends(get_current_user),
    apenas_nao_lidas: bool = False,
):
    """Lista notificações do usuário autenticado."""
    query = (
        select(Notificacao)
        .where(Notificacao.user_id == current_user.id)
        .order_by(Notificacao.created_at.desc())
        .limit(50)
    )
    if apenas_nao_lidas:
        query = query.where(Notificacao.lida == False)

    result = await db.execute(query)
    return [NotificacaoResponse.model_validate(n) for n in result.scalars().all()]


@router.get("/count")
async def contar_nao_lidas(
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Retorna contagem de notificações não lidas (para o badge)."""
    from sqlalchemy import func
    result = await db.execute(
        select(func.count()).where(
            Notificacao.user_id == current_user.id,
            Notificacao.lida == False,
        )
    )
    return {"count": result.scalar() or 0}


@router.patch("/marcar-lida")
async def marcar_lida(
    dados: MarcarLidaRequest,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Marca notificações como lidas."""
    query = update(Notificacao).where(Notificacao.user_id == current_user.id)

    if dados.todas:
        query = query.values(lida=True)
    elif dados.ids:
        query = query.where(Notificacao.id.in_(dados.ids)).values(lida=True)

    await db.execute(query)
    return {"message": "Notificações marcadas como lidas"}


@router.post("/push-subscription")
async def registrar_push(
    dados: PushSubscriptionRequest,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Registra subscription para push notifications (PWA)."""
    # Verificar se já existe
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.user_id == current_user.id,
            PushSubscription.endpoint == dados.endpoint,
        )
    )
    existing = result.scalar_one_or_none()

    if not existing:
        sub = PushSubscription(
            user_id=current_user.id,
            endpoint=dados.endpoint,
            p256dh=dados.p256dh,
            auth_key=dados.auth_key,
        )
        db.add(sub)

    return {"message": "Push subscription registrada"}
