# backend/app/api/v1/routes/empresas.py
# Rotas de empresas do Portal TRK.

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import DbSession, get_current_user, require_role
from app.core.security import criptografar_campo
from app.db.models.empresa import Empresa
from app.db.models.saldo import Saldo
from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaCredenciais,
    EmpresaDetalhe,
    EmpresaResponse,
    SaldoResumo,
    EmpresaUpdate,
)

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_model=list[EmpresaResponse])
async def listar_empresas(
    db: DbSession,
    current_user=Depends(get_current_user),
    grupo: str | None = Query(None),
    banco: str | None = Query(None),
    responsavel_id: UUID | None = Query(None),
):
    """Lista empresas com saldo atual. Filtros opcionais por grupo, banco, responsável."""
    query = select(Empresa).where(Empresa.is_active == True).order_by(Empresa.nome)

    if grupo:
        query = query.where(Empresa.grupo == grupo)
    if banco:
        query = query.where(Empresa.banco == banco)
    if responsavel_id:
        query = query.where(Empresa.responsavel_user_id == responsavel_id)

    result = await db.execute(query)
    empresas = result.scalars().all()

    # Buscar último saldo de cada empresa
    respostas = []
    for emp in empresas:
        saldo_result = await db.execute(
            select(Saldo)
            .where(Saldo.empresa_id == emp.id)
            .order_by(Saldo.synced_at.desc())
            .limit(1)
        )
        saldo = saldo_result.scalar_one_or_none()

        respostas.append(EmpresaResponse(
            id=emp.id, nome=emp.nome, cnpj=emp.cnpj,
            banco=emp.banco, agencia=emp.agencia, conta=emp.conta,
            grupo=emp.grupo, responsavel=emp.responsavel,
            is_active=emp.is_active, created_at=emp.created_at,
            saldo_atual=SaldoResumo.model_validate(saldo) if saldo else None,
        ))

    return respostas


@router.get("/{empresa_id}", response_model=EmpresaDetalhe)
async def obter_empresa(
    empresa_id: UUID,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Obtém detalhes de uma empresa específica."""
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    saldo_result = await db.execute(
        select(Saldo).where(Saldo.empresa_id == emp.id).order_by(Saldo.synced_at.desc()).limit(1)
    )
    saldo = saldo_result.scalar_one_or_none()

    return EmpresaDetalhe(
        id=emp.id, nome=emp.nome, cnpj=emp.cnpj,
        banco=emp.banco, agencia=emp.agencia, conta=emp.conta,
        grupo=emp.grupo, responsavel=emp.responsavel,
        is_active=emp.is_active, created_at=emp.created_at,
        saldo_atual=SaldoResumo.model_validate(saldo) if saldo else None,
        tem_omie_config=bool(emp.omie_app_key_enc),
        tem_bank_config=bool(emp.bank_client_id_enc),
    )


@router.post("/", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def criar_empresa(
    dados: EmpresaCreate,
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Cria nova empresa (admin apenas)."""
    empresa = Empresa(
        nome=dados.nome, cnpj=dados.cnpj, banco=dados.banco,
        agencia=dados.agencia, conta=dados.conta, grupo=dados.grupo,
        responsavel_user_id=dados.responsavel_user_id,
    )
    db.add(empresa)
    await db.flush()
    logger.info("empresa_criada", empresa_id=str(empresa.id))
    return EmpresaResponse(
        id=empresa.id, nome=empresa.nome, cnpj=empresa.cnpj,
        banco=empresa.banco, agencia=empresa.agencia, conta=empresa.conta,
        grupo=empresa.grupo, responsavel=empresa.responsavel,
        is_active=True, created_at=empresa.created_at,
    )


@router.put("/{empresa_id}/credenciais")
async def atualizar_credenciais(
    empresa_id: UUID,
    dados: EmpresaCredenciais,
    db: DbSession,
    current_user=Depends(require_role(["admin"])),
):
    """Atualiza credenciais de integração (criptografadas). Admin apenas."""
    result = await db.execute(select(Empresa).where(Empresa.id == empresa_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if dados.omie_app_key:
        emp.omie_app_key_enc = criptografar_campo(dados.omie_app_key)
    if dados.omie_app_secret:
        emp.omie_app_secret_enc = criptografar_campo(dados.omie_app_secret)
    if dados.bank_client_id:
        emp.bank_client_id_enc = criptografar_campo(dados.bank_client_id)
    if dados.bank_client_secret:
        emp.bank_client_secret_enc = criptografar_campo(dados.bank_client_secret)

    logger.info("credenciais_atualizadas", empresa_id=str(empresa_id))
    return {"message": "Credenciais atualizadas com sucesso"}
