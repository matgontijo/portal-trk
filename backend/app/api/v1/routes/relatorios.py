# backend/app/api/v1/routes/relatorios.py
# Rotas de relatórios do Portal TRK.

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.core.config import get_settings
from app.core.dependencies import DbSession, require_role

router = APIRouter()


@router.get("/")
async def listar_relatorios(
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Lista relatórios disponíveis para download."""
    settings = get_settings()
    reports_dir = os.path.join(settings.RENDER_DISK_PATH, "reports")

    if not os.path.exists(reports_dir):
        return []

    relatorios = []
    for f in sorted(os.listdir(reports_dir), reverse=True):
        if f.endswith(".pdf"):
            path = os.path.join(reports_dir, f)
            relatorios.append({
                "nome": f,
                "tamanho_bytes": os.path.getsize(path),
                "data": f.replace(".pdf", ""),
            })

    return relatorios


@router.get("/download/{nome}")
async def download_relatorio(
    nome: str,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Download de um relatório PDF."""
    settings = get_settings()
    path = os.path.join(settings.RENDER_DISK_PATH, "reports", nome)

    if not os.path.exists(path) or not nome.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="Relatório não encontrado")

    return FileResponse(path, media_type="application/pdf", filename=nome)
