# backend/tests/test_skills.py
# Sanidade do catálogo de skills.

from app.db.models.automacao import ACOES, GATILHOS
from app.services.skills_catalog import SKILLS, get_skill


def test_skills_tem_campos_obrigatorios():
    ids = set()
    for s in SKILLS:
        for campo in ("id", "nome", "descricao", "categoria", "icone", "tipo", "payload"):
            assert campo in s, f"{s.get('id')} sem campo {campo}"
        assert s["tipo"] in ("automacao", "rotina", "pipe")
        assert s["id"] not in ids, f"id duplicado: {s['id']}"
        ids.add(s["id"])


def test_skills_automacao_usam_gatilhos_e_acoes_validos():
    for s in SKILLS:
        if s["tipo"] == "automacao":
            assert s["payload"]["gatilho"] in GATILHOS
            assert s["payload"]["acao"] in ACOES


def test_skills_pipe_tem_template():
    for s in SKILLS:
        if s["tipo"] == "pipe":
            assert s["payload"].get("template") in ("padrao", "contas_pagar", "onboarding")


def test_skills_rotina_tem_blocos():
    for s in SKILLS:
        if s["tipo"] == "rotina":
            assert len(s["payload"].get("blocos", [])) >= 1


def test_get_skill():
    assert get_skill("pipe-contas-pagar") is not None
    assert get_skill("inexistente") is None
