# backend/app/db/models/saldo.py
# Model de saldos bancários do Portal TRK.
# Registra saldo do banco, saldo do Omie, delta e tipo de divergência.
# Atualizado pelo job de sync automático (Celery Beat).

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Saldo(Base):
    __tablename__ = "saldos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    saldo_banco: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    saldo_omie: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    delta: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tem_divergencia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tipo_divergencia: Mapped[str] = mapped_column(
        Enum(
            "sem_divergencia",
            "lancamento_nao_identificado",
            "pagamento_nao_processado",
            "valor_divergente",
            "data_divergente",
            "multiplas",
            name="tipo_divergencia",
        ),
        nullable=False,
        default="sem_divergencia",
    )
    data_referencia: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ─── Dados brutos para debug (nunca exibidos ao usuário) ───
    raw_bank_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    raw_omie_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ─── Relacionamentos ───
    empresa = relationship("Empresa", back_populates="saldos")

    def __repr__(self) -> str:
        return f"<Saldo empresa={self.empresa_id} delta={self.delta} diverg={self.tem_divergencia}>"
