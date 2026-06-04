# backend/app/services/providers/base.py
# Tipos normalizados e protocolos para integração bancária / Omie.
#
# DECISÃO DE ARQUITETURA:
# Toda a aplicação fala com bancos e com o Omie através destes tipos
# normalizados — nunca com o JSON cru de cada provedor. Isso permite:
#   1. Trocar "fake" por "real" sem tocar no worker / serviço de sync.
#   2. Testar a lógica de saldo/divergência sem rede e sem credenciais.
#   3. Adicionar um novo banco implementando apenas o adapter.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class SaldoBancario:
    """Saldo normalizado retornado por qualquer banco."""

    saldo: Decimal
    moeda: str = "BRL"
    atualizado_em: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class LancamentoExtrato:
    """Lançamento normalizado de extrato (valor sempre positivo; sinal vai em `tipo`)."""

    data: date
    valor: Decimal
    tipo: str  # "debito" | "credito"
    descricao: str = ""
    identificador: str | None = None
    cnpj_contraparte: str | None = None
    raw: dict = field(default_factory=dict)


@runtime_checkable
class BankProvider(Protocol):
    """Contrato que todo client bancário (real ou fake) deve cumprir."""

    nome_banco: str

    async def obter_saldo(self) -> SaldoBancario: ...

    async def obter_extrato(
        self, inicio: date, fim: date
    ) -> list[LancamentoExtrato]: ...


@runtime_checkable
class OmieProvider(Protocol):
    """Contrato para obter a posição de caixa esperada no ERP (Omie)."""

    async def obter_saldo_esperado(self, referencia: date) -> Decimal: ...
