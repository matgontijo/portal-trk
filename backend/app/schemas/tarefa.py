# backend/app/schemas/tarefa.py
# Schemas de tarefas (Kanban) — criação, atualização e resposta.

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserBrief


class TarefaCreate(BaseModel):
    """Criação de nova tarefa (gestor+)."""
    titulo: str
    descricao: str | None = None
    prioridade: Literal["baixa", "normal", "alta", "urgente"] = "normal"
    prazo: datetime | None = None
    atribuido_a: UUID | None = None
    empresa_id: UUID | None = None


class TarefaUpdate(BaseModel):
    """Atualização de tarefa."""
    titulo: str | None = None
    descricao: str | None = None
    status: Literal["todo", "doing", "done"] | None = None
    prioridade: Literal["baixa", "normal", "alta", "urgente"] | None = None
    prazo: datetime | None = None
    atribuido_a: UUID | None = None
    empresa_id: UUID | None = None


class TarefaResponse(BaseModel):
    """Resposta de tarefa."""
    id: UUID
    titulo: str
    descricao: str | None
    status: str
    prioridade: str
    prazo: datetime | None
    criador: UserBrief | None
    responsavel: UserBrief | None
    empresa_nome: str | None = None
    esta_atrasada: bool = False
    created_at: datetime
    done_at: datetime | None

    model_config = {"from_attributes": True}
