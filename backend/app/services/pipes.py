# backend/app/services/pipes.py
# Lógica de apoio do subsistema de Pipes.
# calcular_sla_status é PURA (testável sem banco).

from __future__ import annotations

from datetime import datetime, timezone


def calcular_sla_status(
    sla_horas: int | None,
    fase_entrou_em: datetime | None,
    agora: datetime | None = None,
) -> str:
    """Retorna o status de SLA de um card na fase atual.

    - "ok"        : dentro do prazo (ou fase sem SLA)
    - "atencao"   : passou de 80% do SLA
    - "estourado" : passou de 100% do SLA
    """
    if not sla_horas or sla_horas <= 0 or fase_entrou_em is None:
        return "ok"
    agora = agora or datetime.now(timezone.utc)
    if fase_entrou_em.tzinfo is None:
        fase_entrou_em = fase_entrou_em.replace(tzinfo=timezone.utc)
    horas = (agora - fase_entrou_em).total_seconds() / 3600
    if horas >= sla_horas:
        return "estourado"
    if horas >= sla_horas * 0.8:
        return "atencao"
    return "ok"


# ─── Templates de pipe (acelera a criação — estilo "modelos" do Pipefy) ───
# Cores restritas à paleta da marca: slate (neutro), amber (warning), emerald (success).
TEMPLATES: dict[str, list[dict]] = {
    "padrao": [
        {"nome": "A Fazer", "ordem": 0, "cor": "#94a3b8"},
        {"nome": "Em Andamento", "ordem": 1, "cor": "#f59e0b", "sla_horas": 48},
        {"nome": "Concluído", "ordem": 2, "cor": "#10b981", "is_final": True},
    ],
    "contas_pagar": [
        {"nome": "Recebido", "ordem": 0, "cor": "#94a3b8"},
        {"nome": "Em Análise", "ordem": 1, "cor": "#f59e0b", "sla_horas": 24},
        {"nome": "Aprovado", "ordem": 2, "cor": "#475569"},
        {"nome": "Pago", "ordem": 3, "cor": "#10b981", "is_final": True},
    ],
    "onboarding": [
        {"nome": "Lead", "ordem": 0, "cor": "#94a3b8"},
        {"nome": "Documentação", "ordem": 1, "cor": "#f59e0b", "sla_horas": 72},
        {"nome": "Configuração", "ordem": 2, "cor": "#475569"},
        {"nome": "Ativo", "ordem": 3, "cor": "#10b981", "is_final": True},
    ],
}


def fases_do_template(nome: str | None) -> list[dict]:
    """Retorna as fases de um template, com fallback para 'padrao'."""
    return TEMPLATES.get(nome or "padrao", TEMPLATES["padrao"])
