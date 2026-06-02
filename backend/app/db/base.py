# backend/app/db/base.py
# Base declarativa do SQLAlchemy 2.0 para o Portal TRK.
# Define:
#   - Base: classe base para todos os models
#   - TimestampMixin: adiciona created_at e updated_at automáticos
#   - SoftDeleteMixin: adiciona is_deleted e deleted_at para exclusão lógica

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Classe base para todos os models do Portal TRK."""
    pass


class TimestampMixin:
    """
    Mixin que adiciona created_at e updated_at.
    created_at: definido automaticamente na criação (server_default).
    updated_at: atualizado automaticamente em cada modificação (onupdate).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin para soft delete — nunca apaga registros, apenas marca como deletados.
    Queries devem filtrar por is_deleted=False.
    """

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
