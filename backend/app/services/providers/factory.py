# backend/app/services/providers/factory.py
# Fábrica que decide qual provider usar para cada empresa.
#
# Regra:
#   - BANK_PROVIDER_MODE == "fake"  -> sempre simulado (demo/dev/testes)
#   - BANK_PROVIDER_MODE == "real"  -> sempre real (exige credenciais)
#   - BANK_PROVIDER_MODE == "auto"  -> real se a empresa tiver credenciais,
#                                       senão cai no fake (não bloqueia o app)
#
# Trocar do mock para o real é apenas mudar a env var — zero alteração de código.

from __future__ import annotations

from decimal import Decimal

import structlog

from app.core.config import get_settings

from .base import BankProvider, OmieProvider
from .fake import FakeBankProvider, FakeOmieProvider

logger = structlog.get_logger()


def _tem_credenciais_banco(empresa) -> bool:
    banco = getattr(empresa, "banco", None)
    if banco == "inter":
        return bool(getattr(empresa, "bank_client_id_enc", None) and getattr(empresa, "bank_client_secret_enc", None))
    # Santander / Bradesco usam Open Finance via certificado + conta
    return bool(getattr(empresa, "conta", None) and getattr(empresa, "bank_certificate_path", None))


def _tem_credenciais_omie(empresa) -> bool:
    return bool(getattr(empresa, "omie_app_key_enc", None) and getattr(empresa, "omie_app_secret_enc", None))


def get_bank_provider(empresa) -> BankProvider:
    """Retorna o provider bancário apropriado para a empresa."""
    settings = get_settings()
    modo = getattr(settings, "BANK_PROVIDER_MODE", "auto")
    cnpj = getattr(empresa, "cnpj", "") or ""
    banco = getattr(empresa, "banco", "fake") or "fake"

    usar_real = modo == "real" or (modo == "auto" and _tem_credenciais_banco(empresa))
    if not usar_real:
        return FakeBankProvider(cnpj=cnpj, nome_banco=banco)

    from .real import InterAdapter, OpenFinanceAdapter

    if banco == "inter":
        from app.services.banco_inter import BancoInterClient
        return InterAdapter(BancoInterClient.from_empresa(empresa))
    if banco == "santander":
        from app.services.banco_santander import BancoSantanderClient
        return OpenFinanceAdapter(BancoSantanderClient(empresa.conta, empresa.bank_certificate_path), "santander")
    if banco == "bradesco":
        from app.services.banco_bradesco import BancoBradescoClient
        return OpenFinanceAdapter(BancoBradescoClient(empresa.conta, empresa.bank_certificate_path), "bradesco")

    logger.warning("banco_desconhecido_usando_fake", banco=banco)
    return FakeBankProvider(cnpj=cnpj, nome_banco=banco)


def get_omie_provider(empresa, saldo_banco_ref: Decimal) -> OmieProvider:
    """Retorna o provider de posição esperada (Omie) apropriado."""
    settings = get_settings()
    modo = getattr(settings, "BANK_PROVIDER_MODE", "auto")
    cnpj = getattr(empresa, "cnpj", "") or ""

    usar_real = modo == "real" or (modo == "auto" and _tem_credenciais_omie(empresa))
    if not usar_real:
        return FakeOmieProvider(cnpj=cnpj, saldo_banco_ref=saldo_banco_ref)

    from app.services.omie import OmieClient
    from .real import OmieRealProvider

    return OmieRealProvider(OmieClient.from_empresa(empresa))
