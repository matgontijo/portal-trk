# backend/tests/test_providers.py
# Testes da camada de providers simulados (mock testável).

from datetime import date
from decimal import Decimal

from app.services.providers.base import LancamentoExtrato, SaldoBancario
from app.services.providers.fake import FakeBankProvider, FakeOmieProvider


async def test_fake_bank_retorna_saldo_positivo():
    prov = FakeBankProvider(cnpj="12345678000199", nome_banco="inter")
    saldo = await prov.obter_saldo()
    assert isinstance(saldo, SaldoBancario)
    assert isinstance(saldo.saldo, Decimal)
    assert saldo.saldo > 0
    assert saldo.moeda == "BRL"


async def test_fake_bank_determinismo():
    """Mesma empresa => mesmo saldo (chave estável)."""
    a = await FakeBankProvider(cnpj="99887766000155").obter_saldo()
    b = await FakeBankProvider(cnpj="99887766000155").obter_saldo()
    assert a.saldo == b.saldo


async def test_fake_bank_empresas_diferentes_saldos_diferentes():
    a = await FakeBankProvider(cnpj="11111111000111").obter_saldo()
    b = await FakeBankProvider(cnpj="22222222000122").obter_saldo()
    assert a.saldo != b.saldo


async def test_fake_extrato_tem_lancamentos_validos():
    prov = FakeBankProvider(cnpj="12345678000199")
    extrato = await prov.obter_extrato(date(2026, 6, 4), date(2026, 6, 4))
    assert len(extrato) >= 2
    for lanc in extrato:
        assert isinstance(lanc, LancamentoExtrato)
        assert lanc.valor > 0  # valor sempre positivo
        assert lanc.tipo in ("debito", "credito")
        assert lanc.identificador  # idempotência depende disso


async def test_fake_omie_determinismo():
    ref = date(2026, 6, 4)
    saldo_ref = Decimal("100000.00")
    a = await FakeOmieProvider("12345678000199", saldo_ref).obter_saldo_esperado(ref)
    b = await FakeOmieProvider("12345678000199", saldo_ref).obter_saldo_esperado(ref)
    assert a == b
