# backend/app/services/saldo_sync.py
# Serviço de sincronização e verificação de saldo bancário diário.
#
# Este é o módulo que substitui o antigo placeholder (que gravava R$ 0,00).
# Responsabilidades:
#   1. Coletar o saldo real (ou simulado) no banco e a posição esperada no Omie.
#   2. Classificar divergências de forma determinística e auditável.
#   3. Gravar 1 snapshot por empresa/dia (idempotente — re-sync atualiza, não duplica).
#   4. Persistir o extrato do dia (alimenta a conciliação).
#
# A lógica de classificação é PURA (sem I/O) — testável sem banco nem rede.

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

import structlog

from app.core.config import get_settings
from app.services.providers import get_bank_provider, get_omie_provider

logger = structlog.get_logger()

CENTAVOS = Decimal("0.01")


@dataclass(slots=True)
class ResultadoDivergencia:
    tem_divergencia: bool
    tipo: str
    delta: Decimal


def classificar_divergencia(
    saldo_banco: Decimal,
    saldo_omie: Decimal,
    tolerancia: Decimal = Decimal("0.05"),
) -> ResultadoDivergencia:
    """Compara saldo do banco x posição esperada no Omie.

    Heurística (nível de saldo):
      - |delta| <= tolerância  -> sem divergência
      - banco  > omie          -> entrou dinheiro que o ERP não registrou
                                   (lancamento_nao_identificado)
      - omie   > banco         -> ERP espera movimento que o banco não refletiu
                                   (pagamento_nao_processado)
    """
    delta = (saldo_banco - saldo_omie).quantize(CENTAVOS)
    if abs(delta) <= tolerancia:
        return ResultadoDivergencia(False, "sem_divergencia", delta)
    if delta > 0:
        return ResultadoDivergencia(True, "lancamento_nao_identificado", delta)
    return ResultadoDivergencia(True, "pagamento_nao_processado", delta)


@dataclass(slots=True)
class SnapshotSaldo:
    """Resultado completo de uma coleta — pronto para persistir."""

    saldo_banco: Decimal
    saldo_omie: Decimal
    delta: Decimal
    tem_divergencia: bool
    tipo_divergencia: str
    data_referencia: date
    synced_at: datetime
    raw_bank_json: dict
    raw_omie_json: dict
    extrato: list  # list[LancamentoExtrato]


async def coletar_snapshot(empresa, referencia: date | None = None) -> SnapshotSaldo:
    """Coleta saldo do banco + posição do Omie e classifica a divergência.
    Não toca no banco de dados — apenas coleta e calcula."""
    settings = get_settings()
    hoje = referencia or date.today()
    tolerancia = Decimal(str(getattr(settings, "BANK_DIVERGENCIA_TOLERANCIA", "0.05")))

    bank = get_bank_provider(empresa)
    saldo_bancario = await bank.obter_saldo()
    extrato = await bank.obter_extrato(hoje, hoje)

    omie = get_omie_provider(empresa, saldo_banco_ref=saldo_bancario.saldo)
    saldo_omie = await omie.obter_saldo_esperado(hoje)

    div = classificar_divergencia(saldo_bancario.saldo, saldo_omie, tolerancia)

    return SnapshotSaldo(
        saldo_banco=saldo_bancario.saldo,
        saldo_omie=saldo_omie.quantize(CENTAVOS),
        delta=div.delta,
        tem_divergencia=div.tem_divergencia,
        tipo_divergencia=div.tipo,
        data_referencia=hoje,
        synced_at=datetime.now(timezone.utc),
        raw_bank_json=saldo_bancario.raw,
        raw_omie_json={"saldo_esperado": str(saldo_omie)},
        extrato=extrato,
    )


def sincronizar_empresa_sync(session, empresa, referencia: date | None = None):
    """Wrapper síncrono (para Celery) que coleta + persiste o snapshot do dia.

    Idempotente: um único registro de saldo por (empresa, data_referencia).
    Retorna o objeto Saldo persistido.
    """
    from app.db.models.lancamento import LancamentoBanco
    from app.db.models.saldo import Saldo

    snap = asyncio.run(coletar_snapshot(empresa, referencia))

    # ─── Upsert do saldo do dia (idempotente) ───
    saldo = (
        session.query(Saldo)
        .filter(Saldo.empresa_id == empresa.id, Saldo.data_referencia == snap.data_referencia)
        .first()
    )
    if saldo is None:
        saldo = Saldo(empresa_id=empresa.id, data_referencia=snap.data_referencia)
        session.add(saldo)

    saldo.saldo_banco = snap.saldo_banco
    saldo.saldo_omie = snap.saldo_omie
    saldo.delta = snap.delta
    saldo.tem_divergencia = snap.tem_divergencia
    saldo.tipo_divergencia = snap.tipo_divergencia
    saldo.synced_at = snap.synced_at
    saldo.raw_bank_json = snap.raw_bank_json
    saldo.raw_omie_json = snap.raw_omie_json

    # ─── Persistir extrato do dia (idempotente por identificador) ───
    for lanc in snap.extrato:
        if lanc.identificador:
            ja_existe = (
                session.query(LancamentoBanco.id)
                .filter(
                    LancamentoBanco.empresa_id == empresa.id,
                    LancamentoBanco.identificador_banco == lanc.identificador,
                )
                .first()
            )
            if ja_existe:
                continue
        session.add(
            LancamentoBanco(
                empresa_id=empresa.id,
                data_lancamento=lanc.data,
                valor=lanc.valor,
                tipo=lanc.tipo,
                descricao=lanc.descricao,
                identificador_banco=lanc.identificador,
                cnpj_contraparte=lanc.cnpj_contraparte,
                synced_at=snap.synced_at,
            )
        )

    return saldo
