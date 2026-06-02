# backend/app/db/models/rotina_progresso.py
# Model de progresso de rotinas do Portal TRK.
# Registra o estado de cada bloco por usuário e data.
# Constraint UNIQUE(bloco_id, user_id, data_referencia) garante um progresso por dia.

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RotinaProgresso(Base):
    """Estado de um bloco de rotina para um usuário em uma data específica."""
    __tablename__ = "rotina_progresso"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rotina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rotinas.id", ondelete="CASCADE"), nullable=False
    )
    bloco_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rotina_blocos.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    data_referencia: Mapped[date] = mapped_column(Date, nullable=False)

    # ─── Valores preenchidos pelo funcionário ───
    valor_texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    arquivo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    arquivo_nome: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=datetime.now
    )

    # ─── Constraint de unicidade ───
    __table_args__ = (
        UniqueConstraint("bloco_id", "user_id", "data_referencia", name="uq_progresso_bloco_user_data"),
    )

    # ─── Relacionamentos ───
    bloco = relationship("RotinaBloco", lazy="joined")
    user = relationship("User", lazy="joined")

    def __repr__(self) -> str:
        return f"<RotinaProgresso bloco={self.bloco_id} data={self.data_referencia} done={self.is_done}>"
