# backend/app/main.py
# Ponto de entrada da API do Portal TRK.
# Responsabilidades:
#   - Criar a aplicação FastAPI com lifespan (startup/shutdown)
#   - Registrar middlewares (segurança, logging, rate limiting, CORS)
#   - Incluir routers da API v1
#   - Health check endpoint
#   - Swagger/ReDoc apenas em desenvolvimento

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.dependencies import fechar_redis
from app.core.middleware import configurar_middlewares

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação."""
    settings = get_settings()
    logger.info("portal_trk_iniciando", environment=settings.ENVIRONMENT)
    yield
    # Shutdown: fechar conexões
    await fechar_redis()
    logger.info("portal_trk_finalizado")


def criar_app() -> FastAPI:
    """Factory da aplicação FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title="Portal TRK API",
        description="Sistema operacional interno do Grupo TRK — conciliação bancária, rotinas e gestão financeira",
        version="1.0.0",
        lifespan=lifespan,
        # Swagger apenas em desenvolvimento
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
    )

    # Registrar middlewares
    configurar_middlewares(app)

    # Registrar routers
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")

    # Health check
    @app.get("/health", tags=["sistema"])
    async def health_check():
        """Endpoint de saúde para o Render e monitoramento."""
        return {"status": "ok", "service": "portal-trk-api"}

    # Handler global de exceções não tratadas
    @app.exception_handler(Exception)
    async def handler_erro_global(request, exc):
        """Captura erros não tratados — nunca expõe stack trace ao cliente."""
        logger.error(
            "erro_nao_tratado",
            path=request.url.path,
            method=request.method,
            erro=str(exc)[:200],
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )

    return app


# Instância global — usada pelo gunicorn
app = criar_app()
