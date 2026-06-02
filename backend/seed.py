# backend/seed.py
# Script de seed inicial do Portal TRK.
# Cria: primeiro admin + todas as 23 empresas + configuracao de sync padrao.
# Uso: python seed.py (na raiz do backend)

import asyncio
import uuid
from datetime import time

from app.core.security import hash_senha
from app.db.base import Base
from app.db.models import *  # noqa
from app.db.session import async_session_factory, engine


async def seed():
    """Popula o banco com dados iniciais."""

    # Criar tabelas (em dev - em producao usar Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # === Admin ===
        admin = User(
            name="Administrador TRK",
            email="admin@trk.com.br",
            password_hash=hash_senha("admin123"),
            role="admin",
            phone_whatsapp="+5511999999999",
        )
        db.add(admin)
        await db.flush()

        # === Gestores ===
        rafael = User(
            name="Rafael",
            email="rafael@trk.com.br",
            password_hash=hash_senha("rafael123"),
            role="gestor",
        )
        tarik = User(
            name="Tarik",
            email="tarik@trk.com.br",
            password_hash=hash_senha("tarik123"),
            role="gestor",
        )
        db.add_all([rafael, tarik])
        await db.flush()

        # === Empresas TRK (6) ===
        empresas_trk = [
            ("CMF Consultoria", "00.000.000/0001-01", "inter"),
            ("RR Participacoes", "00.000.000/0001-02", "santander"),
            ("Tarifa Participacoes", "00.000.000/0001-03", "bradesco"),
            ("TRK Aluguel", "00.000.000/0001-04", "inter"),
            ("TRK Empresa", "00.000.000/0001-05", "santander"),
            ("TRK Consultoria", "00.000.000/0001-06", "inter"),
        ]

        for nome, cnpj, banco in empresas_trk:
            emp = Empresa(
                nome=nome, cnpj=cnpj, banco=banco,
                grupo="trk", responsavel_user_id=rafael.id,
            )
            db.add(emp)

        # === Empresas BPO (17) ===
        empresas_bpo = [
            ("Acao", "00.000.000/0002-01", "santander"),
            ("Ativus", "00.000.000/0002-02", "inter"),
            ("Audax", "00.000.000/0002-03", "bradesco"),
            ("Autor", "00.000.000/0002-04", "inter"),
            ("Bird", "00.000.000/0002-05", "santander"),
            ("Eleven&One", "00.000.000/0002-06", "inter"),
            ("Esfera", "00.000.000/0002-07", "bradesco"),
            ("Gibraltar", "00.000.000/0002-08", "santander"),
            ("Golf", "00.000.000/0002-09", "inter"),
            ("K Finserv", "00.000.000/0002-10", "bradesco"),
            ("K Consultoria", "00.000.000/0002-11", "santander"),
            ("Malaga", "00.000.000/0002-12", "inter"),
            ("Mar Azul", "00.000.000/0002-13", "bradesco"),
            ("Quintas", "00.000.000/0002-14", "santander"),
            ("Residencial Garden", "00.000.000/0002-15", "inter"),
            ("ROI", "00.000.000/0002-16", "bradesco"),
            ("School", "00.000.000/0002-17", "santander"),
        ]

        for nome, cnpj, banco in empresas_bpo:
            emp = Empresa(
                nome=nome, cnpj=cnpj, banco=banco,
                grupo="bpo", responsavel_user_id=tarik.id,
            )
            db.add(emp)

        # === Configuracao de Sync ===
        sync_config = SyncConfig(
            horario_1=time(6, 0),
            horario_2=time(20, 0),
            whatsapp_horario=time(6, 30),
            relatorio_dia_semana=5,
            relatorio_horario=time(18, 0),
            updated_by=admin.id,
        )
        db.add(sync_config)

        await db.commit()
        print("[OK] Seed concluido com sucesso!")
        print("   Admin: admin@trk.com.br / admin123")
        print("   Rafael: rafael@trk.com.br / rafael123")
        print("   Tarik: tarik@trk.com.br / tarik123")
        print("   Empresas: 6 TRK + 17 BPO = 23 total")


if __name__ == "__main__":
    asyncio.run(seed())
