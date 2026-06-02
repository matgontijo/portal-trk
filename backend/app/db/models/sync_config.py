# backend/app/db/models/sync_config.py
# Model de configuração de sync do Portal TRK.
# Tabela com apenas 1 registro — controla horários de sync, relatório e WhatsApp.
# Celery Beat lê esses horários dinamicamente (não hardcoded).

import uuid
from datetime import time, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SyncConfig(Base):
    __tablename__ = "sync_config"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Horários de sync bancário (BRT)
    horario_1: Mapped[time] = mapped_column(Time, nullable=False, default=time(6, 0))
    horario_2: Mapped[time] = mapped_column(Time, nullable=False, default=time(20, 0))
    # Horário do resumo diário WhatsApp
    whatsapp_horario: Mapped[time] = mapped_column(Time, nullable=False, default=time(6, 30))
    # Relatório semanal: dia (5=sexta) e horário
    relatorio_dia_semana: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    relatorio_horario: Mapped[time] = mapped_column(Time, nullable=False, default=time(18, 0))
    # Auditoria
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<SyncConfig sync={self.horario_1}/{self.horario_2}>"
