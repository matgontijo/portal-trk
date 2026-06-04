# backend/app/services/providers/__init__.py
# Camada de integração normalizada (bancos + Omie) do Portal TRK.

from .base import BankProvider, LancamentoExtrato, OmieProvider, SaldoBancario
from .factory import get_bank_provider, get_omie_provider

__all__ = [
    "BankProvider",
    "OmieProvider",
    "SaldoBancario",
    "LancamentoExtrato",
    "get_bank_provider",
    "get_omie_provider",
]
