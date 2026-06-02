# Dockerfile — Backend FastAPI do Portal TRK
# Multi-stage build para imagem otimizada de produção
# Serve a API via gunicorn com workers uvicorn

FROM python:3.11-slim AS base

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências do sistema para WeasyPrint e PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Stage de dependências ───
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─── Stage de produção ───
FROM dependencies AS production

# Copia o código da aplicação
COPY . .

# Cria diretórios para dados persistentes
RUN mkdir -p /data/reports /data/models /data/uploads /data/certs

# Expõe a porta padrão
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Inicia com gunicorn + uvicorn workers
# Workers = 2 * CPU + 1 (ajustar no Render conforme o plano)
CMD ["gunicorn", "app.main:app", \
     "--bind", "0.0.0.0:8000", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
