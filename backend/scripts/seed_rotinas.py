# backend/scripts/seed_rotinas.py
import asyncio
import os
import sys

# Adiciona o diretório raiz do backend ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.db.session import async_session_factory
from app.db.models.user import User
from app.db.models.rotina import Rotina, RotinaBloco, RotinaAtribuicao

async def run_seed():
    print("Iniciando seed de rotinas padrão...")
    
    async with async_session_factory() as db:
        # Buscar o primeiro admin ou gestor para ser o criador
        result = await db.execute(select(User).where(User.role.in_(["admin", "gestor"])))
        admin = result.scalars().first()
        
        if not admin:
            print("Erro: Nenhum admin ou gestor encontrado para ser o criador das rotinas.")
            return

        # Buscar funcionários
        result = await db.execute(select(User).where(User.role == "funcionario", User.is_active == True))
        funcionarios = result.scalars().all()
        
        if not funcionarios:
            print("Erro: Nenhum funcionário ativo encontrado para atribuir rotinas.")
            return

        print(f"Gestor/Admin: {admin.name}")
        print(f"Encontrados {len(funcionarios)} funcionários ativos.")

        # Verificar se já existem rotinas
        result = await db.execute(select(Rotina))
        if result.scalars().first():
            print("Aviso: Já existem rotinas no banco de dados. Pulando a criação de rotinas iniciais para não duplicar.")
            return

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
                "dias_semana": [5], # Apenas Sexta
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
                created_by=admin.id
            )
            db.add(rotina)
            await db.flush() # Para gerar o ID da rotina

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
                    assigned_by=admin.id
                )
                db.add(atrib)
        
        await db.commit()
        print("Rotinas iniciais criadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(run_seed())
