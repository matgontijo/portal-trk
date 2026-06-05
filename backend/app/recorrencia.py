# trk-universe/backend/app/recorrencia.py
# Motor de recorrência (Todoist-like). Puro, testável.

import calendar
from datetime import date


def _d(v):
    try:
        return date.fromisoformat(str(v)[:10])
    except Exception:
        return None


def ocorre_em(tipo: str | None, config: dict | None, dias_semana: list | None, dia: date, preview: int | None = None) -> bool:
    tipo = (tipo or "semanal").lower()
    config = config or {}
    dias_semana = dias_semana or []
    if tipo == "diaria":
        return not (config.get("apenas_dias_uteis") and dia.isoweekday() > 5)
    if tipo == "semanal":
        return (preview or dia.isoweekday()) in dias_semana
    if tipo == "intervalo":
        cada = int(config.get("cada_dias", 1) or 1)
        ini = _d(config.get("inicio")) or dia
        return cada > 0 and dia >= ini and (dia - ini).days % cada == 0
    if tipo == "mensal":
        if config.get("ultimo_dia"):
            return dia.day == calendar.monthrange(dia.year, dia.month)[1]
        return dia.day in (config.get("dias_mes") or [])
    if tipo == "datas":
        return dia.isoformat() in (config.get("datas") or [])
    return False


def descrever(tipo: str | None, config: dict | None, dias_semana: list | None) -> str:
    tipo = (tipo or "semanal").lower()
    config = config or {}
    nomes = {1: "seg", 2: "ter", 3: "qua", 4: "qui", 5: "sex", 6: "sáb", 7: "dom"}
    if tipo == "diaria":
        return "Dias úteis" if config.get("apenas_dias_uteis") else "Todos os dias"
    if tipo == "semanal":
        d = ", ".join(nomes.get(x, str(x)) for x in sorted(dias_semana or []))
        return f"Semanal: {d}" if d else "Semanal"
    if tipo == "intervalo":
        return f"A cada {config.get('cada_dias', 1)} dia(s)"
    if tipo == "mensal":
        return "Último dia do mês" if config.get("ultimo_dia") else "Mensal: dias " + ", ".join(map(str, config.get("dias_mes") or []))
    if tipo == "datas":
        return f"{len(config.get('datas') or [])} data(s)"
    return "Semanal"
