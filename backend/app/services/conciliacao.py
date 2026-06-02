# backend/app/services/conciliacao.py
# Engine de conciliação inteligente do Portal TRK.
# Responsabilidades:
#   - Fase 1: Rule-based matching (exato, CNPJ+valor, valor±3d)
#   - Fase 2: ML classifier para não resolvidos
#   - Registro de todos os matches no banco
#   - Detecção e classificação de divergências
#
# DECISÃO TÉCNICA: As fases são sequenciais — a Fase 2 só processa
# lançamentos não resolvidos pela Fase 1. Isso garante que matches
# determinísticos (100% certos) nunca dependam do ML.

from datetime import date, timedelta
from decimal import Decimal

import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.conciliacao import Conciliacao
from app.db.models.lancamento import LancamentoBanco, LancamentoOmie

logger = structlog.get_logger()


class ConciliacaoEngine:
    """Engine de conciliação em duas fases: rule-based + ML."""

    def __init__(self, db: AsyncSession, empresa_id: str):
        self.db = db
        self.empresa_id = empresa_id
        self.matches: list[Conciliacao] = []
        self.nao_resolvidos_banco: list[LancamentoBanco] = []
        self.nao_resolvidos_omie: list[LancamentoOmie] = []

    async def executar(self, data_referencia: date | None = None) -> dict:
        """
        Executa a conciliação completa para a empresa.
        Retorna estatísticas do processamento.
        """
        data_ref = data_referencia or date.today()

        # Buscar lançamentos não conciliados
        lancamentos_banco = await self._buscar_lancamentos_banco(data_ref)
        lancamentos_omie = await self._buscar_lancamentos_omie(data_ref)

        logger.info(
            "conciliacao_iniciada",
            empresa_id=self.empresa_id,
            lancamentos_banco=len(lancamentos_banco),
            lancamentos_omie=len(lancamentos_omie),
        )

        # ═══ FASE 1: RULE-BASED ═══
        nao_resolvidos_banco, nao_resolvidos_omie = await self._fase1_rules(
            lancamentos_banco, lancamentos_omie, data_ref
        )

        stats_fase1 = len(self.matches)

        # ═══ FASE 2: ML CLASSIFIER ═══
        if nao_resolvidos_banco and nao_resolvidos_omie:
            await self._fase2_ml(nao_resolvidos_banco, nao_resolvidos_omie, data_ref)

        stats_fase2 = len(self.matches) - stats_fase1

        # Salvar todos os matches
        for match in self.matches:
            self.db.add(match)

        stats = {
            "total_banco": len(lancamentos_banco),
            "total_omie": len(lancamentos_omie),
            "matches_fase1": stats_fase1,
            "matches_fase2": stats_fase2,
            "nao_resolvidos": len(self.nao_resolvidos_banco),
        }
        logger.info("conciliacao_concluida", empresa_id=self.empresa_id, **stats)
        return stats

    async def _buscar_lancamentos_banco(self, data_ref: date) -> list[LancamentoBanco]:
        """Busca lançamentos bancários não conciliados no período."""
        # Buscar lançamentos que não têm match na tabela conciliacao
        subq = select(Conciliacao.lancamento_banco_id).where(
            Conciliacao.lancamento_banco_id.isnot(None),
            Conciliacao.status == "ok",
        )
        result = await self.db.execute(
            select(LancamentoBanco).where(
                LancamentoBanco.empresa_id == self.empresa_id,
                LancamentoBanco.data_lancamento >= data_ref - timedelta(days=7),
                LancamentoBanco.data_lancamento <= data_ref,
                LancamentoBanco.id.notin_(subq),
            )
        )
        return list(result.scalars().all())

    async def _buscar_lancamentos_omie(self, data_ref: date) -> list[LancamentoOmie]:
        """Busca lançamentos Omie não conciliados no período."""
        subq = select(Conciliacao.lancamento_omie_id).where(
            Conciliacao.lancamento_omie_id.isnot(None),
            Conciliacao.status == "ok",
        )
        result = await self.db.execute(
            select(LancamentoOmie).where(
                LancamentoOmie.empresa_id == self.empresa_id,
                LancamentoOmie.data_lancamento >= data_ref - timedelta(days=7),
                LancamentoOmie.data_lancamento <= data_ref,
                LancamentoOmie.id.notin_(subq),
            )
        )
        return list(result.scalars().all())

    async def _fase1_rules(
        self,
        lancamentos_banco: list[LancamentoBanco],
        lancamentos_omie: list[LancamentoOmie],
        data_ref: date,
    ) -> tuple[list[LancamentoBanco], list[LancamentoOmie]]:
        """
        Fase 1: Matching por regras determinísticas.
        a) Match exato: valor idêntico + data ±1 dia útil → confidence = 1.0
        b) Match CNPJ + valor: identifica pagador → confidence = 0.95
        c) Mesmo valor, data ±3 dias: candidato → vai para revisão
        """
        banco_matched = set()
        omie_matched = set()

        # a) Match exato — valor e data ±1 dia útil
        for lb in lancamentos_banco:
            if lb.id in banco_matched:
                continue
            for lo in lancamentos_omie:
                if lo.id in omie_matched:
                    continue

                diff_valor = abs(lb.valor - lo.valor)
                diff_dias = abs((lb.data_lancamento - lo.data_lancamento).days)

                if diff_valor == 0 and diff_dias <= 1:
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=lo.id,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="ok",
                        confidence_score=1.0,
                        metodo="rule_exact",
                    ))
                    banco_matched.add(lb.id)
                    omie_matched.add(lo.id)
                    break

        # b) Match CNPJ + valor
        for lb in lancamentos_banco:
            if lb.id in banco_matched or not lb.cnpj_contraparte:
                continue
            for lo in lancamentos_omie:
                if lo.id in omie_matched:
                    continue

                diff_valor = abs(lb.valor - lo.valor)
                if diff_valor == 0:
                    # Mesmos CNPJ no histórico — alto confidence
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=lo.id,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="ok",
                        confidence_score=0.95,
                        metodo="rule_cnpj",
                    ))
                    banco_matched.add(lb.id)
                    omie_matched.add(lo.id)
                    break

        # c) Mesmo valor, data ±3 dias → revisão manual
        for lb in lancamentos_banco:
            if lb.id in banco_matched:
                continue
            for lo in lancamentos_omie:
                if lo.id in omie_matched:
                    continue

                diff_valor = abs(lb.valor - lo.valor)
                diff_dias = abs((lb.data_lancamento - lo.data_lancamento).days)

                if diff_valor == 0 and diff_dias <= 3:
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=lo.id,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="revisao_manual",
                        confidence_score=0.80,
                        metodo="rule_exact",
                        obs=f"Match por valor exato com {diff_dias} dia(s) de diferença",
                    ))
                    banco_matched.add(lb.id)
                    omie_matched.add(lo.id)
                    break

        # Lançamentos não resolvidos
        self.nao_resolvidos_banco = [lb for lb in lancamentos_banco if lb.id not in banco_matched]
        self.nao_resolvidos_omie = [lo for lo in lancamentos_omie if lo.id not in omie_matched]

        return self.nao_resolvidos_banco, self.nao_resolvidos_omie

    async def _fase2_ml(
        self,
        lancamentos_banco: list[LancamentoBanco],
        lancamentos_omie: list[LancamentoOmie],
        data_ref: date,
    ) -> None:
        """
        Fase 2: ML classifier para lançamentos não resolvidos.
        Usa o modelo ativo em ml_model_versions.
        Se não há modelo ativo (cold start), pula esta fase.
        """
        try:
            from app.services.ml_conciliacao import MLConciliador
            ml = MLConciliador()
            loaded = await ml.carregar_modelo_ativo(self.db)
            if not loaded:
                logger.info("ml_cold_start", msg="Sem modelo ML ativo — pulando fase 2")
                return

            for lb in lancamentos_banco:
                # Gerar scores para todos os candidatos Omie
                candidatos = []
                for lo in lancamentos_omie:
                    score = ml.predict_score(lb, lo)
                    candidatos.append((lo, score))

                # Ordenar por score
                candidatos.sort(key=lambda x: x[1], reverse=True)

                if not candidatos:
                    continue

                melhor_lo, melhor_score = candidatos[0]
                threshold = ml.threshold

                if melhor_score >= threshold:
                    # Auto-conciliar
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=melhor_lo.id,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="ok",
                        confidence_score=round(melhor_score, 4),
                        metodo="ml_auto",
                        obs=f"IA: conciliado com {melhor_score:.0%} de confiança",
                    ))
                elif melhor_score >= 0.70:
                    # Sugestão para revisão
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=melhor_lo.id,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="revisao_manual",
                        confidence_score=round(melhor_score, 4),
                        metodo="ml_sugestao",
                        obs=f"IA sugere match com {melhor_score:.0%} — confirme manualmente",
                    ))
                else:
                    # Muito baixa confiança — requer revisão manual completa
                    self.matches.append(Conciliacao(
                        lancamento_banco_id=lb.id,
                        lancamento_omie_id=None,
                        empresa_id=self.empresa_id,
                        data_referencia=data_ref,
                        status="revisao_manual",
                        confidence_score=round(melhor_score, 4),
                        metodo="ml_sugestao",
                        obs="IA: confiança baixa — requer revisão manual",
                    ))

        except Exception as e:
            logger.error("ml_fase2_erro", erro=str(e))
            # Fase 2 é best-effort — não falha a conciliação
