# backend/app/workers/beat_schedule.py
# Schedule dinâmico do Celery Beat para o Portal TRK.
# Lê os horários da tabela sync_config — nunca hardcoded.
# O Beat relê a cada 5 minutos para capturar mudanças de configuração.

from celery.schedules import crontab

# Schedule padrão (usado se o banco não estiver disponível)
# Em produção, o DatabaseScheduler sobrescreve com valores do banco.
DEFAULT_BEAT_SCHEDULE = {
    # Sync bancário — horários padrão 06:00 e 20:00 BRT
    "sync-saldos-manha": {
        "task": "app.workers.tasks.sync_saldos.sync_todas_empresas",
        "schedule": crontab(hour=6, minute=0),
    },
    "sync-saldos-noite": {
        "task": "app.workers.tasks.sync_saldos.sync_todas_empresas",
        "schedule": crontab(hour=20, minute=0),
    },
    # Conciliação automática — após cada sync
    "conciliacao-auto-manha": {
        "task": "app.workers.tasks.conciliacao_auto.conciliar_todas",
        "schedule": crontab(hour=6, minute=30),
    },
    "conciliacao-auto-noite": {
        "task": "app.workers.tasks.conciliacao_auto.conciliar_todas",
        "schedule": crontab(hour=20, minute=30),
    },
    # Re-treinamento ML — segunda-feira 03:00
    "treinar-modelo-semanal": {
        "task": "app.workers.tasks.treinar_modelo.treinar_modelo_task",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),
    },
    # Relatório semanal — sexta-feira 18:00
    "relatorio-semanal": {
        "task": "app.workers.tasks.relatorio_semanal.gerar_relatorio",
        "schedule": crontab(hour=18, minute=0, day_of_week=5),
    },
    # WhatsApp diário — 06:30
    "whatsapp-diario": {
        "task": "app.workers.tasks.whatsapp_diario.enviar_resumo_diario",
        "schedule": crontab(hour=6, minute=30),
    },
}


def get_beat_schedule() -> dict:
    """
    Retorna o schedule do Beat.
    Em produção, sobrescreve com valores do banco sync_config.
    Decisão: lê do banco de forma síncrona no startup do Beat.
    Para mudanças em runtime, o Beat é reiniciado (Render redeploy).
    """
    try:
        # Tentativa de ler do banco (síncrona para o Beat)
        import psycopg2
        from app.core.config import get_settings

        settings = get_settings()
        sync_url = settings.database_url_sync.replace("postgresql+asyncpg://", "postgresql://")

        conn = psycopg2.connect(sync_url)
        cur = conn.cursor()
        cur.execute("SELECT horario_1, horario_2, whatsapp_horario, relatorio_dia_semana, relatorio_horario FROM sync_config LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if row:
            h1, h2, wh, rd, rh = row
            schedule = dict(DEFAULT_BEAT_SCHEDULE)
            schedule["sync-saldos-manha"]["schedule"] = crontab(hour=h1.hour, minute=h1.minute)
            schedule["sync-saldos-noite"]["schedule"] = crontab(hour=h2.hour, minute=h2.minute)
            schedule["conciliacao-auto-manha"]["schedule"] = crontab(hour=h1.hour, minute=h1.minute + 30)
            schedule["conciliacao-auto-noite"]["schedule"] = crontab(hour=h2.hour, minute=h2.minute + 30)
            schedule["whatsapp-diario"]["schedule"] = crontab(hour=wh.hour, minute=wh.minute)
            schedule["relatorio-semanal"]["schedule"] = crontab(hour=rh.hour, minute=rh.minute, day_of_week=rd)
            return schedule

    except Exception:
        pass

    return DEFAULT_BEAT_SCHEDULE
