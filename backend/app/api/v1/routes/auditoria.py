# backend/app/api/v1/routes/auditoria.py
# Rotas de auditoria do Portal TRK (admin apenas).

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.core.dependencies import DbSession, require_role
from app.db.models.audit_log import AuditLog
from app.schemas.auditoria import AuditLogResponse

router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
async def listar_audit_logs(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
    user_id: UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=100),
):
    """Lista logs de auditoria com filtros."""
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        AuditLogResponse(
            id=log.id,
            user_name=log.user.name if log.user else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=str(log.ip_address) if log.ip_address else None,
            timestamp=log.timestamp,
            before_json=log.before_json,
            after_json=log.after_json,
        )
        for log in logs
    ]


@router.get("/export")
async def exportar_csv(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Exporta logs de auditoria em CSV."""
    result = await db.execute(
        select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10000)
    )
    logs = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "usuario", "acao", "recurso_tipo", "recurso_id", "ip"])

    for log in logs:
        writer.writerow([
            log.timestamp.isoformat(),
            log.user.name if log.user else "",
            log.action,
            log.resource_type or "",
            str(log.resource_id) if log.resource_id else "",
            str(log.ip_address) if log.ip_address else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=auditoria.csv"},
    )
