# backend/tests/conftest.py
# Configuração global dos testes. Força o modo "fake" dos providers
# ANTES de qualquer import que chame get_settings() (que é lru_cached).

import os
from types import SimpleNamespace
from uuid import uuid4

os.environ.setdefault("BANK_PROVIDER_MODE", "fake")
os.environ.setdefault("BANK_DIVERGENCIA_TOLERANCIA", "0.05")
os.environ.setdefault("ENCRYPTION_KEY", "00" * 32)

import pytest


@pytest.fixture
def empresa_fake():
    """Empresa mínima — sem credenciais => providers caem no modo fake."""
    return SimpleNamespace(
        id=uuid4(),
        nome="Empresa Teste LTDA",
        cnpj="12345678000199",
        banco="inter",
        conta="12345-6",
        responsavel_user_id=uuid4(),
        omie_app_key_enc=None,
        omie_app_secret_enc=None,
        bank_client_id_enc=None,
        bank_client_secret_enc=None,
        bank_certificate_path=None,
    )
