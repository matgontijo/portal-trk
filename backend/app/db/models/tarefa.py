# backend/app/db/models/tarefa.py
# Model de tarefas do Portal TRK (Kanban).
# Status: todo → doing → done (colunas do Kanban)
# Prioridade: baixa, normal, alta, urgente

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Tarefa(Base, TimestampMixin):
    __tablename__ = "tarefas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("todo", "doing", "done", name="tarefa_status"),
        nullable=False,
        default="todo",
    )
    prioridade: Mapped[str] = mapped_column(
        Enum("baixa", "normal", "alta", "urgente", name="tarefa_prioridade"),
        nullable=False,
        default="normal",
    )
    prazo: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    criado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    atribuido_a: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True
    )
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ─── Relacionamentos ───
    criador = relationship("User", foreign_keys=[criado_por], lazy="joined")
    responsavel = relationship("User", foreign_keys=[atribuido_a], lazy="joined")
    empresa = relationship("Empresa", lazy="joined")

    @property
    def esta_atrasada(self) -> bool:
        """Verifica se a tarefa está atrasada (prazo vencido e não concluída)."""
        if self.prazo and self.status != "done":
            return datetime.now(self.prazo.tzinfo) > self.prazo
        return False

    def __repr__(self) -> str:
        return f"<Tarefa {self.titulo} status={self.status}>"
