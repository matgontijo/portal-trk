# backend/app/api/v1/routes/rotinas.py
# Rotas de rotinas diárias do Portal TRK.
# Funcionário: vê rotinas do dia, atualiza progresso.
# Gestor+: CRUD completo de rotinas (builder).

from datetime import date, datetime, timezone
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from app.core.dependencies import DbSession, get_current_user, require_role
from app.db.models.rotina import Rotina, RotinaAtribuicao, RotinaBloco
from app.db.models.rotina_progresso import RotinaProgresso
from app.schemas.rotina import (
    BlocoResponse,
    ProgressoResponse,
    ProgressoUpdate,
    RotinaCreate,
    RotinaResponse,
    RotinaUpdate,
)

router = APIRouter()
logger = structlog.get_logger()


def _dia_semana_atual() -> int:
    """Retorna o dia da semana atual (1=seg, ..., 5=sex). Sábado/Domingo → None."""
    dia = date.today().isoweekday()  # 1=seg, 7=dom
    return dia if dia <= 5 else None


@router.get("/hoje", response_model=list[RotinaResponse])
async def rotinas_do_dia(
    db: DbSession,
    dia: int | None = Query(None, ge=1, le=5, description="Dia da semana (1=seg, 5=sex)"),
    current_user=Depends(get_current_user),
):
    """
    Retorna as rotinas do dia para o usuário autenticado.
    Se não informar dia, usa o dia atual.
    Inclui progresso de cada bloco para a data de hoje.
    """
    dia_semana = dia or _dia_semana_atual()
    if dia_semana is None:
        return []  # Fim de semana

    hoje = date.today()

    # Buscar rotinas atribuídas ao usuário para o dia
    query = (
        select(Rotina)
        .join(RotinaAtribuicao)
        .where(
            RotinaAtribuicao.user_id == current_user.id,
            Rotina.status == "ativa",
            Rotina.dias_semana.any(dia_semana),
        )
        .options(selectinload(Rotina.blocos), selectinload(Rotina.atribuicoes))
        .order_by(Rotina.nome)
    )
    result = await db.execute(query)
    rotinas = result.scalars().unique().all()

    # Buscar progresso do dia para todos os blocos do usuário
    bloco_ids = [b.id for r in rotinas for b in r.blocos]
    progresso_map = {}
    if bloco_ids:
        prog_result = await db.execute(
            select(RotinaProgresso).where(
                RotinaProgresso.user_id == current_user.id,
                RotinaProgresso.data_referencia == hoje,
                RotinaProgresso.bloco_id.in_(bloco_ids),
            )
        )
        for p in prog_result.scalars().all():
            progresso_map[p.bloco_id] = p

    # Montar resposta
    respostas = []
    for rotina in rotinas:
        blocos_resp = []
        concluidos = 0
        for bloco in rotina.blocos:
            prog = progresso_map.get(bloco.id)
            bloco_r = BlocoResponse(
                id=bloco.id,
                tipo=bloco.tipo,
                label=bloco.label,
                config=bloco.config or {},
                posicao=bloco.posicao,
                is_required=bloco.is_required,
                progresso=ProgressoResponse.model_validate(prog) if prog else None,
            )
            blocos_resp.append(bloco_r)
            if prog and prog.is_done:
                concluidos += 1

        respostas.append(RotinaResponse(
            id=rotina.id,
            nome=rotina.nome,
            descricao=rotina.descricao,
            dias_semana=rotina.dias_semana,
            alertas=rotina.alertas or [],
            categoria=rotina.categoria,
            status=rotina.status,
            blocos=blocos_resp,
            total_blocos=len(rotina.blocos),
            blocos_concluidos=concluidos,
            created_at=rotina.created_at,
        ))

    return respostas


