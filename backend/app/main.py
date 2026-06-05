# trk-universe/backend/app/main.py
# TRK OS — Sistema Operacional do Grupo TRK.
# App novo, zero-dependência de infra para rodar (SQLite). Permissões por setor.

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import config
from .db import Base, SessionLocal, engine
from .routers import (
    auth, automacoes, departamentos, empresas, meta, pipes, rotinas, saldos, skills, tarefas, usuarios,
)
from .seed import seed


def criar_app() -> FastAPI:
    app = FastAPI(title="TRK OS", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if config.FRONTEND_URL == "*" else [config.FRONTEND_URL],
        allow_credentials=False,  # auth via header Bearer (não cookies) => '*' é válido
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup():
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed(db)

    @app.get("/health")
    def health():
        return {"status": "ok", "app": "TRK OS"}

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(meta.router, prefix="/api/meta", tags=["meta"])
    app.include_router(usuarios.router, prefix="/api/usuarios", tags=["usuarios"])
    app.include_router(departamentos.router, prefix="/api/departamentos", tags=["departamentos"])
    app.include_router(saldos.router, prefix="/api/saldos", tags=["saldos"])
    app.include_router(tarefas.router, prefix="/api/tarefas", tags=["tarefas"])
    app.include_router(rotinas.router, prefix="/api/rotinas", tags=["rotinas"])
    app.include_router(pipes.router, prefix="/api/pipes", tags=["pipes"])
    app.include_router(automacoes.router, prefix="/api/automacoes", tags=["automacoes"])
    app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
    app.include_router(empresas.router, prefix="/api/empresas", tags=["empresas"])

    # ─── Serve o frontend (SPA) na mesma origem, se o build existir ───
    static_dir = os.getenv("STATIC_DIR", "static")
    if os.path.isdir(static_dir):
        assets = os.path.join(static_dir, "assets")
        if os.path.isdir(assets):
            app.mount("/assets", StaticFiles(directory=assets), name="assets")

        @app.get("/{full_path:path}")
        def spa(full_path: str):
            # Arquivos reais (favicon, etc.); senão devolve o index.html (rotas do React)
            candidato = os.path.join(static_dir, full_path)
            if full_path and os.path.isfile(candidato):
                return FileResponse(candidato)
            return FileResponse(os.path.join(static_dir, "index.html"))

    return app


app = criar_app()
