# backend/app/db/models/rotina.py
# Models de rotinas do Portal TRK.
# Rotina: template de rotina diária (criada pelo gestor)
# RotinaBloco: blocos individuais de uma rotina (checkbox, upload, etc.)
# RotinaAtribuicao: associação rotina ↔ funcionário

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Rotina(Base, TimestampMixin):
    """Template de rotina configurada pelo gestor."""
    __tablename__ = "rotinas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Dias da semana: 1=seg, 2=ter, 3=qua, 4=qui, 5=sex (usado quando recorrência = semanal)
    dias_semana: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=[])
    # Recorrência estilo Todoist: diaria | semanal | intervalo | mensal | datas
    tipo_recorrencia: Mapped[str] = mapped_column(String(20), nullable=False, default="semanal", server_default="semanal")
    # Config da recorrência (cada_dias, inicio, dias_mes, datas, etc.)
    recorrencia_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    # Alertas exibidos como banners no topo da rotina
    alertas: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True, default=[])
    categoria: Mapped[str] = mapped_column(
        Enum("banco", "omie", "drive", "urgente", "pipe", "geral", name="rotina_categoria"),
        nullable=False,
        default="geral",
    )
    status: Mapped[str] = mapped_column(
        Enum("ativa", "pausada", "arquivada", name="rotina_status"),
        nullable=False,
        default="ativa",
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # ─── Relacionamentos ───
    blocos = relationship("RotinaBloco", back_populates="rotina", lazy="selectin",
                          order_by="RotinaBloco.posicao", cascade="all, delete-orphan")
    atribuicoes = relationship("RotinaAtribuicao", back_populates="rotina", lazy="selectin",
                               cascade="all, delete-orphan")
    criador = relationship("User", foreign_keys=[created_by], lazy="joined")

    def __repr__(self) -> str:
        return f"<Rotina {self.nome} status={self.status}>"


class RotinaBloco(Base):
    """Bloco individual dentro de uma rotina (checkbox, text, upload, etc.)."""
    __tablename__ = "rotina_blocos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rotina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rotinas.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(
        Enum(
            "checkbox", "text_short", "text_long", "link",
            "section_header", "file_upload", "balance_indicator", "date_field",
            name="bloco_tipo",
        ),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(300), nullable=False)
    # Configuração variável por tipo (placeholder, url, max_chars, tipos_aceitos, etc.)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default={})
    posicao: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ─── Relacionamentos ───
    rotina = relationship("Rotina", back_populates="blocos")

    def __repr__(self) -> str:
        return f"<RotinaBloco {self.tipo} label={self.label}>"


class RotinaAtribuicao(Base):
    """Associação entre rotina e funcionário atribuído."""
    __tablename__ = "rotina_atribuicoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rotina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rotinas.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ─── Relacionamentos ───
    rotina = relationship("Rotina", back_populates="atribuicoes")
    user = relationship("User", foreign_keys=[user_id], lazy="joined")
