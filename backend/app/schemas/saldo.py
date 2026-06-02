# backend/app/schemas/saldo.py
# Schemas de saldos bancários — resposta e status de sync.

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class SaldoResponse(BaseModel):
    """Saldo de uma empresa com status de divergência."""
    id: UUID
    empresa_id: UUID
    empresa_nome: str
    saldo_banco: Decimal
    saldo_omie: Decimal
    delta: Decimal
    tem_divergencia: bool
    tipo_divergencia: str
    data_referencia: date
    synced_at: datetime

    model_config = {"from_attributes": True}


class SaldoHistorico(BaseModel):
    """Ponto de dados para gráfico de evolução de saldo."""
    data_referencia: date
    saldo_banco: Decimal
    saldo_omie: Decimal
    delta: Decimal
    tem_divergencia: bool


class SyncStatus(BaseModel):
    """Status do último sync de uma empresa."""
    empresa_id: UUID
    empresa_nome: str
    ultimo_sync: datetime | None
    status: str  # "ok" | "erro" | "pendente" | "desatualizado"
    mensagem: str | None = None


class DashboardKPIs(BaseModel):
    """KPIs do dashboard financeiro."""
    total_em_caixa: Decimal
    a_pagar_hoje: Decimal
    a_pagar_semana: Decimal
    em_atraso: Decimal
    empresas_com_divergencia: int
    total_empresas: int
