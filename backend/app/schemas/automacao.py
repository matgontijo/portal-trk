# backend/app/schemas/automacao.py
# Schemas das automações (gatilho → condição → ação).

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RegraCondicao(BaseModel):
    campo: str
    op: str = "=="
    valor: object | None = None


class CondicaoBloco(BaseModel):
    logica: str = "and"  # "and" | "or"
    regras: list[RegraCondicao] = Field(default_factory=list)


class AutomacaoBase(BaseModel):
    nome: str
    descricao: str | None = None
    gatilho: str
    condicao: dict = Field(default_factory=dict)
    acao: str
    acao_config: dict = Field(default_factory=dict)
    ativa: bool = True
    prioridade: int = 0


class AutomacaoCreate(AutomacaoBase):
    pass


class AutomacaoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    gatilho: str | None = None
    condicao: dict | None = None
    acao: str | None = None
    acao_config: dict | None = None
    ativa: bool | None = None
    prioridade: int | None = None


class AutomacaoResponse(AutomacaoBase):
    id: UUID
    execucoes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TestarAutomacaoRequest(BaseModel):
    """Avalia a condição contra um contexto simulado (não executa a ação)."""
    condicao: dict = Field(default_factory=dict)
    contexto: dict = Field(default_factory=dict)


class TestarAutomacaoResponse(BaseModel):
    condicao_satisfeita: bool
