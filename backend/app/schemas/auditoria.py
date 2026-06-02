# backend/app/schemas/auditoria.py
# Schemas de auditoria — filtros e respostas.

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Registro de log de auditoria."""
    id: UUID
    user_name: str | None = None
    action: str
    resource_type: str | None
    resource_id: UUID | None
    ip_address: str | None
    timestamp: datetime
    before_json: dict | None = None
    after_json: dict | None = None

    model_config = {"from_attributes": True}


class AuditFilter(BaseModel):
    """Filtros para consulta de auditoria."""
    user_id: UUID | None = None
    action: str | None = None
    resource_type: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    page: int = 1
    per_page: int = 50
