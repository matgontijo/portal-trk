# backend/app/db/models/user.py
# Model de usuário do Portal TRK.
# Roles: admin (dono), gestor, funcionario
# Cada usuário tem email único, senha hasheada e pode ter telefone WhatsApp.

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("admin", "gestor", "funcionario", name="user_role"),
        nullable=False,
        default="funcionario",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    phone_whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ─── Relacionamentos ───
    refresh_tokens = relationship("RefreshToken", back_populates="user", lazy="selectin")
    empresa_assignments = relationship("UserEmpresaAssignment", foreign_keys="[UserEmpresaAssignment.user_id]", back_populates="user", lazy="selectin")
    notificacoes = relationship("Notificacao", back_populates="user", lazy="noload")
    push_subscriptions = relationship("PushSubscription", back_populates="user", lazy="noload")

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"
