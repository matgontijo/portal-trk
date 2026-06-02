# backend/app/schemas/common.py
# Schemas comuns reutilizados em múltiplos domínios.

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

T = TypeVar("T")


class SuccessMessage(BaseModel):
    """Resposta genérica de sucesso."""
    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""
    detail: str
    code: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Resposta paginada genérica."""
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class IDResponse(BaseModel):
    """Resposta com ID do recurso criado."""
    id: UUID
    message: str = "Criado com sucesso"
