# backend/app/services/banco_bradesco.py
# Client Open Finance Brasil para Bradesco.
# Usa certificado mTLS para autenticação.
# Endpoints: saldo e transações (leitura apenas).

import structlog
import httpx

from app.core.config import get_settings

logger = structlog.get_logger()


class BancoBradescoClient:
    """Client Open Finance para Bradesco."""

    def __init__(self, account_id: str, cert_path: str | None = None):
        settings = get_settings()
        self.base_url = settings.BRADESCO_BASE_URL
        self.account_id = account_id
        self.cert_path = cert_path or settings.BRADESCO_CERT_PATH

    async def obter_saldo(self) -> dict:
        """Busca saldo da conta via Open Finance."""
        url = f"{self.base_url}/accounts/{self.account_id}/balances"

        try:
            async with httpx.AsyncClient(
                timeout=15,
                cert=self.cert_path if self.cert_path else None,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("bradesco_saldo_erro", account=self.account_id, erro=str(e))
            raise

    async def obter_transacoes(self, data_inicio: str, data_fim: str) -> dict:
        """
        Busca transações no período via Open Finance.
        Formato de data: YYYY-MM-DD
        """
        url = f"{self.base_url}/accounts/{self.account_id}/transactions"

        try:
            async with httpx.AsyncClient(
                timeout=30,
                cert=self.cert_path if self.cert_path else None,
            ) as client:
                response = await client.get(
                    url,
                    params={"fromBookingDateTime": data_inicio, "toBookingDateTime": data_fim},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("bradesco_transacoes_erro", account=self.account_id, erro=str(e))
            raise
