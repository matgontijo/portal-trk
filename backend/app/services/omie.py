# backend/app/services/omie.py
# Client da API Omie ERP.
# Responsabilidades:
#   - ListarContasPagar: busca contas a pagar por empresa
#   - ListarContasReceber: busca contas a receber por empresa
#   - Conciliação bancária no Omie
# Todas as chamadas são autenticadas com app_key e app_secret por empresa.

import structlog
import httpx

from app.core.config import get_settings
from app.core.security import descriptografar_campo

logger = structlog.get_logger()


class OmieClient:
    """Client para a API Omie ERP."""

    def __init__(self, app_key: str, app_secret: str):
        self.base_url = get_settings().OMIE_BASE_URL
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def from_empresa(cls, empresa) -> "OmieClient":
        """Cria client a partir de uma empresa (descriptografa credenciais)."""
        if not empresa.omie_app_key_enc or not empresa.omie_app_secret_enc:
            raise ValueError(f"Empresa {empresa.nome} não tem credenciais Omie configuradas")

        app_key = descriptografar_campo(empresa.omie_app_key_enc)
        app_secret = descriptografar_campo(empresa.omie_app_secret_enc)
        return cls(app_key, app_secret)

    async def _chamar_api(self, endpoint: str, call: str, params: dict) -> dict:
        """Chamada genérica à API Omie."""
        url = f"{self.base_url}/{endpoint}/"
        payload = {
            "call": call,
            "app_key": self.app_key,
            "app_secret": self.app_secret,
            "param": [params],
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("omie_api_erro", endpoint=endpoint, call=call, erro=str(e))
            raise

    async def listar_contas_pagar(
        self, pagina: int = 1, registros_por_pagina: int = 500
    ) -> dict:
        """Lista contas a pagar."""
        return await self._chamar_api(
            "financas/contapagar",
            "ListarContasPagar",
            {
                "nPagina": pagina,
                "nRegPorPagina": registros_por_pagina,
                "dDtVencInicial": "",
                "dDtVencFinal": "",
            },
        )

    async def listar_contas_receber(
        self, pagina: int = 1, registros_por_pagina: int = 500
    ) -> dict:
        """Lista contas a receber."""
        return await self._chamar_api(
            "financas/contareceber",
            "ListarContasReceber",
            {
                "nPagina": pagina,
                "nRegPorPagina": registros_por_pagina,
            },
        )

    async def conciliar_lancamento(self, id_lancamento: int, data_conciliacao: str) -> dict:
        """Concilia um lançamento no Omie."""
        return await self._chamar_api(
            "financas/contacorrentelancamentos",
            "ConciliarLancamento",
            {
                "nIdLancamento": id_lancamento,
                "dDtConciliacao": data_conciliacao,
            },
        )
