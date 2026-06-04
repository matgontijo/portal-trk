# backend/app/db/models/pipe.py
# Subsistema de Pipes (estilo Pipefy) do Portal TRK.
#
# Hierarquia:
#   Pipe  ─┬─ PipeFase (colunas do kanban, ordenadas, com SLA opcional)
#          ├─ PipeCampo (campos customizados: do formulário inicial ou de uma fase)
#          └─ PipeCard ─── PipeCardHistorico (movimentações, comentários, log)
#
# Os valores dos campos de cada card ficam em JSONB (campo_id -> valor),
# permitindo campos 100% customizáveis pela UI sem alterar o schema.

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

# Tipos de campo suportados (inspirados no Pipefy)
CAMPO_TIPOS = (
    "text", "textarea", "number", "currency", "date",
    "select", "checkbox", "email", "phone", "attachment", "empresa",
)


class Pipe(Base, TimestampMixin):
    """Um pipe = um processo (ex.: Onboarding de Cliente, Contas a Pagar)."""
    __tablename__ = "pipes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    cor: Mapped[str] = mapped_column(String(20), nullable=False, default="#6366f1")
    icone: Mapped[str] = mapped_column(String(40), nullable=False, default="Kanban")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    fases = relationship(
        "PipeFase", back_populates="pipe", lazy="selectin",
        order_by="PipeFase.ordem", cascade="all, delete-orphan",
    )
    campos = relationship(
        "PipeCampo", back_populates="pipe", lazy="selectin",
        order_by="PipeCampo.ordem", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Pipe {self.nome}>"


class PipeFase(Base):
    """Fase (coluna) do pipe."""
    __tablename__ = "pipe_fases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cor: Mapped[str] = mapped_column(String(20), nullable=False, default="#94a3b8")
    is_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # SLA: horas máximas que um card deveria ficar nesta fase (None = sem SLA)
    sla_horas: Mapped[int | None] = mapped_column(Integer, nullable=True)

    pipe = relationship("Pipe", back_populates="fases")

    def __repr__(self) -> str:
        return f"<PipeFase {self.nome} ordem={self.ordem}>"


class PipeCampo(Base):
    """Definição de um campo customizado do pipe.
    fase_id nulo => campo do formulário inicial (preenchido ao criar o card)."""
    __tablename__ = "pipe_campos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fase_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipe_fases.id", ondelete="CASCADE"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="text")
    # Config: {"opcoes": [...], "obrigatorio": bool, "placeholder": "...", ...}
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    pipe = relationship("Pipe", back_populates="campos")

    def __repr__(self) -> str:
        return f"<PipeCampo {self.label} tipo={self.tipo}>"


class PipeCard(Base, TimestampMixin):
    """Card que percorre as fases do pipe."""
    __tablename__ = "pipe_cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    fase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipe_fases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    # Valores dos campos customizados: {campo_id: valor}
    valores: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    concluido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    valor_monetario: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    prazo: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fase_entrou_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    atribuido_a: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    empresa_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True
    )
    criado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    responsavel = relationship("User", foreign_keys=[atribuido_a], lazy="joined")
    empresa = relationship("Empresa", lazy="joined")
    historico = relationship(
        "PipeCardHistorico", back_populates="card", lazy="selectin",
        order_by="PipeCardHistorico.created_at.desc()", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PipeCard {self.titulo} fase={self.fase_id}>"


class PipeCardHistorico(Base):
    """Linha do tempo do card: criação, movimentações e comentários."""
    __tablename__ = "pipe_card_historico"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pipe_cards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="comentario")  # criacao|movimentacao|comentario
    texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    de_fase_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    para_fase_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    card = relationship("PipeCard", back_populates="historico")
    autor = relationship("User", lazy="joined")

    def __repr__(self) -> str:
        return f"<PipeCardHistorico {self.tipo} card={self.card_id}>"
