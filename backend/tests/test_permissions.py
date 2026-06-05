# trk-universe/backend/tests/test_permissions.py
# Testes do motor de permissões por setor.

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.permissions import modulos_acessiveis, permissoes_efetivas, pode


def _user(cargo="colaborador", permissoes=None):
    return SimpleNamespace(cargo=cargo, permissoes=permissoes or {})


def test_diretor_tem_acesso_total():
    u = _user(cargo="diretor")
    assert pode(u, "saldos", "editar")
    assert pode(u, "conciliacao", "ver")
    assert pode(u, "usuarios", "editar")


def test_colaborador_sem_permissao_e_negado():
    u = _user(permissoes={})
    assert pode(u, "saldos", "ver") is False
    assert pode(u, "conciliacao", "ver") is False


def test_permissao_granular_ver_sem_editar():
    u = _user(permissoes={"relatorios": {"ver": True, "editar": False}})
    assert pode(u, "relatorios", "ver") is True
    assert pode(u, "relatorios", "editar") is False


def test_rh_nao_ve_modulos_financeiros():
    u = _user(permissoes={
        "dashboard": {"ver": True, "editar": True},
        "rh": {"ver": True, "editar": True},
        "rotinas": {"ver": True, "editar": True},
    })
    acessiveis = modulos_acessiveis(u)
    assert "rh" in acessiveis
    assert "saldos" not in acessiveis
    assert "conciliacao" not in acessiveis
    assert "contas_bancarias" not in acessiveis


def test_efetivas_preenche_todos_modulos():
    u = _user(permissoes={"dashboard": {"ver": True, "editar": False}})
    ef = permissoes_efetivas(u)
    # todos os módulos presentes, default negado
    assert ef["saldos"] == {"ver": False, "editar": False}
    assert ef["dashboard"]["ver"] is True
