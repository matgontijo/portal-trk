# backend/app/services/providers/real.py
# Adapters que normalizam os clients reais (Inter / Santander / Bradesco / Omie)
# para os tipos do `base.py`. A parsing é defensiva: formatos variam entre
# bancos e versões de API, então toleramos chaves ausentes sem quebrar o sync.

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

import structlog

from .base import LancamentoErp, LancamentoExtrato, SaldoBancario

logger = structlog.get_logger()


def _to_decimal(valor) -> Decimal:
    try:
        return Decimal(str(valor)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _primeiro(d: dict, *chaves, default=None):
    """Retorna o primeiro valor presente entre várias chaves possíveis."""
    for k in chaves:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return default


class InterAdapter:
    nome_banco = "inter"

    def __init__(self, client):
        self._client = client

    async def obter_saldo(self) -> SaldoBancario:
        raw = await self._client.obter_saldo()
        # API Inter: { "disponivel": 1234.56, ... }
        valor = _primeiro(raw, "disponivel", "saldo", "available", default=0)
        return SaldoBancario(saldo=_to_decimal(valor), raw=raw)

    async def obter_extrato(self, inicio: date, fim: date) -> list[LancamentoExtrato]:
        raw = await self._client.obter_extrato(inicio.isoformat(), fim.isoformat())
        itens = _primeiro(raw, "transacoes", "transactions", default=[]) or []
        out: list[LancamentoExtrato] = []
        for t in itens:
            tipo_raw = str(_primeiro(t, "tipoOperacao", "type", default="")).upper()
            tipo = "credito" if tipo_raw.startswith("C") else "debito"
            out.append(
                LancamentoExtrato(
                    data=_parse_data(_primeiro(t, "dataEntrada", "data", default=inicio.isoformat())),
                    valor=abs(_to_decimal(_primeiro(t, "valor", "amount", default=0))),
                    tipo=tipo,
                    descricao=str(_primeiro(t, "descricao", "titulo", default="")),
                    identificador=_primeiro(t, "idTransacao", "transactionId"),
                    raw=t,
                )
            )
        return out


class OpenFinanceAdapter:
    """Adapter genérico para Santander/Bradesco (formato Open Finance Brasil)."""

    def __init__(self, client, nome_banco: str):
        self._client = client
        self.nome_banco = nome_banco

    async def obter_saldo(self) -> SaldoBancario:
        raw = await self._client.obter_saldo()
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        if isinstance(data, list) and data:
            data = data[0]
        valor = _primeiro(data, "availableAmount", "amount", "saldo", default=0)
        if isinstance(valor, dict):
            valor = _primeiro(valor, "amount", "value", default=0)
        return SaldoBancario(saldo=_to_decimal(valor), raw=raw)

    async def obter_extrato(self, inicio: date, fim: date) -> list[LancamentoExtrato]:
        raw = await self._client.obter_transacoes(inicio.isoformat(), fim.isoformat())
        data = raw.get("data", raw) if isinstance(raw, dict) else {}
        itens = data.get("transactions", []) if isinstance(data, dict) else (data or [])
        out: list[LancamentoExtrato] = []
        for t in itens:
            tipo_raw = str(_primeiro(t, "creditDebitType", "type", default="")).upper()
            tipo = "credito" if "CRED" in tipo_raw else "debito"
            amount = _primeiro(t, "amount", "transactionAmount", default=0)
            if isinstance(amount, dict):
                amount = _primeiro(amount, "amount", "value", default=0)
            out.append(
                LancamentoExtrato(
                    data=_parse_data(_primeiro(t, "bookingDate", "transactionDate", default=inicio.isoformat())),
                    valor=abs(_to_decimal(amount)),
                    tipo=tipo,
                    descricao=str(_primeiro(t, "transactionName", "remittanceInformation", default="")),
                    identificador=_primeiro(t, "transactionId"),
                    raw=t,
                )
            )
        return out


class OmieRealProvider:
    """Calcula a posição esperada somando contas a pagar/receber em aberto.
    Best-effort: se a API não responder, o serviço de sync trata o erro."""

    def __init__(self, client):
        self._client = client

    async def obter_saldo_esperado(self, referencia: date) -> Decimal:
        receber = await self._somar(self._client.listar_contas_receber)
        pagar = await self._somar(self._client.listar_contas_pagar)
        return (receber - pagar).quantize(Decimal("0.01"))

    async def obter_lancamentos(self, referencia: date) -> list[LancamentoErp]:
        """Lista contas a pagar/receber em aberto como lançamentos do ERP."""
        out: list[LancamentoErp] = []
        for metodo in (self._client.listar_contas_receber, self._client.listar_contas_pagar):
            try:
                resp = await metodo()
            except Exception as e:  # noqa: BLE001
                logger.warning("omie_lancamentos_erro", erro=str(e))
                continue
            registros = []
            if isinstance(resp, dict):
                for chave in ("conta_pagar_cadastro", "conta_receber_cadastro", "lancamentos"):
                    if isinstance(resp.get(chave), list):
                        registros = resp[chave]
                        break
            for r in registros:
                out.append(LancamentoErp(
                    data=_parse_data(_primeiro(r, "data_emissao", "data_previsao", default=referencia.isoformat())),
                    valor=abs(_to_decimal(_primeiro(r, "valor_documento", "valor", default=0))),
                    descricao=str(_primeiro(r, "observacao", "categoria", default="")),
                    numero_documento=str(_primeiro(r, "numero_documento", "numero_titulo", default="") or ""),
                    id_omie=_primeiro(r, "codigo_lancamento_omie", "codigo_lancamento"),
                    data_vencimento=_parse_data(_primeiro(r, "data_vencimento", default=referencia.isoformat())),
                    status=str(_primeiro(r, "status_titulo", default="aberto")),
                    raw=r,
                ))
        return out

    @staticmethod
    async def _somar(metodo) -> Decimal:
        total = Decimal("0.00")
        try:
            resp = await metodo()
        except Exception as e:  # noqa: BLE001 — best-effort, erro tratado acima
            logger.warning("omie_listar_erro", erro=str(e))
            return total
        registros = []
        if isinstance(resp, dict):
            for chave in ("conta_pagar_cadastro", "conta_receber_cadastro", "lancamentos"):
                if isinstance(resp.get(chave), list):
                    registros = resp[chave]
                    break
        for r in registros:
            total += _to_decimal(_primeiro(r, "valor_documento", "valor", default=0))
        return total


def _parse_data(valor: str) -> date:
    try:
        return datetime.fromisoformat(str(valor)[:10]).date()
    except (ValueError, TypeError):
        return datetime.now(timezone.utc).date()
