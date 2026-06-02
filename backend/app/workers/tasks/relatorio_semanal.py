# backend/app/workers/tasks/relatorio_semanal.py
# Task Celery para geração do relatório semanal PDF.
# Executa toda sexta 18:00 BRT.

import os
from datetime import date, timedelta

import structlog

from app.core.config import get_settings
from app.workers.celery_app import celery

logger = structlog.get_logger()


@celery.task(name="app.workers.tasks.relatorio_semanal.gerar_relatorio")
def gerar_relatorio():
    """Gera relatório semanal PDF com WeasyPrint."""
    settings = get_settings()
    hoje = date.today()
    nome_arquivo = f"{hoje.isoformat()}.pdf"
    reports_dir = os.path.join(settings.RENDER_DISK_PATH, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    caminho = os.path.join(reports_dir, nome_arquivo)

    try:
        from app.services.relatorio import gerar_relatorio_pdf
        gerar_relatorio_pdf(caminho, hoje - timedelta(days=7), hoje)
        logger.info("relatorio_gerado", caminho=caminho)

        # TODO: Enviar via WhatsApp e notificar in-app
        return {"caminho": caminho, "sucesso": True}

    except Exception as e:
        logger.error("relatorio_erro", erro=str(e))
        return {"sucesso": False, "erro": str(e)}
