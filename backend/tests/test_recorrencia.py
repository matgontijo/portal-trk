# backend/tests/test_recorrencia.py
# Testes do motor de recorrência de rotinas (estilo Todoist).

from datetime import date

from app.services.recorrencia import descrever_recorrencia, rotina_ocorre_em

# 2026-06-04 é uma quinta-feira (isoweekday=4)
QUINTA = date(2026, 6, 4)
SABADO = date(2026, 6, 6)


def test_diaria_ocorre_sempre():
    assert rotina_ocorre_em("diaria", {}, [], QUINTA) is True
    assert rotina_ocorre_em("diaria", {}, [], SABADO) is True


def test_diaria_apenas_dias_uteis_pula_fim_de_semana():
    assert rotina_ocorre_em("diaria", {"apenas_dias_uteis": True}, [], QUINTA) is True
    assert rotina_ocorre_em("diaria", {"apenas_dias_uteis": True}, [], SABADO) is False


def test_semanal_usa_dias_semana():
    assert rotina_ocorre_em("semanal", {}, [4], QUINTA) is True   # quinta
    assert rotina_ocorre_em("semanal", {}, [1, 2], QUINTA) is False


def test_semanal_preview_por_dia():
    # dia_preview força a avaliação por dia da semana (sem depender da data)
    assert rotina_ocorre_em("semanal", {}, [1], QUINTA, dia_preview=1) is True
    assert rotina_ocorre_em("semanal", {}, [1], QUINTA, dia_preview=2) is False


def test_intervalo_cada_n_dias():
    cfg = {"cada_dias": 3, "inicio": "2026-06-01"}
    assert rotina_ocorre_em("intervalo", cfg, [], date(2026, 6, 1)) is True   # dia 0
    assert rotina_ocorre_em("intervalo", cfg, [], date(2026, 6, 4)) is True   # +3
    assert rotina_ocorre_em("intervalo", cfg, [], date(2026, 6, 5)) is False
    assert rotina_ocorre_em("intervalo", cfg, [], date(2026, 5, 30)) is False  # antes do início


def test_mensal_dias_do_mes():
    cfg = {"dias_mes": [1, 15]}
    assert rotina_ocorre_em("mensal", cfg, [], date(2026, 6, 15)) is True
    assert rotina_ocorre_em("mensal", cfg, [], date(2026, 6, 10)) is False


def test_mensal_ultimo_dia():
    cfg = {"ultimo_dia": True}
    assert rotina_ocorre_em("mensal", cfg, [], date(2026, 6, 30)) is True   # junho tem 30
    assert rotina_ocorre_em("mensal", cfg, [], date(2026, 2, 28)) is True   # fev 2026 (não bissexto)
    assert rotina_ocorre_em("mensal", cfg, [], date(2026, 6, 29)) is False


def test_datas_especificas():
    cfg = {"datas": ["2026-06-04", "2026-12-25"]}
    assert rotina_ocorre_em("datas", cfg, [], QUINTA) is True
    assert rotina_ocorre_em("datas", cfg, [], date(2026, 6, 5)) is False


def test_descrever_recorrencia():
    assert "dia" in descrever_recorrencia("diaria", {}, []).lower()
    assert descrever_recorrencia("intervalo", {"cada_dias": 5}, []) == "A cada 5 dia(s)"
    assert "último" in descrever_recorrencia("mensal", {"ultimo_dia": True}, []).lower()
