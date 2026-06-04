# backend/app/services/skills_catalog.py
# Catálogo de "Skills" do Portal TRK — capacidades prontas instaláveis em 1 clique.
# Inspirado no conceito de skills do Claude: blocos de habilidade reutilizáveis.
#
# Cada skill tem um `tipo` (automacao | rotina | pipe) e um `payload` que descreve
# o que será criado quando o usuário instalar. O catálogo é DADO (sem I/O) — fácil
# de testar e de estender.

SKILLS: list[dict] = [
    # ───────────────────────── Automações ─────────────────────────
    {
        "id": "alerta-divergencia-alta",
        "nome": "Alerta de divergência alta",
        "descricao": "Quando o saldo divergir mais de R$ 1.000 do Omie, cria uma tarefa urgente e avisa o responsável.",
        "categoria": "Financeiro",
        "icone": "AlertTriangle",
        "tipo": "automacao",
        "payload": {
            "gatilho": "saldo_divergencia",
            "condicao": {"logica": "and", "regras": [{"campo": "delta_abs", "op": ">", "valor": 1000}]},
            "acao": "criar_tarefa",
            "acao_config": {
                "titulo": "Conciliar divergência — {empresa_nome}",
                "descricao": "Diferença de R$ {delta_abs} entre banco e Omie.",
                "prioridade": "urgente", "prazo_dias": 1,
            },
        },
    },
    {
        "id": "escalar-falha-sync",
        "nome": "Escalar falha de sincronização",
        "descricao": "Se a busca de saldo de uma empresa falhar, notifica imediatamente o responsável.",
        "categoria": "Financeiro",
        "icone": "WifiOff",
        "tipo": "automacao",
        "payload": {
            "gatilho": "saldo_falha",
            "condicao": {},
            "acao": "notificar",
            "acao_config": {"titulo": "Falha no saldo — {empresa_nome}", "mensagem": "Verifique as credenciais/banco.", "tipo": "sistema"},
        },
    },
    {
        "id": "registro-conciliado",
        "nome": "Confirmar dia conciliado",
        "descricao": "Quando o saldo é atualizado sem divergências, registra uma notificação de 'tudo certo'.",
        "categoria": "Financeiro",
        "icone": "CheckCircle2",
        "tipo": "automacao",
        "payload": {
            "gatilho": "saldo_atualizado",
            "condicao": {},
            "acao": "notificar",
            "acao_config": {"titulo": "Saldo conciliado — {empresa_nome}", "mensagem": "Banco e Omie batem.", "tipo": "sync_concluido"},
        },
    },

    # ───────────────────────── Rotinas ─────────────────────────
    {
        "id": "fechamento-diario-caixa",
        "nome": "Fechamento diário de caixa",
        "descricao": "Checklist diário para conferir saldos, conciliar lançamentos e registrar pendências.",
        "categoria": "Rotinas",
        "icone": "Wallet",
        "tipo": "rotina",
        "payload": {
            "nome": "Fechamento diário de caixa",
            "descricao": "Rotina de conferência financeira do dia.",
            "tipo_recorrencia": "diaria",
            "recorrencia_config": {"apenas_dias_uteis": True},
            "categoria": "banco",
            "blocos": [
                {"tipo": "section_header", "label": "Conferência de saldos", "is_required": False},
                {"tipo": "checkbox", "label": "Conferir saldo de todas as contas", "is_required": True},
                {"tipo": "checkbox", "label": "Conciliar lançamentos do dia", "is_required": True},
                {"tipo": "text_long", "label": "Pendências/observações", "is_required": False},
            ],
        },
    },
    {
        "id": "conciliacao-matinal",
        "nome": "Conciliação matinal",
        "descricao": "Toda manhã: revisar sugestões da IA e aprovar/recusar conciliações.",
        "categoria": "Rotinas",
        "icone": "Sunrise",
        "tipo": "rotina",
        "payload": {
            "nome": "Conciliação matinal",
            "descricao": "Revisão das conciliações sugeridas pela IA.",
            "tipo_recorrencia": "semanal",
            "dias_semana": [1, 2, 3, 4, 5],
            "categoria": "omie",
            "blocos": [
                {"tipo": "checkbox", "label": "Revisar sugestões da IA", "is_required": True},
                {"tipo": "checkbox", "label": "Aprovar matches corretos", "is_required": True},
                {"tipo": "link", "label": "Link do relatório (se houver)", "is_required": False},
            ],
        },
    },
    {
        "id": "fechamento-mensal",
        "nome": "Fechamento mensal",
        "descricao": "No último dia do mês: conferir documentos e fechar competência.",
        "categoria": "Rotinas",
        "icone": "CalendarCheck",
        "tipo": "rotina",
        "payload": {
            "nome": "Fechamento mensal",
            "descricao": "Conferências de fim de mês.",
            "tipo_recorrencia": "mensal",
            "recorrencia_config": {"ultimo_dia": True},
            "categoria": "geral",
            "blocos": [
                {"tipo": "checkbox", "label": "Conferir notas do mês", "is_required": True},
                {"tipo": "file_upload", "label": "Anexar balancete", "is_required": False},
                {"tipo": "checkbox", "label": "Fechar competência no Omie", "is_required": True},
            ],
        },
    },

    # ───────────────────────── Pipes ─────────────────────────
    {
        "id": "pipe-contas-pagar",
        "nome": "Pipe: Contas a Pagar",
        "descricao": "Fluxo Recebido → Análise → Aprovado → Pago, com SLA na análise.",
        "categoria": "Pipes",
        "icone": "Receipt",
        "tipo": "pipe",
        "payload": {"nome": "Contas a Pagar", "template": "contas_pagar", "cor": "#10b981"},
    },
    {
        "id": "pipe-onboarding",
        "nome": "Pipe: Onboarding de Cliente",
        "descricao": "Lead → Documentação → Configuração → Ativo, para entrada de novas empresas.",
        "categoria": "Pipes",
        "icone": "UserPlus",
        "tipo": "pipe",
        "payload": {"nome": "Onboarding de Cliente", "template": "onboarding", "cor": "#475569"},
    },
    {
        "id": "pipe-tarefas",
        "nome": "Pipe: Quadro de Tarefas",
        "descricao": "Quadro simples A Fazer → Em Andamento → Concluído para projetos avulsos.",
        "categoria": "Pipes",
        "icone": "Kanban",
        "tipo": "pipe",
        "payload": {"nome": "Quadro de Tarefas", "template": "padrao", "cor": "#171717"},
    },
]


def get_skill(skill_id: str) -> dict | None:
    return next((s for s in SKILLS if s["id"] == skill_id), None)
