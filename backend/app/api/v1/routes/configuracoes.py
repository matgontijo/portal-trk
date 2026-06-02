# backend/app/api/v1/routes/configuracoes.py
# Rotas de configurações do Portal TRK (admin apenas).

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.core.dependencies import DbSession, require_role
from app.db.models.ml_model import MLModelVersion
from app.db.models.sync_config import SyncConfig
from app.schemas.configuracao import MLConfigResponse, SyncConfigResponse, SyncConfigUpdate

router = APIRouter()


@router.get("/sync", response_model=SyncConfigResponse)
async def obter_sync_config(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Obtém configuração de horários de sync."""
    result = await db.execute(select(SyncConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return SyncConfigResponse.model_validate(config)


@router.put("/sync", response_model=SyncConfigResponse)
async def atualizar_sync_config(
    dados: SyncConfigUpdate,
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Atualiza horários de sync. Celery Beat relê automaticamente."""
    result = await db.execute(select(SyncConfig).limit(1))
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(config, campo, valor)

    config.updated_by = current_user.id
    from datetime import datetime, timezone
    config.updated_at = datetime.now(timezone.utc)

    return SyncConfigResponse.model_validate(config)


@router.get("/ml", response_model=MLConfigResponse)
async def obter_ml_config(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Obtém informações do modelo ML ativo."""
    result = await db.execute(
        select(MLModelVersion).where(MLModelVersion.is_active == True).limit(1)
    )
    modelo = result.scalar_one_or_none()
    if not modelo:
        return MLConfigResponse()
    return MLConfigResponse.model_validate(modelo)


@router.post("/ml/re-treinar")
async def re_treinar_modelo(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Aciona re-treinamento do modelo ML."""
    from app.workers.tasks.treinar_modelo import treinar_modelo_task
    treinar_modelo_task.delay(str(current_user.id))
    return {"message": "Re-treinamento iniciado — o modelo será atualizado em breve"}


@router.get("/ml/versoes", response_model=list[MLConfigResponse])
async def listar_versoes_ml(
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Lista todas as versões do modelo ML."""
    result = await db.execute(
        select(MLModelVersion).order_by(MLModelVersion.treinado_em.desc())
    )
    return [MLConfigResponse.model_validate(m) for m in result.scalars().all()]


@router.post("/ml/rollback/{version_id}")
async def rollback_modelo(
    version_id: str,
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Ativa uma versão anterior do modelo ML (rollback)."""
    from uuid import UUID

    # Desativar modelo atual
    result = await db.execute(
        select(MLModelVersion).where(MLModelVersion.is_active == True)
    )
    ativo = result.scalar_one_or_none()
    if ativo:
        ativo.is_active = False

    # Ativar versão selecionada
    result = await db.execute(
        select(MLModelVersion).where(MLModelVersion.id == UUID(version_id))
    )
    versao = result.scalar_one_or_none()
    if not versao:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    versao.is_active = True

    return {"message": f"Modelo rollback para versão {version_id}"}
