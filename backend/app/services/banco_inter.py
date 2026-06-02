# backend/app/services/banco_inter.py
# Client da API Inter Empresas v2.
# Autenticação: OAuth2 client_credentials
# Endpoints: saldo e extrato (leitura apenas)

import structlog
import httpx

from app.core.config import get_settings
from app.core.security import descriptografar_campo

logger = structlog.get_logger()


class BancoInterClient:
    """Client para a API do Banco Inter Empresas v2."""

    def __init__(self, client_id: str, client_secret: str):
        self.base_url = get_settings().INTER_BASE_URL
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None

    @classmethod
    def from_empresa(cls, empresa) -> "BancoInterClient":
        """Cria client a partir de uma empresa (descriptografa credenciais)."""
        if not empresa.bank_client_id_enc or not empresa.bank_client_secret_enc:
            raise ValueError(f"Empresa {empresa.nome} não tem credenciais Inter configuradas")

        client_id = descriptografar_campo(empresa.bank_client_id_enc)
        client_secret = descriptografar_campo(empresa.bank_client_secret_enc)
        return cls(client_id, client_secret)

    async def _autenticar(self) -> str:
        """Obtém access token via OAuth2 client_credentials."""
        if self._access_token:
            return self._access_token

        url = f"{self.base_url}/oauth/v2/token"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "extrato.read boleto-cobranca.read",
                    },
                )
                response.raise_for_status()
                data = response.json()
                self._access_token = data["access_token"]
                return self._access_token
        except httpx.HTTPError as e:
            logger.error("inter_auth_erro", erro=str(e))
            raise

    async def obter_saldo(self) -> dict:
        """Busca saldo atual da conta."""
        token = await self._autenticar()
        url = f"{self.base_url}/banking/v2/saldo"

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()

    async def obter_extrato(self, data_inicio: str, data_fim: str) -> dict:
        """
        Busca extrato bancário no período.
        Formato de data: YYYY-MM-DD
        """
        token = await self._autenticar()
        url = f"{self.base_url}/banking/v2/extrato"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params={"dataInicio": data_inicio, "dataFim": data_fim},
            )
            response.raise_for_status()
            return response.json()