@router.put("/progresso", status_code=status.HTTP_200_OK)
async def atualizar_progresso(
    dados: ProgressoUpdate,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """
    Atualiza o progresso de um bloco para o dia atual.
    Cria o registro se não existir (upsert).
    """
    hoje = date.today()

    # Verificar se o bloco existe e o usuário tem acesso
    result = await db.execute(
        select(RotinaProgresso).where(
            RotinaProgresso.bloco_id == dados.bloco_id,
            RotinaProgresso.user_id == current_user.id,
            RotinaProgresso.data_referencia == hoje,
        )
    )
    progresso = result.scalar_one_or_none()

    if progresso is None:
        # Buscar rotina_id do bloco
        bloco_result = await db.execute(
            select(RotinaBloco).where(RotinaBloco.id == dados.bloco_id)
        )
        bloco = bloco_result.scalar_one_or_none()
        if not bloco:
            raise HTTPException(status_code=404, detail="Bloco não encontrado")

        progresso = RotinaProgresso(
            rotina_id=bloco.rotina_id,
            bloco_id=dados.bloco_id,
            user_id=current_user.id,
            data_referencia=hoje,
        )
        db.add(progresso)

    # Atualizar campos fornecidos
    if dados.is_done is not None:
        progresso.is_done = dados.is_done
        progresso.done_at = datetime.now(timezone.utc) if dados.is_done else None
    if dados.valor_texto is not None:
        progresso.valor_texto = dados.valor_texto
    if dados.arquivo_url is not None:
        progresso.arquivo_url = dados.arquivo_url
        progresso.arquivo_nome = dados.arquivo_nome

    return {"message": "Progresso atualizado"}


# ═══ ROTAS GESTOR+ (CRUD de rotinas / builder) ═══

@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_rotinas_padrao(
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Cria rotinas padrão e atribui a todos os funcionários (Apenas Administradores)."""
    from app.db.models.user import User

    # Verificar se já existem rotinas
    result = await db.execute(select(Rotina))
    if result.scalars().first():
        return {"message": "Rotinas já existem no sistema. Nenhuma ação realizada."}

    # Buscar funcionários
    result = await db.execute(select(User).where(User.role == "funcionario", User.is_active == True))
    funcionarios = result.scalars().all()

    rotinas_padrao = [
        {
            "nome": "Conciliação Bancária Matinal",
            "descricao": "Fazer a checagem dos saldos e entradas nos bancos e importar para o Omie.",
            "dias_semana": [1, 2, 3, 4, 5],
            "categoria": "banco",
            "blocos": [
                {"tipo": "checkbox", "label": "Acessar Banco Santander e exportar OFX", "is_required": True},
                {"tipo": "checkbox", "label": "Acessar Banco Inter e exportar OFX", "is_required": True},
                {"tipo": "checkbox", "label": "Acessar Omie e importar os arquivos OFX", "is_required": True},
                {"tipo": "text_short", "label": "Saldo Final Consolidado (Santander + Inter)", "is_required": True},
            ]
        },
        {
            "nome": "Checagem de E-mails e Pipefy",
            "descricao": "Verificar a caixa de entrada geral e atualizar os cards de onboarding no Pipefy.",
            "dias_semana": [1, 2, 3, 4, 5],
            "categoria": "pipe",
            "blocos": [
                {"tipo": "checkbox", "label": "Responder todos os e-mails urgentes", "is_required": True},
                {"tipo": "checkbox", "label": "Mover cards concluídos no Pipefy", "is_required": True},
                {"tipo": "checkbox", "label": "Triagem de novos clientes no Funil", "is_required": False},
            ]
        },
        {
            "nome": "Relatório Semanal de Fechamento",
            "descricao": "Organizar os documentos da semana e salvar no Google Drive.",
            "dias_semana": [5],
            "categoria": "drive",
            "blocos": [
                {"tipo": "checkbox", "label": "Revisar notas fiscais emitidas", "is_required": True},
                {"tipo": "file_upload", "label": "Link da pasta do Drive com os PDFs", "is_required": True},
            ]
        }
    ]

    for rt_data in rotinas_padrao:
        rotina = Rotina(
            nome=rt_data["nome"],
            descricao=rt_data["descricao"],
            dias_semana=rt_data["dias_semana"],
            categoria=rt_data["categoria"],
            created_by=current_user.id
        )
        db.add(rotina)
        await db.flush()

        for i, bloco_data in enumerate(rt_data["blocos"]):
            bloco = RotinaBloco(
                rotina_id=rotina.id,
                tipo=bloco_data["tipo"],
                label=bloco_data["label"],
                is_required=bloco_data["is_required"],
                posicao=i
            )
            db.add(bloco)

        for func in funcionarios:
            atrib = RotinaAtribuicao(
                rotina_id=rotina.id,
                user_id=func.id,
                assigned_by=current_user.id
            )
            db.add(atrib)
    
    await db.commit()
    return {"message": "Rotinas padrão criadas com sucesso!"}



@router.get("/", response_model=list[RotinaResponse])
async def listar_rotinas(
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Lista todas as rotinas (gestor+)."""
    result = await db.execute(
        select(Rotina)
        .options(selectinload(Rotina.blocos), selectinload(Rotina.atribuicoes))
        .order_by(Rotina.nome)
    )
    rotinas = result.scalars().unique().all()
    return [
        RotinaResponse(
            id=r.id, nome=r.nome, descricao=r.descricao,
            dias_semana=r.dias_semana, alertas=r.alertas or [],
            categoria=r.categoria, status=r.status,
            blocos=[BlocoResponse.model_validate(b) for b in r.blocos],
            total_blocos=len(r.blocos), blocos_concluidos=0,
            created_at=r.created_at,
        )
        for r in rotinas
    ]


@router.post("/", response_model=RotinaResponse, status_code=status.HTTP_201_CREATED)
async def criar_rotina(
    dados: RotinaCreate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Cria uma nova rotina com blocos e atribuições."""
    rotina = Rotina(
        nome=dados.nome,
        descricao=dados.descricao,
        dias_semana=dados.dias_semana,
        alertas=dados.alertas,
        categoria=dados.categoria,
        created_by=current_user.id,
    )
    db.add(rotina)
    await db.flush()

    # Criar blocos
    for i, bloco_config in enumerate(dados.blocos):
        bloco = RotinaBloco(
            rotina_id=rotina.id,
            tipo=bloco_config.tipo,
            label=bloco_config.label,
            config=bloco_config.config,
            posicao=i,
            is_required=bloco_config.is_required,
        )
        db.add(bloco)

    # Criar atribuições
    for user_id in dados.user_ids:
        atrib = RotinaAtribuicao(
            rotina_id=rotina.id,
            user_id=user_id,
            assigned_by=current_user.id,
        )
        db.add(atrib)

    await db.flush()
    logger.info("rotina_criada", rotina_id=str(rotina.id), por=str(current_user.id))

    return RotinaResponse(
        id=rotina.id, nome=rotina.nome, descricao=rotina.descricao,
        dias_semana=rotina.dias_semana, alertas=rotina.alertas or [],
        categoria=rotina.categoria, status=rotina.status,
        blocos=[], total_blocos=len(dados.blocos), blocos_concluidos=0,
        created_at=rotina.created_at,
    )


@router.put("/{rotina_id}", response_model=RotinaResponse)
async def atualizar_rotina(
    rotina_id: UUID,
    dados: RotinaUpdate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Atualiza uma rotina existente (builder save)."""
    result = await db.execute(
        select(Rotina).where(Rotina.id == rotina_id)
        .options(selectinload(Rotina.blocos), selectinload(Rotina.atribuicoes))
    )
    rotina = result.scalar_one_or_none()
    if not rotina:
        raise HTTPException(status_code=404, detail="Rotina não encontrada")

    # Atualizar campos simples
    update_fields = dados.model_dump(exclude_unset=True, exclude={"blocos", "user_ids"})
    for campo, valor in update_fields.items():
        setattr(rotina, campo, valor)

    # Atualizar blocos se fornecidos (recria todos)
    if dados.blocos is not None:
        # Remover blocos existentes
        for bloco in rotina.blocos:
            await db.delete(bloco)
        # Criar novos
        for i, bc in enumerate(dados.blocos):
            bloco = RotinaBloco(
                rotina_id=rotina.id,
                tipo=bc.tipo, label=bc.label, config=bc.config,
                posicao=i, is_required=bc.is_required,
            )
            db.add(bloco)

    # Atualizar atribuições se fornecidas
    if dados.user_ids is not None:
        for atrib in rotina.atribuicoes:
            await db.delete(atrib)
        for uid in dados.user_ids:
            db.add(RotinaAtribuicao(
                rotina_id=rotina.id, user_id=uid, assigned_by=current_user.id
            ))

    await db.flush()
    logger.info("rotina_atualizada", rotina_id=str(rotina_id), por=str(current_user.id))
    return RotinaResponse(
        id=rotina.id, nome=rotina.nome, descricao=rotina.descricao,
        dias_semana=rotina.dias_semana, alertas=rotina.alertas or [],
        categoria=rotina.categoria, status=rotina.status,
        blocos=[], total_blocos=0, blocos_concluidos=0,
        created_at=rotina.created_at,
    )


@router.delete("/{rotina_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_rotina(
    rotina_id: UUID,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Arquiva uma rotina (soft delete via status)."""
    result = await db.execute(select(Rotina).where(Rotina.id == rotina_id))
    rotina = result.scalar_one_or_none()
    if not rotina:
        raise HTTPException(status_code=404, detail="Rotina não encontrada")
    rotina.status = "arquivada"
    logger.info("rotina_arquivada", rotina_id=str(rotina_id), por=str(current_user.id))
