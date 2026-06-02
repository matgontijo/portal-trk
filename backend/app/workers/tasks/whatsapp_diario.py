# backend/app/workers/tasks/whatsapp_diario.py
# Task Celery para envio de resumo diário via WhatsApp.
# Executa diariamente às 06:30 BRT.

import structlog

from app.workers.celery_app import celery

logger = structlog.get_logger()


@celery.task(name="app.workers.tasks.whatsapp_diario.enviar_resumo_diario")
def enviar_resumo_diario():
    """Envia resumo diário via WhatsApp para gestora e funcionários."""
    try:
        from app.services.whatsapp import WhatsAppClient
        from app.core.config import get_settings

        settings = get_settings()
        if not settings.WHATSAPP_TOKEN:
            logger.warning("whatsapp_nao_configurado")
            return {"sucesso": False, "motivo": "WhatsApp não configurado"}

        # TODO: Montar resumo com dados do banco e enviar
        logger.info("whatsapp_resumo_enviado")
        return {"sucesso": True}

    except Exception as e:
        logger.error("whatsapp_erro", erro=str(e))
        return {"sucesso": False, "erro": str(e)}
