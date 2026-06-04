# backend/tests/test_automacoes.py
# Testes da engine de automações (avaliação pura + execução de ação).

from types import SimpleNamespace

from app.services.automacoes import avaliar_condicao, executar_acao


def test_sem_regras_dispara_sempre():
    assert avaliar_condicao({}, {"qualquer": 1}) is True
    assert avaliar_condicao({"regras": []}, {}) is True


def test_operador_maior_que_numerico():
    cond = {"regras": [{"campo": "delta_abs", "op": ">", "valor": 1000}]}
    assert avaliar_condicao(cond, {"delta_abs": 1500}) is True
    assert avaliar_condicao(cond, {"delta_abs": 500}) is False


def test_logica_and_exige_todas():
    cond = {"logica": "and", "regras": [
        {"campo": "delta_abs", "op": ">", "valor": 1000},
        {"campo": "tipo_divergencia", "op": "==", "valor": "pagamento_nao_processado"},
    ]}
    assert avaliar_condicao(cond, {"delta_abs": 2000, "tipo_divergencia": "pagamento_nao_processado"}) is True
    assert avaliar_condicao(cond, {"delta_abs": 2000, "tipo_divergencia": "outro"}) is False


def test_logica_or_basta_uma():
    cond = {"logica": "or", "regras": [
        {"campo": "prioridade", "op": "==", "valor": "urgente"},
        {"campo": "delta_abs", "op": ">", "valor": 10000},
    ]}
    assert avaliar_condicao(cond, {"prioridade": "urgente", "delta_abs": 1}) is True
    assert avaliar_condicao(cond, {"prioridade": "baixa", "delta_abs": 1}) is False


def test_operador_contains():
    cond = {"regras": [{"campo": "empresa_nome", "op": "contains", "valor": "trk"}]}
    assert avaliar_condicao(cond, {"empresa_nome": "Holding TRK LTDA"}) is True
    assert avaliar_condicao(cond, {"empresa_nome": "Outra Empresa"}) is False


class _FakeSession:
    """Session mínima para testar executar_acao sem banco real."""
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)


def test_executar_acao_criar_tarefa():
    sess = _FakeSession()
    auto = SimpleNamespace(
        nome="Tarefa em divergência",
        acao="criar_tarefa",
        acao_config={"titulo": "Conciliar {empresa_nome}", "prioridade": "urgente", "prazo_dias": 1},
    )
    ok = executar_acao(sess, auto, {"empresa_nome": "ACME", "user_id": None, "empresa_id": None})
    assert ok is True
    assert len(sess.added) == 1
    tarefa = sess.added[0]
    assert tarefa.titulo == "Conciliar ACME"
    assert tarefa.prioridade == "urgente"
    assert tarefa.prazo is not None


def test_executar_acao_notificar_sem_user_nao_executa():
    sess = _FakeSession()
    auto = SimpleNamespace(nome="x", acao="notificar", acao_config={"titulo": "oi"})
    ok = executar_acao(sess, auto, {})  # sem user_id
    assert ok is False
    assert sess.added == []
