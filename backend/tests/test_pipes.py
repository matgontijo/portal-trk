# backend/tests/test_pipes.py
# Testes da lógica pura de SLA e dos templates de pipe.

from datetime import datetime, timedelta, timezone

from app.services.pipes import calcular_sla_status, fases_do_template


def test_sem_sla_sempre_ok():
    assert calcular_sla_status(None, datetime.now(timezone.utc)) == "ok"
    assert calcular_sla_status(0, datetime.now(timezone.utc)) == "ok"


def test_sla_dentro_do_prazo():
    entrou = datetime.now(timezone.utc) - timedelta(hours=1)
    assert calcular_sla_status(48, entrou) == "ok"


def test_sla_em_atencao_acima_de_80pct():
    entrou = datetime.now(timezone.utc) - timedelta(hours=42)  # 87.5% de 48h
    assert calcular_sla_status(48, entrou) == "atencao"


def test_sla_estourado():
    entrou = datetime.now(timezone.utc) - timedelta(hours=50)
    assert calcular_sla_status(48, entrou) == "estourado"


def test_sla_tolera_datetime_naive():
    entrou = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=50)  # naive
    assert calcular_sla_status(48, entrou) == "estourado"


def test_template_padrao_fallback():
    fases = fases_do_template("inexistente")
    assert len(fases) == 3
    assert fases[-1]["is_final"] is True


def test_template_contas_pagar():
    fases = fases_do_template("contas_pagar")
    nomes = [f["nome"] for f in fases]
    assert "Pago" in nomes
    assert any(f.get("sla_horas") for f in fases)
