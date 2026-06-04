# backend/app/api/v1/routes/skills.py
# Biblioteca de Skills — capacidades prontas instaláveis em 1 clique.
# GET /skills           -> catálogo
# POST /skills/{id}/instalar -> cria a automação/rotina/pipe correspondente

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import DbSession, require_role
from app.services.skills_catalog import SKILLS, get_skill

router = APIRouter()


@router.get("/")
async def listar_skills(current_user=Depends(require_role(["admin", "gestor"]))):
    """Catálogo de skills disponíveis (sem o payload técnico)."""
    return [
        {k: s[k] for k in ("id", "nome", "descricao", "categoria", "icone", "tipo")}
        for s in SKILLS
    ]


@router.post("/{skill_id}/instalar", status_code=status.HTTP_201_CREATED)
async def instalar_skill(
    skill_id: str,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Instala uma skill, criando o objeto correspondente no portal."""
    skill = get_skill(skill_id)
    if not skill:
        raise HTTPException(404, "Skill não encontrada")

    tipo = skill["tipo"]
    payload = skill["payload"]

    if tipo == "automacao":
        obj_id = await _instalar_automacao(db, skill, payload, current_user)
    elif tipo == "rotina":
        obj_id = await _instalar_rotina(db, skill, payload, current_user)
    elif tipo == "pipe":
        obj_id = await _instalar_pipe(db, payload, current_user)
    else:
        raise HTTPException(422, f"Tipo de skill desconhecido: {tipo}")

    await db.commit()
    return {"status": "instalada", "tipo": tipo, "id": str(obj_id), "nome": skill["nome"]}


async def _instalar_automacao(db, skill, payload, current_user):
    from app.db.models.automacao import Automacao
    auto = Automacao(
        nome=skill["nome"],
        descricao=skill["descricao"],
        gatilho=payload["gatilho"],
        condicao=payload.get("condicao", {}),
        acao=payload["acao"],
        acao_config=payload.get("acao_config", {}),
        ativa=True,
        created_by=current_user.id,
    )
    db.add(auto)
    await db.flush()
    return auto.id


async def _instalar_rotina(db, skill, payload, current_user):
    from app.db.models.rotina import Rotina, RotinaAtribuicao, RotinaBloco
    rotina = Rotina(
        nome=payload["nome"],
        descricao=payload.get("descricao"),
        dias_semana=payload.get("dias_semana", []),
        tipo_recorrencia=payload.get("tipo_recorrencia", "semanal"),
        recorrencia_config=payload.get("recorrencia_config", {}),
        categoria=payload.get("categoria", "geral"),
        created_by=current_user.id,
    )
    db.add(rotina)
    await db.flush()
    for i, bloco in enumerate(payload.get("blocos", [])):
        db.add(RotinaBloco(
            rotina_id=rotina.id, tipo=bloco["tipo"], label=bloco["label"],
            config=bloco.get("config", {}), posicao=i,
            is_required=bloco.get("is_required", False),
        ))
    # Atribui ao próprio instalador (gestor) para já aparecer
    db.add(RotinaAtribuicao(rotina_id=rotina.id, user_id=current_user.id, assigned_by=current_user.id))
    return rotina.id


async def _instalar_pipe(db, payload, current_user):
    from app.db.models.pipe import Pipe, PipeFase
    from app.services.pipes import fases_do_template
    pipe = Pipe(
        nome=payload["nome"], cor=payload.get("cor", "#171717"),
        created_by=current_user.id,
    )
    db.add(pipe)
    await db.flush()
    for f in fases_do_template(payload.get("template")):
        db.add(PipeFase(
            pipe_id=pipe.id, nome=f["nome"], ordem=f.get("ordem", 0),
            cor=f.get("cor", "#94a3b8"), is_final=f.get("is_final", False),
            sla_horas=f.get("sla_horas"),
        ))
    return pipe.id
