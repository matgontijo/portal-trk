# backend/app/services/notificacoes.py
# Serviço de notificações do Portal TRK.
# Responsabilidades:
#   - Criar notificações in-app (banco)
#   - Enviar push notifications via Web Push API (VAPID)

import json

import structlog
from pywebpush import webpush, WebPushException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.notificacao import Notificacao
from app.db.models.push_subscription import PushSubscription

logger = structlog.get_logger()


async def criar_notificacao(
    db: AsyncSession,
    user_id,
    tipo: str,
    titulo: str,
    mensagem: str | None = None,
    link_acao: str | None = None,
) -> Notificacao:
    """Cria uma notificação in-app e tenta enviar push."""
    notif = Notificacao(
        user_id=user_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        link_acao=link_acao,
    )
    db.add(notif)

    # Tentar push
    await enviar_push(db, user_id, titulo, mensagem or "")

    return notif


async def enviar_push(
    db: AsyncSession,
    user_id,
    titulo: str,
    mensagem: str,
) -> None:
    """Envia push notification para todas as subscriptions do usuário."""
    settings = get_settings()

    if not settings.VAPID_PRIVATE_KEY:
        return

    result = await db.execute(
        select(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    subscriptions = result.scalars().all()

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth_key,
                    },
                },
                data=json.dumps({
                    "title": titulo,
                    "body": mensagem,
                    "icon": "/icons/icon-192x192.png",
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_CLAIMS_SUB},
            )
        except WebPushException as e:
            logger.warning("push_erro", user_id=str(user_id), erro=str(e))
            # Subscription expirada — remover
            if e.response and e.response.status_code in [404, 410]:
                await db.delete(sub)
        except Exception as e:
            logger.error("push_erro_geral", erro=str(e))
