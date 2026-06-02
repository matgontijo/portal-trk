# backend/app/services/whatsapp.py
# Client da WhatsApp Business Cloud API (Meta).
# Envia mensagens de texto via template ou mensagem livre.

import structlog
import httpx

from app.core.config import get_settings

logger = structlog.get_logger()

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"


class WhatsAppClient:
    """Client para envio de mensagens via WhatsApp Business Cloud API."""

    def __init__(self):
        settings = get_settings()
        self.token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    async def enviar_mensagem(self, telefone: str, texto: str) -> bool:
        """Envia mensagem de texto para um número."""
        if not self.token or not self.phone_number_id:
            logger.warning("whatsapp_nao_configurado")
            return False

        url = f"{WHATSAPP_API_URL}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": telefone,
            "type": "text",
            "text": {"body": texto},
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                logger.info("whatsapp_enviado", telefone=telefone[:6] + "***")
                return True
        except httpx.HTTPError as e:
            logger.error("whatsapp_erro", telefone=telefone[:6] + "***", erro=str(e))
            return False

    async def enviar_resumo_diario(self, telefone: str, dados: dict) -> bool:
        """Envia resumo diário formatado."""
        texto = (
            f"📊 *Portal TRK — Resumo do Dia*\n\n"
            f"💰 Total em caixa: R$ {dados.get('total_caixa', '0,00')}\n"
            f"⚠️ Divergências: {dados.get('divergencias', 0)}\n"
            f"📋 Rotinas pendentes: {dados.get('rotinas_pendentes', 0)}\n"
            f"💳 A pagar hoje: R$ {dados.get('a_pagar_hoje', '0,00')}\n"
        )
        return await self.enviar_mensagem(telefone, texto)
