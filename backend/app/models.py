# trk-universe/backend/app/models.py
# Modelos do TRK OS. IDs como UUID hex (compatível com SQLite e Postgres).

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Departamento(Base):
    __tablename__ = "departamentos"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    cor: Mapped[str] = mapped_column(String(20), default="#171717")
    icone: Mapped[str] = mapped_column(String(40), default="Building2")
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Template de permissões aplicado a novos membros: {modulo: {ver, editar}}
    permissoes_padrao: Mapped[dict] = mapped_column(JSON, default=dict)

    usuarios = relationship("User", back_populates="departamento")


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    # diretor (acesso total) | gestor (gere o setor) | colaborador
    cargo: Mapped[str] = mapped_column(String(20), default="colaborador", nullable=False)
    departamento_id: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("departamentos.id", ondelete="SET NULL"), nullable=True
    )
    # Permissões efetivas do usuário: {modulo: {ver: bool, editar: bool}}
    permissoes: Mapped[dict] = mapped_column(JSON, default=dict)
    avatar_cor: Mapped[str] = mapped_column(String(20), default="#171717")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    departamento = relationship("Departamento", back_populates="usuarios")


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(20), default="")
    banco: Mapped[str] = mapped_column(String(30), default="fake")
    grupo: Mapped[str] = mapped_column(String(20), default="trk")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class Saldo(Base):
    __tablename__ = "saldos"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    empresa_id: Mapped[str] = mapped_column(String(32), ForeignKey("empresas.id", ondelete="CASCADE"))
    saldo_banco: Mapped[float] = mapped_column(default=0.0)
    saldo_omie: Mapped[float] = mapped_column(default=0.0)
    delta: Mapped[float] = mapped_column(default=0.0)
    tem_divergencia: Mapped[bool] = mapped_column(Boolean, default=False)
    data_referencia: Mapped[str] = mapped_column(String(10), default="")
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    empresa = relationship("Empresa")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="todo")  # todo|doing|done
    prioridade: Mapped[str] = mapped_column(String(20), default="normal")
    ordem: Mapped[int] = mapped_column(default=0)
    departamento_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    atribuido_a: Mapped[str | None] = mapped_column(String(32), nullable=True)
    criado_por: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class Rotina(Base):
    __tablename__ = "rotinas"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(300), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_recorrencia: Mapped[str] = mapped_column(String(20), default="semanal")
    recorrencia_config: Mapped[dict] = mapped_column(JSON, default=dict)
    dias_semana: Mapped[list] = mapped_column(JSON, default=list)
    categoria: Mapped[str] = mapped_column(String(20), default="geral")
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    blocos: Mapped[list] = mapped_column(JSON, default=list)  # [{id,tipo,label,obrigatorio}]
    atribuidos: Mapped[list] = mapped_column(JSON, default=list)  # [user_id]
    departamento_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class RotinaProgresso(Base):
    __tablename__ = "rotina_progresso"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    rotina_id: Mapped[str] = mapped_column(String(32), index=True)
    bloco_id: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    data_ref: Mapped[str] = mapped_column(String(10))
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    valor_texto: Mapped[str | None] = mapped_column(Text, nullable=True)


class Pipe(Base):
    __tablename__ = "pipes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cor: Mapped[str] = mapped_column(String(20), default="#171717")
    fases: Mapped[list] = mapped_column(JSON, default=list)  # [{id,nome,cor,ordem,final}]
    departamento_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class PipeCard(Base):
    __tablename__ = "pipe_cards"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    pipe_id: Mapped[str] = mapped_column(String(32), index=True)
    fase_id: Mapped[str] = mapped_column(String(32))
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    ordem: Mapped[int] = mapped_column(default=0)
    valor: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class Automacao(Base):
    __tablename__ = "automacoes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    gatilho: Mapped[str] = mapped_column(String(40))
    condicao: Mapped[dict] = mapped_column(JSON, default=dict)
    acao: Mapped[str] = mapped_column(String(40))
    acao_config: Mapped[dict] = mapped_column(JSON, default=dict)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
    execucoes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
