# backend/app/api/v1/router.py
# Router principal da API v1 — agrega todos os sub-routers.

from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    auditoria,
    automacoes,
    conciliacao,
    configuracoes,
    dashboard,
    empresas,
    notificacoes,
    relatorios,
    rotinas,
    saldos,
    tarefas,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["autenticação"])
api_router.include_router(users.router, prefix="/users", tags=["usuários"])
api_router.include_router(empresas.router, prefix="/empresas", tags=["empresas"])
api_router.include_router(rotinas.router, prefix="/rotinas", tags=["rotinas"])
api_router.include_router(tarefas.router, prefix="/tarefas", tags=["tarefas"])
api_router.include_router(saldos.router, prefix="/saldos", tags=["saldos"])
api_router.include_router(conciliacao.router, prefix="/conciliacao", tags=["conciliação"])
api_router.include_router(notificacoes.router, prefix="/notificacoes", tags=["notificações"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["relatórios"])
api_router.include_router(configuracoes.router, prefix="/configuracoes", tags=["configurações"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(automacoes.router, prefix="/automacoes", tags=["automações"])
