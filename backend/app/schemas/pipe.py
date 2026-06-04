# backend/app/schemas/pipe.py
# Schemas do subsistema de Pipes (estilo Pipefy).

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ─── Fases ───
class FaseBase(BaseModel):
    nome: str
    ordem: int = 0
    cor: str = "#94a3b8"
    is_final: bool = False
    sla_horas: int | None = None


class FaseCreate(FaseBase):
    pass


class FaseResponse(FaseBase):
    id: UUID
    model_config = {"from_attributes": True}


# ─── Campos ───
class CampoBase(BaseModel):
    label: str
    tipo: str = "text"
    config: dict = Field(default_factory=dict)
    ordem: int = 0
    fase_id: UUID | None = None


class CampoCreate(CampoBase):
    pass


class CampoResponse(CampoBase):
    id: UUID
    model_config = {"from_attributes": True}


# ─── Pipes ───
class PipeBase(BaseModel):
    nome: str
    descricao: str | None = None
    cor: str = "#6366f1"
    icone: str = "Kanban"


class PipeCreate(PipeBase):
    # Opcional: cria fases iniciais junto. Se vazio, usa um padrão.
    fases: list[FaseCreate] = Field(default_factory=list)
    usar_template: str | None = None  # "padrao" | "contas_pagar" | None


class PipeUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    cor: str | None = None
    icone: str | None = None
    is_active: bool | None = None


class PipeResponse(PipeBase):
    id: UUID
    is_active: bool
    fases: list[FaseResponse] = []
    campos: list[CampoResponse] = []
    model_config = {"from_attributes": True}


# ─── Cards ───
class CardCreate(BaseModel):
    titulo: str
    fase_id: UUID | None = None  # default: primeira fase
    valores: dict = Field(default_factory=dict)
    valor_monetario: Decimal | None = None
    prazo: datetime | None = None
    atribuido_a: UUID | None = None
    empresa_id: UUID | None = None


class CardUpdate(BaseModel):
    titulo: str | None = None
    valores: dict | None = None
    valor_monetario: Decimal | None = None
    prazo: datetime | None = None
    atribuido_a: UUID | None = None
    empresa_id: UUID | None = None
    concluido: bool | None = None


class CardMove(BaseModel):
    fase_id: UUID
    ordem: int | None = None


class HistoricoResponse(BaseModel):
    id: UUID
    tipo: str
    texto: str | None
    de_fase_id: UUID | None
    para_fase_id: UUID | None
    user_id: UUID | None
    created_at: datetime
    model_config = {"from_attributes": True}


class CardResponse(BaseModel):
    id: UUID
    pipe_id: UUID
    fase_id: UUID
    titulo: str
    valores: dict
    ordem: int
    concluido: bool
    valor_monetario: Decimal | None
    prazo: datetime | None
    fase_entrou_em: datetime
    atribuido_a: UUID | None
    empresa_id: UUID | None
    responsavel_nome: str | None = None
    empresa_nome: str | None = None
    sla_status: str = "ok"  # ok | atencao | estourado
    created_at: datetime
    model_config = {"from_attributes": True}


class ComentarioCreate(BaseModel):
    texto: str


class BoardFase(BaseModel):
    fase: FaseResponse
    cards: list[CardResponse]


class BoardResponse(BaseModel):
    pipe: PipeResponse
    colunas: list[BoardFase]
