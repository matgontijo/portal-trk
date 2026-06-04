# backend/app/services/automacoes.py
# Engine de avaliação e execução de automações.
#
# A avaliação de condições é PURA (sem I/O) — totalmente testável.
# A execução de ações usa uma Session SÍNCRONA (chamada pelos workers Celery).

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import structlog

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────
# Avaliação de condições (pura)
# ─────────────────────────────────────────────────────────────────────────

def _coerce(valor: Any) -> Any:
    """Converte para Decimal quando ambos os lados parecem numéricos."""
    if isinstance(valor, bool):
        return valor
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return valor


def _comparar(esquerda: Any, op: str, direita: Any) -> bool:
    e, d = _coerce(esquerda), _coerce(direita)
    try:
        if op in ("==", "eq"):
            return e == d
        if op in ("!=", "ne"):
            return e != d
        if op in (">", "gt"):
            return e > d
        if op in (">=", "gte"):
            return e >= d
        if op in ("<", "lt"):
            return e < d
        if op in ("<=", "lte"):
            return e <= d
        if op in ("contains", "contem"):
            return str(direita).lower() in str(esquerda).lower()
        if op in ("in",):
            return esquerda in direita if isinstance(direita, (list, tuple, set)) else False
    except (TypeError, InvalidOperation):
        return False
    logger.warning("automacao_operador_desconhecido", op=op)
    return False


def avaliar_condicao(condicao: dict | None, contexto: dict) -> bool:
    """Avalia o bloco de condições contra o contexto do evento.

    Formato: {"logica": "and"|"or", "regras": [{"campo","op","valor"}, ...]}
    Sem regras => sempre True (a automação dispara sempre que o gatilho ocorre).
    """
    if not condicao:
        return True
    regras = condicao.get("regras") or []
    if not regras:
        return True
    logica = (condicao.get("logica") or "and").lower()

    resultados = [
        _comparar(contexto.get(r.get("campo")), r.get("op", "=="), r.get("valor"))
        for r in regras
    ]
    return any(resultados) if logica == "or" else all(resultados)


# ─────────────────────────────────────────────────────────────────────────
# Execução de ações (Session síncrona — workers)
# ─────────────────────────────────────────────────────────────────────────

def _render(template: str, contexto: dict) -> str:
    """Substitui {placeholders} pelo contexto (sem quebrar se faltar chave)."""
    out = template or ""
    for k, v in contexto.items():
        out = out.replace("{" + str(k) + "}", str(v))
    return out


def executar_acao(session, automacao, contexto: dict) -> bool:
    """Executa a ação de uma automação. Retorna True se executou."""
    cfg = automacao.acao_config or {}

    if automacao.acao == "notificar":
        from app.db.models.notificacao import Notificacao
        user_id = cfg.get("user_id") or contexto.get("user_id")
        if not user_id:
            return False
        session.add(Notificacao(
            user_id=user_id,
            tipo=cfg.get("tipo", "sistema"),
            titulo=_render(cfg.get("titulo", automacao.nome), contexto),
            mensagem=_render(cfg.get("mensagem", ""), contexto),
            link_acao=cfg.get("link_acao"),
        ))
        return True

    if automacao.acao == "criar_tarefa":
        from app.db.models.tarefa import Tarefa
        prazo = None
        if cfg.get("prazo_dias") is not None:
            prazo = datetime.now(timezone.utc) + timedelta(days=int(cfg["prazo_dias"]))
        session.add(Tarefa(
            titulo=_render(cfg.get("titulo", automacao.nome), contexto),
            descricao=_render(cfg.get("descricao", ""), contexto),
            prioridade=cfg.get("prioridade", "normal"),
            status="todo",
            prazo=prazo,
            atribuido_a=cfg.get("atribuido_a") or contexto.get("user_id"),
            empresa_id=contexto.get("empresa_id"),
        ))
        return True

    if automacao.acao == "whatsapp":
        # Best-effort: registra intenção; o envio real depende do serviço WhatsApp.
        logger.info("automacao_whatsapp", para=cfg.get("para"), msg=_render(cfg.get("mensagem", ""), contexto))
        return True

    if automacao.acao == "webhook":
        logger.info("automacao_webhook", url=cfg.get("url"), contexto=contexto)
        return True

    logger.warning("automacao_acao_desconhecida", acao=automacao.acao)
    return False


def disparar(session, gatilho: str, contexto: dict) -> int:
    """Avalia e executa todas as automações ativas para um gatilho.

    Usado pelos workers (Session síncrona). Retorna quantas executaram.
    Nunca propaga exceção — automação não pode derrubar o fluxo principal.
    """
    from app.db.models.automacao import Automacao

    executadas = 0
    try:
        autos = (
            session.query(Automacao)
            .filter(Automacao.gatilho == gatilho, Automacao.ativa == True)  # noqa: E712
            .order_by(Automacao.prioridade.desc())
            .all()
        )
    except Exception as e:  # noqa: BLE001 — tabela pode não existir em DB antigo
        logger.warning("automacao_query_erro", erro=str(e))
        return 0

    for auto in autos:
        try:
            if not avaliar_condicao(auto.condicao, contexto):
                continue
            if executar_acao(session, auto, contexto):
                auto.execucoes = (auto.execucoes or 0) + 1
                executadas += 1
        except Exception as e:  # noqa: BLE001
            logger.error("automacao_execucao_erro", automacao=auto.nome, erro=str(e))

    if executadas:
        logger.info("automacoes_disparadas", gatilho=gatilho, total=executadas)
    return executadas
