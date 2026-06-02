# backend/app/db/models/lancamento.py
# Models de lançamentos bancários e do Omie.
# LancamentoBanco: transações vindas do extrato bancário (API dos bancos)
# LancamentoOmie: contas a pagar/receber vindas do Omie ERP

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LancamentoBanco(Base):
    """Lançamento importado do extrato bancário via API."""
    __tablename__ = "lancamentos_banco"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_lancamento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tipo: Mapped[str] = mapped_column(
        Enum("debito", "credito", name="lancamento_tipo"),
        nullable=False,
    )
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    identificador_banco: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cnpj_contraparte: Mapped[str | None] = mapped_column(String(18), nullable=True, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ─── Relacionamentos ───
    empresa = relationship("Empresa", lazy="joined")

    def __repr__(self) -> str:
        return f"<LancamentoBanco {self.tipo} R${self.valor} em {self.data_lancamento}>"


class LancamentoOmie(Base):
    """Lançamento importado do Omie ERP (contas a pagar/receber)."""
    __tablename__ = "lancamentos_omie"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    empresa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_lancamento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_omie: Mapped[str | None] = mapped_column(String(50), nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    id_omie: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ─── Relacionamentos ───
    empresa = relationship("Empresa", lazy="joined")

    def __repr__(self) -> str:
        return f"<LancamentoOmie R${self.valor} doc={self.numero_documento}>"
