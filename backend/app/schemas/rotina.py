# backend/app/schemas/rotina.py
# Schemas de rotinas — criação, blocos, progresso e resposta.

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.schemas.user import UserBrief


class BlocoConfig(BaseModel):
    """Configuração de um bloco de rotina (varia por tipo)."""
    tipo: Literal[
        "checkbox", "text_short", "text_long", "link",
        "section_header", "file_upload", "balance_indicator", "date_field"
    ]
    label: str
    config: dict[str, Any] = {}
    posicao: int = 0
    is_required: bool = False


class RotinaCreate(BaseModel):
    """Criação de nova rotina (gestor+)."""
    nome: str
    descricao: str | None = None
    dias_semana: list[int]
    alertas: list[str] = []
    categoria: Literal["banco", "omie", "drive", "urgente", "pipe", "geral"] = "geral"
    blocos: list[BlocoConfig] = []
    user_ids: list[UUID] = []  # Funcionários atribuídos

    @field_validator("dias_semana")
    @classmethod
    def validar_dias(cls, v: list[int]) -> list[int]:
        for dia in v:
            if dia < 1 or dia > 5:
                raise ValueError("Dias da semana devem ser entre 1 (seg) e 5 (sex)")
        return sorted(set(v))


class RotinaUpdate(BaseModel):
    """Atualização de rotina existente."""
    nome: str | None = None
    descricao: str | None = None
    dias_semana: list[int] | None = None
    alertas: list[str] | None = None
    categoria: Literal["banco", "omie", "drive", "urgente", "pipe", "geral"] | None = None
    status: Literal["ativa", "pausada", "arquivada"] | None = None
    blocos: list[BlocoConfig] | None = None
    user_ids: list[UUID] | None = None


class ProgressoUpdate(BaseModel):
    """Atualização de progresso de um bloco pelo funcionário."""
    bloco_id: UUID
    is_done: bool | None = None
    valor_texto: str | None = None
    arquivo_url: str | None = None
    arquivo_nome: str | None = None


class BlocoResponse(BaseModel):
    """Resposta de bloco com progresso do dia."""
    id: UUID
    tipo: str
    label: str
    config: dict[str, Any]
    posicao: int
    is_required: bool
    # Progresso do dia atual (preenchido ao carregar rotina)
    progresso: "ProgressoResponse | None" = None

    model_config = {"from_attributes": True}


class ProgressoResponse(BaseModel):
    """Estado do progresso de um bloco."""
    id: UUID
    is_done: bool
    valor_texto: str | None
    arquivo_url: str | None
    arquivo_nome: str | None
    done_at: datetime | None

    model_config = {"from_attributes": True}


class RotinaResponse(BaseModel):
    """Resposta completa de rotina com blocos e progresso."""
    id: UUID
    nome: str
    descricao: str | None
    dias_semana: list[int]
    alertas: list[str]
    categoria: str
    status: str
    blocos: list[BlocoResponse]
    atribuidos: list[UserBrief] = []
    # Progresso geral: X de Y concluídos
    total_blocos: int = 0
    blocos_concluidos: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
