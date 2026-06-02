# backend/app/schemas/configuracao.py
# Schemas de configurações — sync, integrações, IA.

from datetime import time, datetime
from uuid import UUID

from pydantic import BaseModel


class SyncConfigUpdate(BaseModel):
    """Atualização dos horários de sync."""
    horario_1: time | None = None
    horario_2: time | None = None
    whatsapp_horario: time | None = None
    relatorio_dia_semana: int | None = None
    relatorio_horario: time | None = None


class SyncConfigResponse(BaseModel):
    """Resposta da configuração de sync."""
    horario_1: time
    horario_2: time
    whatsapp_horario: time
    relatorio_dia_semana: int
    relatorio_horario: time
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class IntegracaoUpdate(BaseModel):
    """Atualização de credenciais de integração por empresa."""
    empresa_id: UUID
    omie_app_key: str | None = None
    omie_app_secret: str | None = None
    bank_client_id: str | None = None
    bank_client_secret: str | None = None


class MLConfigResponse(BaseModel):
    """Informações do modelo ML ativo."""
    id: UUID | None = None
    treinado_em: datetime | None = None
    precision_score: float | None = None
    recall_score: float | None = None
    f1_score: float | None = None
    n_amostras_treino: int = 0
    threshold_auto: float = 0.90
    is_active: bool = False

    model_config = {"from_attributes": True}


class MLThresholdUpdate(BaseModel):
    """Atualização do threshold de auto-conciliação."""
    threshold: float

    class Config:
        json_schema_extra = {"example": {"threshold": 0.90}}
