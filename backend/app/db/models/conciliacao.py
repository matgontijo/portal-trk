# backend/app/db/models/conciliacao.py
# Model de conciliação do Portal TRK.
# Registra o match entre lançamentos bancários e do Omie.
# O par (lancamento_banco_id, lancamento_omie_id) é o coração da tabela.

import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Conciliacao(Base, TimestampMixin):
    __tablename__ = "conciliacao"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lancamento_banco_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lancamentos_banco.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    lancamento_omie_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lancamentos_omie.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False
    )
    data_referencia: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(
            "ok", "pendente", "divergente", "revisao_manual", "sem_correspondencia",
            name="conciliacao_status",
        ),
        nullable=False,
        default="pendente",
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4), nullable=True
    )
    metodo: Mapped[str] = mapped_column(
        Enum(
            "rule_exact", "rule_cnpj", "ml_auto", "ml_sugestao", "manual",
            name="conciliacao_metodo",
        ),
        nullable=False,
    )
    conciliado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    obs: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Relacionamentos ───
    lancamento_banco = relationship("LancamentoBanco", lazy="joined")
    lancamento_omie = relationship("LancamentoOmie", lazy="joined")
    empresa = relationship("Empresa", lazy="joined")
    usuario = relationship("User", foreign_keys=[conciliado_por], lazy="joined")

    def __repr__(self) -> str:
        return f"<Conciliacao status={self.status} metodo={self.metodo} score={self.confidence_score}>"
