# backend/app/db/models/empresa.py
# Model de empresa do Portal TRK.
# Representa as 23 empresas do grupo (6 TRK + 17 BPO).
# Credenciais bancárias e do Omie são armazenadas criptografadas (AES-256-GCM).

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Empresa(Base, TimestampMixin):
    __tablename__ = "empresas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(300), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, nullable=False, index=True)
    banco: Mapped[str] = mapped_column(
        Enum("santander", "inter", "bradesco", name="banco_tipo"),
        nullable=False,
    )
    agencia: Mapped[str | None] = mapped_column(String(20), nullable=True)
    conta: Mapped[str | None] = mapped_column(String(30), nullable=True)
    grupo: Mapped[str] = mapped_column(
        Enum("trk", "bpo", name="empresa_grupo"),
        nullable=False,
    )
    responsavel_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ─── Credenciais criptografadas (AES-256-GCM) ───
    # Valores armazenados como base64(IV + ciphertext + tag)
    omie_app_key_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    omie_app_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_client_id_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_client_secret_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_certificate_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Relacionamentos ───
    responsavel = relationship("User", foreign_keys=[responsavel_user_id], lazy="joined")
    saldos = relationship("Saldo", back_populates="empresa", lazy="noload")
    user_assignments = relationship("UserEmpresaAssignment", back_populates="empresa", lazy="noload")

    def __repr__(self) -> str:
        return f"<Empresa {self.nome} grupo={self.grupo}>"
