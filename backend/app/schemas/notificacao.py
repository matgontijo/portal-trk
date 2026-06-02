# backend/app/schemas/notificacao.py
# Schemas de notificações — in-app e push subscriptions.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NotificacaoResponse(BaseModel):
    """Notificação in-app."""
    id: UUID
    tipo: str
    titulo: str
    mensagem: str | None
    link_acao: str | None
    lida: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MarcarLidaRequest(BaseModel):
    """Marcar notificação(ões) como lida(s)."""
    ids: list[UUID] | None = None  # None = marcar todas
    todas: bool = False


class PushSubscriptionRequest(BaseModel):
    """Registrar subscription para push notifications."""
    endpoint: str
    p256dh: str
    auth_key: str
