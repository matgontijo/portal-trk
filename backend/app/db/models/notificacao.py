# backend/app/db/models/notificacao.py
# Model de notificações in-app do Portal TRK.
# Tipos: tarefa_atribuida, divergencia, sync_concluido, relatorio_disponivel, sistema

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(
        Enum(
            "tarefa_atribuida", "divergencia", "sync_concluido",
            "relatorio_disponivel", "sistema",
            name="notificacao_tipo",
        ),
        nullable=False,
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    link_acao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relacionamentos ───
    user = relationship("User", back_populates="notificacoes")

    def __repr__(self) -> str:
        return f"<Notificacao tipo={self.tipo} lida={self.lida}>"
