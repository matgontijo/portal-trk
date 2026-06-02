# backend/app/core/middleware.py
# Middleware FastAPI do Portal TRK.
# Responsabilidades:
#   - Headers de segurança (HSTS, CSP, X-Frame-Options, etc.)
#   - Logging estruturado de requisições (structlog)
#   - Rate limiting para endpoints sensíveis (/auth/login)

import time
from collections import defaultdict
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

logger = structlog.get_logger()


# ════════════════════════════════════════════════════════════════
# HEADERS DE SEGURANÇA
# ════════════════════════════════════════════════════════════════


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adiciona headers de segurança a todas as respostas.
    Segue as melhores práticas OWASP.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self'; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )

        return response


# ════════════════════════════════════════════════════════════════
# LOGGING DE REQUISIÇÕES
# ════════════════════════════════════════════════════════════════


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Loga cada requisição com duração, status e informações do cliente.
    Nunca loga dados sensíveis (body, tokens, senhas).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        inicio = time.time()
        request_id = request.headers.get("X-Request-ID", "")

        try:
            response = await call_next(request)
            duracao_ms = (time.time() - inicio) * 1000

            logger.info(
                "requisicao_http",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duracao_ms=round(duracao_ms, 2),
                ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("User-Agent", "")[:100],
                request_id=request_id,
            )

            return response

        except Exception as exc:
            duracao_ms = (time.time() - inicio) * 1000
            logger.error(
                "erro_requisicao",
                method=request.method,
                path=request.url.path,
                duracao_ms=round(duracao_ms, 2),
                erro=str(exc)[:200],  # Trunca para evitar log excessivo
                ip=request.client.host if request.client else "unknown",
            )
            raise


# ════════════════════════════════════════════════════════════════
# RATE LIMITING (em memória — para produção usar Redis)
# ════════════════════════════════════════════════════════════════

# Armazena tentativas por IP: {ip: [(timestamp, ...)] }
_rate_limit_store: dict[str, list[float]] = defaultdict(list)

# Configuração: 5 tentativas por minuto para /auth/login
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting para endpoints sensíveis.
    Aplica-se apenas ao POST /api/v1/auth/login.
    Limita a 5 tentativas por minuto por IP.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Aplicar apenas ao login
        if request.method == "POST" and "/auth/login" in request.url.path:
            ip = request.client.host if request.client else "0.0.0.0"
            agora = time.time()

            # Limpar tentativas antigas
            _rate_limit_store[ip] = [
                t for t in _rate_limit_store[ip]
                if agora - t < RATE_LIMIT_WINDOW_SECONDS
            ]

            if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
                logger.warning(
                    "rate_limit_excedido",
                    ip=ip,
                    path=request.url.path,
                    tentativas=len(_rate_limit_store[ip]),
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Muitas tentativas de login. Aguarde 1 minuto."
                    },
                )

            _rate_limit_store[ip].append(agora)

        return await call_next(request)


# ════════════════════════════════════════════════════════════════
# CONFIGURAR TODOS OS MIDDLEWARES
# ════════════════════════════════════════════════════════════════


def configurar_middlewares(app: FastAPI) -> None:
    """Registra todos os middlewares na aplicação FastAPI na ordem correta."""
    settings = get_settings()

    # CORS — deve ser o primeiro middleware
    origens_permitidas = (
        [settings.FRONTEND_URL]
        if settings.is_production
        else ["http://localhost:5173", "http://localhost:3000"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens_permitidas,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Ordem: rate limit → logging → security headers
    # (executam na ordem inversa — o último adicionado executa primeiro)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
