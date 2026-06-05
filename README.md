# TRK OS 🌐 — Sistema Operacional do Grupo TRK

Aplicativo **novo**, da empresa inteira (não só financeiro). Cada setor com seu acesso,
o **gestor no controle das permissões**, bloqueio de informação por departamento.

Mantém a paleta do original (preto/branco + emerald/amber/red, fonte Inter).

## Por que esta arquitetura
- **Roda em qualquer lugar, sem infra**: SQLite + auth sem libs externas (PBKDF2 + JWT stdlib).
  Não depende de Postgres/Redis/Celery para subir.
- **Permissões no coração**: 16 módulos × ações (ver/editar), aplicadas no **backend**
  (a API recusa com 403) e no **frontend** (nem aparece no menu).

## Rodar localmente

**Backend** (porta 8010):
```bash
cd backend
python -m venv venv && venv\Scripts\activate   # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --port 8010 --reload
```

**Frontend** (porta 5180, com proxy /api → 8010):
```bash
cd frontend
npm install
npm run dev
# abra http://localhost:5180
```

## Logins demo (senha `Trk@123`)
| E-mail | Papel | O que vê |
|--------|-------|----------|
| diretor@trk.com | Diretor | Tudo (acesso total) |
| financeiro@trk.com | Gestor Financeiro | Saldos, conciliação, contas, empresas… |
| rh@trk.com | Gestora de RH | RH, rotinas, pipes, tarefas (**sem financeiro**) |
| comercial@trk.com | Comercial | Comercial, pipes, tarefas |
| operacoes@trk.com | Operações | Rotinas, pipes, tarefas |

> Entre como **RH** e tente abrir Saldos: o módulo nem aparece — e a API responde **403**.
> Entre como **Diretor** → Usuários → escolha alguém → ligue/desligue módulos na **matriz**.

## Stack
- **Backend**: FastAPI + SQLAlchemy 2 + SQLite. Testes: `pytest` (motor de permissões).
- **Frontend**: Vite + React + TypeScript + TailwindCSS + Zustand.

## Roadmap (próximas fases)
Portar a experiência completa de cada módulo (rotinas, pipes, automações, skills,
conciliação com IA) reaproveitando as funções já testadas — agora dentro do
ecossistema de permissões por setor.
