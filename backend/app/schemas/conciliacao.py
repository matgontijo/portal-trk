# backend/app/schemas/conciliacao.py
# Schemas de conciliação — matches, sugestões e decisões.

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class LancamentoBancoResponse(BaseModel):
    """Lançamento bancário para exibição."""
    id: UUID
    data_lancamento: date
    valor: Decimal
    tipo: str
    descricao: str | None
    identificador_banco: str | None

    model_config = {"from_attributes": True}


class LancamentoOmieResponse(BaseModel):
    """Lançamento do Omie para exibição."""
    id: UUID
    data_lancamento: date
    data_vencimento: date | None
    valor: Decimal
    descricao: str | None
    status_omie: str | None
    numero_documento: str | None

    model_config = {"from_attributes": True}


class MatchSugestao(BaseModel):
    """Sugestão de match entre lançamentos (gerada pela IA)."""
    lancamento_banco: LancamentoBancoResponse
    lancamento_omie: LancamentoOmieResponse
    confidence_score: float
    metodo: str  # rule_exact, rule_cnpj, ml_auto, ml_sugestao
    diferenca_valor: Decimal
    diferenca_dias: int


class DecisaoMatch(BaseModel):
    """Decisão do funcionário sobre um match sugerido."""
    lancamento_banco_id: UUID
    lancamento_omie_id: UUID | None = None  # None = sem correspondência
    aceitar: bool
    obs: str | None = None


class ConciliacaoResponse(BaseModel):
    """Registro de conciliação."""
    id: UUID
    lancamento_banco: LancamentoBancoResponse | None
    lancamento_omie: LancamentoOmieResponse | None
    empresa_nome: str
    data_referencia: date
    status: str
    confidence_score: float | None
    metodo: str
    conciliado_por_nome: str | None = None
    obs: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConciliacaoEstatisticas(BaseModel):
    """Estatísticas de conciliação para o dashboard."""
    total_conciliados: int
    total_pendentes: int
    total_divergentes: int
    total_revisao_manual: int
    taxa_automatica: float  # percentual conciliado automaticamente
    por_metodo: dict[str, int]
