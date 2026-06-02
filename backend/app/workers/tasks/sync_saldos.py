# backend/app/workers/tasks/sync_saldos.py
# Task Celery para sincronização de saldos bancários.
# Executa nos horários configurados (padrão 06:00 e 20:00 BRT).
# Para cada empresa: autentica no banco, busca saldo e extrato,
# salva em saldos e lancamentos_banco, calcula divergência.

import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal

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
    try:
        from app.db.models.empresa import Empresa
        empresas = session.query(Empresa).filter(Empresa.is_active == True).all()

        logger.info("sync_iniciado", total_empresas=len(empresas))

        for empresa in empresas:
            try:
                _sync_empresa(session, empresa)
            except Exception as e:
                logger.error("sync_empresa_erro", empresa=empresa.nome, erro=str(e))

        session.commit()
        logger.info("sync_concluido", total_empresas=len(empresas))

    except Exception as e:
        session.rollback()
        logger.error("sync_erro_geral", erro=str(e))
        raise self.retry(exc=e, countdown=60)
    finally:
        session.close()


@celery.task(name="app.workers.tasks.sync_saldos.sync_empresa_task")
def sync_empresa_task(empresa_id: str):
    """Sync manual de uma empresa específica."""
    session = _get_db_session()
    try:
        from app.db.models.empresa import Empresa
        from uuid import UUID
        empresa = session.query(Empresa).filter(Empresa.id == UUID(empresa_id)).first()
        if empresa:
            _sync_empresa(session, empresa)
            session.commit()
            logger.info("sync_manual_concluido", empresa=empresa.nome)
    except Exception as e:
        session.rollback()
        logger.error("sync_manual_erro", empresa_id=empresa_id, erro=str(e))
    finally:
        session.close()


def _sync_empresa(session, empresa):
    """Lógica de sync de uma empresa individual."""
    from app.db.models.saldo import Saldo

    hoje = date.today()
    agora = datetime.now(timezone.utc)

    # Placeholder: em produção, chamar API bancária real
    # Por enquanto, cria registro com saldo zero para demonstrar o fluxo
    saldo = Saldo(
        empresa_id=empresa.id,
        saldo_banco=Decimal("0.00"),
        saldo_omie=Decimal("0.00"),
        delta=Decimal("0.00"),
        tem_divergencia=False,
        tipo_divergencia="sem_divergencia",
        data_referencia=hoje,
        synced_at=agora,
    )
    session.add(saldo)
    logger.info("sync_empresa_ok", empresa=empresa.nome)
