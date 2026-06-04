# backend/tests/test_saldo_sync.py
# Testes da lógica pura de divergência e da coleta de snapshot.

from datetime import date
from decimal import Decimal

from app.services.saldo_sync import classificar_divergencia, coletar_snapshot


def test_sem_divergencia_dentro_da_tolerancia():
    r = classificar_divergencia(Decimal("1000.00"), Decimal("1000.03"), Decimal("0.05"))
    assert r.tem_divergencia is False
    assert r.tipo == "sem_divergencia"


def test_divergencia_banco_maior_que_omie():
    r = classificar_divergencia(Decimal("1500.00"), Decimal("1000.00"), Decimal("0.05"))
    assert r.tem_divergencia is True
    assert r.tipo == "lancamento_nao_identificado"
    assert r.delta == Decimal("500.00")


def test_divergencia_omie_maior_que_banco():
    r = classificar_divergencia(Decimal("800.00"), Decimal("1000.00"), Decimal("0.05"))
    assert r.tem_divergencia is True
    assert r.tipo == "pagamento_nao_processado"
    assert r.delta == Decimal("-200.00")


def test_limite_exato_da_tolerancia_nao_e_divergencia():
    r = classificar_divergencia(Decimal("1000.05"), Decimal("1000.00"), Decimal("0.05"))
    assert r.tem_divergencia is False


async def test_coletar_snapshot_determinismo(empresa_fake):
    ref = date(2026, 6, 4)
    a = await coletar_snapshot(empresa_fake, ref)
    b = await coletar_snapshot(empresa_fake, ref)
    assert a.saldo_banco == b.saldo_banco
    assert a.saldo_omie == b.saldo_omie
    assert a.delta == b.delta
    assert a.tem_divergencia == b.tem_divergencia


async def test_coletar_snapshot_coerencia_do_delta(empresa_fake):
    snap = await coletar_snapshot(empresa_fake, date(2026, 6, 4))
    assert snap.delta == (snap.saldo_banco - snap.saldo_omie)
    assert snap.data_referencia == date(2026, 6, 4)
    assert len(snap.extrato) >= 1
