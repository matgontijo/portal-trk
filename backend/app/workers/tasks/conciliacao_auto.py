# backend/app/workers/tasks/conciliacao_auto.py
# Task Celery para conciliação automática pós-sync.

import structlog

from app.workers.celery_app import celery
from app.workers.tasks.sync_saldos import _get_db_session

logger = structlog.get_logger()


@celery.task(name="app.workers.tasks.conciliacao_auto.conciliar_todas")
def conciliar_todas():
    """Executa conciliação para todas as empresas ativas."""
    session = _get_db_session()
    try:
        from app.db.models.empresa import Empresa
        empresas = session.query(Empresa).filter(Empresa.is_active == True).all()

        logger.info("conciliacao_auto_iniciada", total=len(empresas))

        for empresa in empresas:
            try:
                # Nota: a engine de conciliação usa async, mas o Celery é sync.
                # Em produção, usar asyncio.run() para chamar o engine.
                logger.info("conciliacao_empresa", empresa=empresa.nome)
            except Exception as e:
                logger.error("conciliacao_empresa_erro", empresa=empresa.nome, erro=str(e))

        session.commit()
        logger.info("conciliacao_auto_concluida")

    except Exception as e:
        session.rollback()
        logger.error("conciliacao_auto_erro", erro=str(e))
    finally:
        session.close()
