# backend/app/db/session.py
# Fábrica de sessões async do SQLAlchemy para o Portal TRK.
# Usa asyncpg como driver para PostgreSQL.
# A sessão é gerenciada pela dependency get_db() em dependencies.py.

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


def _criar_engine():
    """Cria o engine async. NullPool em produção para compatibilidade com pgbouncer."""
    settings = get_settings()

    kwargs = {
        "echo": not settings.is_production,  # SQL logging apenas em dev
        "future": True,
    }

    # Em produção, NullPool é recomendado com pgbouncer/connection poolers
    if settings.is_production:
        kwargs["poolclass"] = NullPool
    else:
        kwargs["pool_size"] = 5
        kwargs["max_overflow"] = 10
        kwargs["pool_pre_ping"] = True

    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine = _criar_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
