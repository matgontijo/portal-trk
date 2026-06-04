# backend/app/services/recorrencia.py
# Motor de recorrência de rotinas (estilo Todoist). Lógica PURA — sem I/O.
#
# Tipos suportados:
#   - "diaria"   : todo dia (opcional: apenas_dias_uteis)
#   - "semanal"  : usa dias_semana (1=seg ... 7=dom)  [compatível com o legado]
#   - "intervalo": a cada N dias a partir de uma data início
#   - "mensal"   : em dias específicos do mês (ou no último dia / 1º dia útil)
#   - "datas"    : conjunto explícito de datas (YYYY-MM-DD)

from __future__ import annotations

import calendar
from datetime import date

TIPOS_RECORRENCIA = ("diaria", "semanal", "intervalo", "mensal", "datas")


def _parse_date(valor) -> date | None:
    try:
        return date.fromisoformat(str(valor)[:10])
    except (ValueError, TypeError):
        return None


def _primeiro_dia_util(ano: int, mes: int) -> int:
    """Retorna o dia do mês do 1º dia útil (seg-sex)."""
    d = date(ano, mes, 1)
    while d.isoweekday() > 5:
        d = date(ano, mes, d.day + 1)
    return d.day


def rotina_ocorre_em(
    tipo: str | None,
    config: dict | None,
    dias_semana: list[int] | None,
    data: date,
    dia_preview: int | None = None,
) -> bool:
    """Decide se uma rotina ocorre em `data`.

    `dia_preview` (1..7) permite pré-visualizar rotinas semanais por dia da
    semana mesmo sem uma data específica (mantém compatibilidade com a UI).
    """
    tipo = (tipo or "semanal").lower()
    config = config or {}
    dias_semana = dias_semana or []

    if tipo == "diaria":
        if config.get("apenas_dias_uteis") and data.isoweekday() > 5:
            return False
        return True

    if tipo == "semanal":
        wd = dia_preview or data.isoweekday()
        return wd in dias_semana

    if tipo == "intervalo":
        cada = int(config.get("cada_dias", 1) or 1)
        if cada <= 0:
            return False
        inicio = _parse_date(config.get("inicio")) or data
        if data < inicio:
            return False
        return (data - inicio).days % cada == 0

    if tipo == "mensal":
        if config.get("ultimo_dia"):
            ultimo = calendar.monthrange(data.year, data.month)[1]
            return data.day == ultimo
        if config.get("primeiro_dia_util"):
            return data.day == _primeiro_dia_util(data.year, data.month)
        return data.day in (config.get("dias_mes") or [])

    if tipo == "datas":
        return data.isoformat() in (config.get("datas") or [])

    return False


def descrever_recorrencia(tipo: str | None, config: dict | None, dias_semana: list[int] | None) -> str:
    """Texto amigável da recorrência (para a UI)."""
    tipo = (tipo or "semanal").lower()
    config = config or {}
    nomes = {1: "seg", 2: "ter", 3: "qua", 4: "qui", 5: "sex", 6: "sáb", 7: "dom"}
    if tipo == "diaria":
        return "Todos os dias úteis" if config.get("apenas_dias_uteis") else "Todos os dias"
    if tipo == "semanal":
        dias = ", ".join(nomes.get(d, str(d)) for d in sorted(dias_semana or []))
        return f"Toda semana: {dias}" if dias else "Semanal"
    if tipo == "intervalo":
        return f"A cada {config.get('cada_dias', 1)} dia(s)"
    if tipo == "mensal":
        if config.get("ultimo_dia"):
            return "Todo último dia do mês"
        if config.get("primeiro_dia_util"):
            return "Todo 1º dia útil do mês"
        dias = ", ".join(f"dia {d}" for d in (config.get("dias_mes") or []))
        return f"Todo mês: {dias}" if dias else "Mensal"
    if tipo == "datas":
        return f"{len(config.get('datas') or [])} data(s) específica(s)"
    return "Semanal"
