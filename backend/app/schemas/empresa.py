# backend/app/schemas/empresa.py
# Schemas de empresa — criação, atualização e resposta.

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserBrief


class EmpresaCreate(BaseModel):
    """Criação de nova empresa."""
    nome: str
    cnpj: str
    banco: Literal["santander", "inter", "bradesco"]
    agencia: str | None = None
    conta: str | None = None
    grupo: Literal["trk", "bpo"]
    responsavel_user_id: UUID | None = None


class EmpresaUpdate(BaseModel):
    """Atualização de empresa."""
    nome: str | None = None
    banco: Literal["santander", "inter", "bradesco"] | None = None
    agencia: str | None = None
    conta: str | None = None
    grupo: Literal["trk", "bpo"] | None = None
    responsavel_user_id: UUID | None = None
    is_active: bool | None = None


class EmpresaCredenciais(BaseModel):
    """Atualização de credenciais de integração (criptografadas)."""
    omie_app_key: str | None = None
    omie_app_secret: str | None = None
    bank_client_id: str | None = None
    bank_client_secret: str | None = None


class SaldoResumo(BaseModel):
    """Resumo do saldo para exibição no card de empresa."""
    saldo_banco: Decimal
    saldo_omie: Decimal
    delta: Decimal
    tem_divergencia: bool
    tipo_divergencia: str
    synced_at: datetime | None

    model_config = {"from_attributes": True}


class EmpresaResponse(BaseModel):
    """Resposta completa de empresa."""
    id: UUID
    nome: str
    cnpj: str
    banco: str
    agencia: str | None
    conta: str | None
    grupo: str
    responsavel: UserBrief | None
    is_active: bool
    saldo_atual: SaldoResumo | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmpresaDetalhe(EmpresaResponse):
    """Detalhes expandidos da empresa (para drawer/página de detalhe)."""
    tem_omie_config: bool = False
    tem_bank_config: bool = False
