# trk-universe/backend/app/config.py
# Configuração do TRK OS. Tudo via env, com defaults sãos para rodar localmente.

import os


class Config:
    # Banco: SQLite por padrão (zero-config). Em produção use DATABASE_URL (Postgres).
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./trk_os.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "trk-os-dev-secret-troque-em-producao")
    TOKEN_EXP_SECONDS: int = int(os.getenv("TOKEN_EXP_SECONDS", str(60 * 60 * 24 * 7)))  # 7 dias
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "*")
    # Provedor de saldo: "fake" (demo) | "real"
    BANK_PROVIDER_MODE: str = os.getenv("BANK_PROVIDER_MODE", "fake")


config = Config()
