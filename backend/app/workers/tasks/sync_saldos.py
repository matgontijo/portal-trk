# backend/app/workers/tasks/sync_saldos.py
# Task Celery para sincronização e VERIFICAÇÃO de saldos bancários.
# Executa nos horários configurados (padrão 06:00 e 20:00 BRT).
#
# Para cada empresa:
#   1. Coleta saldo no banco (real ou simulado) + posição no Omie.
#   2. Classifica divergência e grava 1 snapshot/dia (idempotente).
#   3. Persiste o extrato do dia.
#   4. Notifica o responsável quando há divergência ou falha de sync.
#
# Resiliência: cada empresa é processada e COMMITADA isoladamente — a falha
# de uma (ou de um banco) nunca derruba as demais.

from datetime import date, datetime, timezone

import structlog

from app.workers.celery_app import celery

logger = structlog.get_logger()


def _get_db_session():
    """Cria sessão síncrona para uso nos tasks Celery."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.core.config import get_settings
    settings = get_settings()
    sync_url = settings.database_url_sync
    engine = create_engine(sync_url)
    return Session(engine)


@celery.task(name="app.workers.tasks.sync_saldos.sync_todas_empresas", bind=True, max_retries=3)
def sync_todas_empresas(self):
    """Sincroniza saldos de todas as empresas ativas."""
    session = _get_db_session()
    sucesso = 0
    falhas = 0
    divergencias = 0
    try:
        from app.db.models.empresa import Empresa
        empresas = session.query(Empresa).filter(Empresa.is_active == True).all()  # noqa: E712
        logger.info("sync_iniciado", total_empresas=len(empresas))

        for empresa in empresas:
            resultado = _sync_empresa_isolado(session, empresa)
            if resultado == "erro":
                falhas += 1
            else:
                sucesso += 1
                if resultado == "divergencia":
                    divergencias += 1

        logger.info(
            "sync_concluido",
            sucesso=sucesso, falhas=falhas, divergencias=divergencias,
        )
        return {"sucesso": sucesso, "falhas": falhas, "divergencias": divergencias}

    except Exception as e:  # erro estrutural (ex.: banco indisponível) -> retry
        logger.error("sync_erro_geral", erro=str(e))
        raise self.retry(exc=e, countdown=60)
    finally:
        session.close()


@celery.task(name="app.workers.tasks.sync_saldos.sync_empresa_task")
def sync_empresa_task(empresa_id: str):
    """Sync manual de uma empresa específica (disparado pela UI)."""
    from uuid import UUID
    from app.db.models.empresa import Empresa

    session = _get_db_session()
    try:
        empresa = session.query(Empresa).filter(Empresa.id == UUID(empresa_id)).first()
        if not empresa:
            logger.warning("sync_manual_empresa_inexistente", empresa_id=empresa_id)
            return {"status": "nao_encontrada"}
        resultado = _sync_empresa_isolado(session, empresa)
        logger.info("sync_manual_concluido", empresa=empresa.nome, resultado=resultado)
        return {"status": resultado}
    finally:
        session.close()


def _sync_empresa_isolado(session, empresa) -> str:
    """Processa UMA empresa em transação isolada.
    Retorna: "ok" | "divergencia" | "erro"."""
    from app.services.automacoes import disparar
    from app.services.saldo_sync import sincronizar_empresa_sync

    try:
        saldo = sincronizar_empresa_sync(session, empresa)
        contexto = {
            "empresa_id": empresa.id,
            "empresa_nome": empresa.nome,
            "user_id": empresa.responsavel_user_id,
            "delta": float(saldo.delta),
            "delta_abs": float(abs(saldo.delta)),
            "saldo_banco": float(saldo.saldo_banco),
            "saldo_omie": float(saldo.saldo_omie),
            "tipo_divergencia": saldo.tipo_divergencia,
        }
        if saldo.tem_divergencia:
            _notificar_divergencia(session, empresa, saldo)
            disparar(session, "saldo_divergencia", contexto)
            session.commit()
            logger.info(
                "sync_empresa_divergencia",
                empresa=empresa.nome, delta=str(saldo.delta), tipo=saldo.tipo_divergencia,
            )
            return "divergencia"
        disparar(session, "saldo_atualizado", contexto)
        session.commit()
        logger.info("sync_empresa_ok", empresa=empresa.nome, saldo=str(saldo.saldo_banco))
        return "ok"
    except Exception as e:  # noqa: BLE001
        session.rollback()
        logger.error("sync_empresa_erro", empresa=getattr(empresa, "nome", "?"), erro=str(e))
        _registrar_falha_sync(session, empresa, str(e))
        try:
            disparar(session, "saldo_falha", {
                "empresa_id": empresa.id, "empresa_nome": empresa.nome,
                "user_id": empresa.responsavel_user_id, "erro": str(e)[:200],
            })
            session.commit()
        except Exception:  # noqa: BLE001
            session.rollback()
        return "erro"


def _notificar_divergencia(session, empresa, saldo) -> None:
    """Cria notificação in-app para o responsável da empresa."""
    if not empresa.responsavel_user_id:
        return
    from app.db.models.notificacao import Notificacao

    sinal = "acima" if saldo.delta > 0 else "abaixo"
    valor = abs(saldo.delta)
    session.add(
        Notificacao(
            user_id=empresa.responsavel_user_id,
            tipo="divergencia",
            titulo=f"Divergência de saldo · {empresa.nome}",
            mensagem=(
                f"Saldo do banco está R$ {valor:,.2f} {sinal} da posição do Omie "
                f"({saldo.tipo_divergencia.replace('_', ' ')}). Verifique a conciliação."
            ),
            link_acao=f"/conciliacao?empresa={empresa.id}",
        )
    )


def _registrar_falha_sync(session, empresa, erro: str) -> None:
    """Notifica o responsável quando o sync de uma empresa falha."""
    if not empresa.responsavel_user_id:
        return
    try:
        from app.db.models.notificacao import Notificacao
        session.add(
            Notificacao(
                user_id=empresa.responsavel_user_id,
                tipo="sistema",
                titulo=f"Falha ao atualizar saldo · {empresa.nome}",
                mensagem=f"Não foi possível obter o saldo hoje: {erro[:200]}",
                link_acao=f"/empresas?empresa={empresa.id}",
            )
        )
        session.commit()
    except Exception:  # noqa: BLE001 — notificação é best-effort
        session.rollback()
