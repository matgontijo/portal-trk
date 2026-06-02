# backend/app/core/config.py
# Configurações centralizadas do Portal TRK via pydantic-settings.
# Todas as variáveis de ambiente são tipadas, validadas e documentadas.
# Nunca use valores hardcoded para configurações sensíveis.

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Ambiente ───
    ENVIRONMENT: Literal["development", "production"] = "development"

    # ─── Banco de Dados ───
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/portal_trk"

    # ─── Redis ───
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── JWT (HS256) ───
    JWT_SECRET_KEY: str = "trk-portal-dev-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Criptografia (AES-256-GCM) ───
    ENCRYPTION_KEY: str = ""

    # ─── CORS ───
    FRONTEND_URL: str = "http://localhost:5173"

    # ─── Omie ERP ───
    OMIE_BASE_URL: str = "https://app.omie.com.br/api/v1"

    # ─── Bancos ───
    INTER_BASE_URL: str = "https://cdpj.partners.bancointer.com.br"
    SANTANDER_BASE_URL: str = "https://trust-open.api.santander.com.br"
    SANTANDER_CERT_PATH: str = ""
    BRADESCO_BASE_URL: str = "https://proxy.api.prebanco.com.br"
    BRADESCO_CERT_PATH: str = ""

    # ─── WhatsApp Business ───
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""

    # ─── VAPID (Web Push) ───
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIMS_SUB: str = "mailto:admin@trk.com.br"

    # ─── E-mail (SMTP) ───
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    EMAIL_FROM: str = "noreply@trk.com.br"

    # ─── Google Drive ───
    GOOGLE_DRIVE_CREDENTIALS_PATH: str = ""

    # ─── Armazenamento ───
    RENDER_DISK_PATH: str = "./data"

    @field_validator("DATABASE_URL")
    @classmethod
    def validar_database_url(cls, v: str) -> str:
        """Garante que a URL do banco usa o driver asyncpg."""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def encryption_key_bytes(self) -> bytes:
        """Converte a chave hex de 64 caracteres para 32 bytes."""
        if not self.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY não configurada")
        return bytes.fromhex(self.ENCRYPTION_KEY)

    @property
    def database_url_sync(self) -> str:
        """URL síncrona para Alembic (usa psycopg2 em vez de asyncpg)."""
        return self.DATABASE_URL.replace("+asyncpg", "")


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
