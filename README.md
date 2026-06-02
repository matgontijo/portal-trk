# Portal TRK 🚀

O **Portal TRK** é o sistema operacional interno e exclusivo corporativo criado para gerenciar as 23 empresas do Grupo TRK (Fundo de Investimentos Imobiliários). Ele atua como um ERP/CRM customizado, centralizando conciliações bancárias via Inteligência Artificial, gestão de rotinas diárias e integração com Open Finance.

---

## 📖 Parte 1: Manual do Usuário (Equipe TRK)

Bem-vindo ao Portal TRK! Este guia ajudará você a navegar e utilizar as ferramentas do portal de acordo com o seu perfil de acesso.

### Níveis de Acesso
O portal é inteligente e adapta a tela dependendo de quem você é:
1. **Gestor / Admin (Liderança):** Visão completa do negócio. Pode ver dashboards, todas as empresas, acompanhar o progresso de toda a equipe e criar/configurar novas rotinas e usuários.
2. **Funcionário (Operação):** Visão focada e sem distrações. Vê apenas o que precisa ser feito no dia (as suas rotinas) e o seu progresso pessoal.

### Funcionalidades Principais

#### 🔄 1. Conciliação Bancária (BPO)
O coração financeiro do portal. O sistema puxa os dados do **Omie** e dos **Bancos (Inter, Santander, Bradesco)** e usa **Inteligência Artificial** para cruzar as contas a pagar/receber automaticamente.
- Se a IA tem 100% de certeza, ela concilia sozinha (`Match Exato`).
- Se a IA tem dúvida, ela sugere a conciliação para você aprovar com 1 clique (`Sugestão IA`).

#### 📋 2. Rotinas (O seu "Pipefy" interno)
A aba de rotinas dita o ritmo de trabalho diário.
- **Para a Gestora:** Aqui você possui um "Builder". Clique em `Nova Rotina` para montar um checklist do zero. Você pode adicionar campos de texto, botões de check e campos de link/upload, dizer em quais dias da semana essa rotina se repete e atribuir ao funcionário responsável.
- **Para o Funcionário:** Você verá seu "Checklist do Dia". Basta preencher as informações pedidas e marcar as caixinhas. Seu progresso (a barrinha verde) avança em tempo real e a liderança consegue acompanhar.

#### 👥 3. Gestão de Usuários
Na tela de Usuários (restrita a Gestores), você tem o poder de cadastrar novos funcionários no sistema. Basta preencher nome, e-mail e senha provisória, definindo se a pessoa será da Gestão ou da Operação.

#### 🏢 4. Empresas e Tarefas
- O portal mantém um diretório seguro com os dados das 23 empresas do grupo.
- Você possui um painel de **Tarefas (Kanban)** para projetos isolados que não se encaixam numa rotina diária repetitiva.

---

## 💻 Parte 2: Documentação Técnica (Para Desenvolvedores)

Se você é um desenvolvedor assumindo este projeto, parabéns! Você tem em mãos uma arquitetura moderna, robusta e escalável orientada a microsserviços e processamento em background.

### 🛠️ Stack Tecnológica

**Frontend (React Premium):**
- **Core:** React 18 + Vite + TypeScript.
- **Estilização:** TailwindCSS 3 (Design System customizado com variáveis semânticas `primary`, `success`, `danger`, e animações de micro-interações).
- **Estado e API:** Zustand (Gerenciamento Global) + React Router v6.
- **PWA:** Preparado com Service Workers para offline-first.

**Backend (Python de Alta Performance):**
- **Core:** FastAPI (Python 3.12) rodando com Uvicorn/Gunicorn.
- **Banco de Dados:** PostgreSQL 15 via SQLAlchemy 2.0 (Totalmente Assíncrono) + Alembic para migrações.
- **Background Jobs:** Celery (Workers) + Celery Beat (Cron) + Redis 7 (Message Broker & Cache).
- **Inteligência Artificial:** Scikit-Learn (RandomForest Classifier com TF-IDF text vectorization) rodando em fallback determinístico.

### 🏗️ Arquitetura e Modelagem

- **Autenticação:** Baseada em JWT (JSON Web Tokens) stateless, com controle rigoroso de RBAC (Role-Based Access Control) nas rotas (`admin`, `gestor`, `funcionario`).
- **Sync Bancário (Workers):** O Celery dispara tarefas às 06h00 e 20h00 para consumir extratos via Open Finance e notas do Omie, rodando a predição da IA e populando a tabela `conciliacoes`.
- **Proteção de Rotas UI:** O Frontend possui um componente `<RoleGuard>` que bloqueia a renderização de telas e botões caso o Payload do JWT não permita o acesso, evitando vazamento de UI.

### 🚀 Setup Local (Como Rodar)

**Pré-requisitos:** Node 20+, Python 3.12, Docker Desktop.

1. **Subir Banco e Broker:**
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

2. **Backend (API):**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (No Windows: venv\Scripts\activate)
pip install -r requirements.txt

# Copie o .env.example para .env e gere as tabelas:
cp .env.example .env
alembic upgrade head
python seed.py # Popula as empresas e admin inicial

uvicorn app.main:app --reload
```

3. **Frontend (UI):**
```bash
cd frontend
npm install
npm run dev
# Acesse: http://localhost:5173 (admin@grupotropik.com.br / Admin@2024!)
```

### ☁️ Deploy (Render.com)
O projeto conta com Infraestrutura como Código (IaC). O arquivo `render.yaml` na raiz orquestra 5 serviços simultâneos:
1. Web Service (FastAPI)
2. Celery Worker (Processamento pesado/IA)
3. PostgreSQL Database
4. Redis Instance
5. Static Site (React UI)

Basta conectar o repositório no [Render](https://render.com) via Blueprint e tudo será provisionado automaticamente.

---
*Construído com ♥ focando na melhor UI/UX e escalabilidade técnica.*
