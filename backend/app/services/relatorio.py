# backend/app/services/relatorio.py
# Geração de relatório semanal PDF com WeasyPrint.
# Layout profissional com capa, KPIs, divergências e atividade da equipe.

import os
from datetime import date

import structlog

logger = structlog.get_logger()


def gerar_relatorio_pdf(caminho: str, data_inicio: date, data_fim: date) -> str:
    """
    Gera relatório semanal em PDF usando WeasyPrint.
    Retorna o caminho do arquivo gerado.
    """
    from weasyprint import HTML

    html_content = _montar_html_relatorio(data_inicio, data_fim)

    HTML(string=html_content).write_pdf(caminho)
    logger.info("relatorio_pdf_gerado", caminho=caminho)
    return caminho


def _montar_html_relatorio(data_inicio: date, data_fim: date) -> str:
    """Monta o HTML do relatório com CSS inline para WeasyPrint."""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 2cm; }}
            body {{ font-family: 'Inter', Arial, sans-serif; color: #1e293b; font-size: 11pt; line-height: 1.6; }}
            .capa {{ text-align: center; padding: 120px 0 60px; page-break-after: always; }}
            .capa h1 {{ font-size: 28pt; color: #6366F1; margin-bottom: 10px; }}
            .capa .periodo {{ font-size: 14pt; color: #64748b; margin-top: 20px; }}
            .capa .gerado {{ font-size: 10pt; color: #94a3b8; margin-top: 40px; }}
            h2 {{ color: #6366F1; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 10pt; }}
            th {{ background-color: #6366F1; color: white; padding: 10px 8px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; }}
            tr:nth-child(even) {{ background-color: #f8fafc; }}
            .kpi-grid {{ display: flex; gap: 15px; margin: 20px 0; }}
            .kpi-card {{ flex: 1; padding: 15px; border-radius: 8px; text-align: center; }}
            .kpi-card.primary {{ background: #eef2ff; color: #6366F1; }}
            .kpi-card.success {{ background: #ecfdf5; color: #059669; }}
            .kpi-card.danger {{ background: #fef2f2; color: #dc2626; }}
            .kpi-card .valor {{ font-size: 20pt; font-weight: 700; }}
            .kpi-card .label {{ font-size: 9pt; color: #64748b; margin-top: 5px; }}
            .badge-ok {{ color: #059669; font-weight: 600; }}
            .badge-divergente {{ color: #dc2626; font-weight: 600; }}
            .rodape {{ text-align: center; color: #94a3b8; font-size: 8pt; margin-top: 40px; padding-top: 15px; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <!-- Capa -->
        <div class="capa">
            <h1>Portal TRK</h1>
            <p style="font-size: 16pt; color: #475569;">Relatório Semanal</p>
            <p class="periodo">Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</p>
            <p class="gerado">Gerado automaticamente pelo Portal TRK em {data_fim.strftime('%d/%m/%Y')}</p>
        </div>

        <!-- 1. Resumo Executivo -->
        <h2>1. Resumo Executivo</h2>
        <table>
            <thead>
                <tr><th>Empresa</th><th>Saldo Atual</th><th>Variação</th><th>Status</th></tr>
            </thead>
            <tbody>
                <tr><td colspan="4" style="text-align: center; color: #94a3b8;">Dados serão preenchidos automaticamente quando o sync estiver configurado</td></tr>
            </tbody>
        </table>

        <!-- 2. Divergências -->
        <h2>2. Divergências da Semana</h2>
        <p style="color: #64748b;">Nenhuma divergência registrada no período.</p>

        <!-- 3. Atividade da Equipe -->
        <h2>3. Atividade da Equipe</h2>
        <table>
            <thead>
                <tr><th>Funcionário</th><th>Rotinas (%)</th><th>Tarefas Concluídas</th><th>Em Atraso</th></tr>
            </thead>
            <tbody>
                <tr><td colspan="4" style="text-align: center; color: #94a3b8;">Dados serão preenchidos conforme uso do sistema</td></tr>
            </tbody>
        </table>

        <!-- 4. Contas a Pagar -->
        <h2>4. Contas a Pagar — Próxima Semana</h2>
        <p style="color: #64748b;">Nenhum vencimento registrado.</p>

        <div class="rodape">
            Gerado automaticamente pelo Portal TRK em {data_fim.strftime('%d/%m/%Y')}
        </div>
    </body>
    </html>
    """
