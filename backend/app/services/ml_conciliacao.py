# backend/app/services/ml_conciliacao.py
# Módulo de Machine Learning para conciliação inteligente.
# Responsabilidades:
#   - Treino de RandomForestClassifier com cross-validation
#   - Feature engineering: valor, diferença, dias, empresa, sazonalidade, TF-IDF
#   - Predict: score 0.0–1.0 para cada par banco/omie
#   - Versionamento: salva .pkl + métricas em ml_model_versions
#   - Cold start: sem dados → retorna False
#
# DECISÃO TÉCNICA: O modelo usa features numéricas simples + TF-IDF da descrição.
# RandomForest foi escolhido por: (1) funciona bem com poucos dados, (2) não precisa
# de normalização, (3) feature importance interpretável, (4) robusto a outliers.

import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

import joblib
import numpy as np
import structlog
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.conciliacao import Conciliacao
from app.db.models.ml_model import MLModelVersion

logger = structlog.get_logger()

# Mínimo de amostras para treinar o modelo
MIN_AMOSTRAS_TREINO = 50


class MLConciliador:
    """Classificador ML para conciliação bancária."""

    def __init__(self):
        self.modelo: RandomForestClassifier | None = None
        self.tfidf: TfidfVectorizer | None = None
        self.threshold: float = 0.90

    async def carregar_modelo_ativo(self, db: AsyncSession) -> bool:
        """
        Carrega o modelo ativo do banco.
        Retorna True se carregou com sucesso, False se não há modelo.
        """
        result = await db.execute(
            select(MLModelVersion).where(MLModelVersion.is_active == True).limit(1)
        )
        versao = result.scalar_one_or_none()

        if versao is None:
            return False

        try:
            dados = joblib.load(versao.arquivo_path)
            self.modelo = dados["modelo"]
            self.tfidf = dados.get("tfidf")
            self.threshold = float(versao.threshold_auto)
            return True
        except Exception as e:
            logger.error("ml_carregar_erro", path=versao.arquivo_path, erro=str(e))
            return False

    def _extrair_features(self, lb, lo) -> np.ndarray:
        """Extrai features numéricas de um par banco/omie."""
        valor_banco = float(lb.valor) if isinstance(lb.valor, Decimal) else lb.valor
        valor_omie = float(lo.valor) if isinstance(lo.valor, Decimal) else lo.valor

        diff_abs = abs(valor_banco - valor_omie)
        diff_pct = diff_abs / max(valor_banco, 0.01) * 100
        diff_dias = abs((lb.data_lancamento - lo.data_lancamento).days)
        dia_semana = lb.data_lancamento.weekday()
        dia_mes = lb.data_lancamento.day

        features = [
            valor_banco,
            valor_omie,
            diff_abs,
            diff_pct,
            diff_dias,
            dia_semana,
            dia_mes,
        ]

        # TF-IDF similarity entre descrições
        if self.tfidf and lb.descricao and lo.descricao:
            try:
                tfidf_banco = self.tfidf.transform([lb.descricao or ""])
                tfidf_omie = self.tfidf.transform([lo.descricao or ""])
                similarity = (tfidf_banco * tfidf_omie.T).toarray()[0][0]
                features.append(similarity)
            except Exception:
                features.append(0.0)
        else:
            features.append(0.0)

        return np.array(features).reshape(1, -1)

    def predict_score(self, lb, lo) -> float:
        """Prediz score de match (0.0–1.0) para um par banco/omie."""
        if self.modelo is None:
            return 0.0

        features = self._extrair_features(lb, lo)
        proba = self.modelo.predict_proba(features)

        # Retorna probabilidade da classe positiva (match)
        if proba.shape[1] >= 2:
            return float(proba[0][1])
        return float(proba[0][0])

    @staticmethod
    async def treinar(db: AsyncSession, user_id: str | None = None) -> dict:
        """
        Treina novo modelo a partir dos dados históricos de conciliação.
        Salva .pkl e registra em ml_model_versions.
        Retorna métricas do treinamento.
        """
        settings = get_settings()

        # Buscar dados de treino: conciliações com status definido
        result = await db.execute(
            select(Conciliacao).where(
                Conciliacao.status.in_(["ok", "sem_correspondencia"]),
                Conciliacao.lancamento_banco_id.isnot(None),
            )
        )
        conciliacoes = result.scalars().all()

        if len(conciliacoes) < MIN_AMOSTRAS_TREINO:
            logger.warning(
                "ml_amostras_insuficientes",
                total=len(conciliacoes),
                minimo=MIN_AMOSTRAS_TREINO,
            )
            return {
                "sucesso": False,
                "motivo": f"Amostras insuficientes ({len(conciliacoes)}/{MIN_AMOSTRAS_TREINO})",
            }

        # Preparar features e labels
        X_list = []
        y_list = []
        descricoes = []

        for c in conciliacoes:
            lb = c.lancamento_banco
            lo = c.lancamento_omie
            if not lb:
                continue

            label = 1 if c.status == "ok" and lo else 0

            if lo:
                valor_b = float(lb.valor)
                valor_o = float(lo.valor)
                diff_abs = abs(valor_b - valor_o)
                diff_pct = diff_abs / max(valor_b, 0.01) * 100
                diff_dias = abs((lb.data_lancamento - lo.data_lancamento).days)
            else:
                valor_b = float(lb.valor)
                valor_o = 0.0
                diff_abs = valor_b
                diff_pct = 100.0
                diff_dias = 30

            features = [
                valor_b, valor_o, diff_abs, diff_pct, diff_dias,
                lb.data_lancamento.weekday(), lb.data_lancamento.day,
                0.0,  # TF-IDF placeholder (preenchido abaixo)
            ]

            X_list.append(features)
            y_list.append(label)
            descricoes.append((lb.descricao or "", lo.descricao or "" if lo else ""))

        X = np.array(X_list)
        y = np.array(y_list)

        # TF-IDF das descrições
        tfidf = TfidfVectorizer(max_features=500, stop_words=None)
        todos_textos = [d[0] + " " + d[1] for d in descricoes]

        if any(t.strip() for t in todos_textos):
            tfidf.fit(todos_textos)
            for i, (desc_b, desc_o) in enumerate(descricoes):
                if desc_b and desc_o:
                    try:
                        v1 = tfidf.transform([desc_b])
                        v2 = tfidf.transform([desc_o])
                        sim = (v1 * v2.T).toarray()[0][0]
                        X[i, -1] = sim
                    except Exception:
                        pass

        # Treinar modelo
        modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight="balanced",
        )

        # Cross-validation
        cv_scores = cross_val_score(modelo, X, y, cv=min(5, len(X) // 10 + 1), scoring="f1")

        # Treinar com todos os dados
        modelo.fit(X, y)
        y_pred = modelo.predict(X)

        precision = precision_score(y, y_pred, zero_division=0)
        recall = recall_score(y, y_pred, zero_division=0)
        f1 = f1_score(y, y_pred, zero_division=0)

        # Salvar modelo
        model_id = str(uuid.uuid4())
        models_dir = os.path.join(settings.RENDER_DISK_PATH, "models")
        os.makedirs(models_dir, exist_ok=True)
        path = os.path.join(models_dir, f"conciliacao_{model_id}.pkl")

        joblib.dump({"modelo": modelo, "tfidf": tfidf}, path)

        # Desativar modelo anterior
        result = await db.execute(
            select(MLModelVersion).where(MLModelVersion.is_active == True)
        )
        ativo = result.scalar_one_or_none()
        if ativo:
            ativo.is_active = False

        # Registrar nova versão
        versao = MLModelVersion(
            treinado_em=datetime.now(timezone.utc),
            precision_score=round(precision, 4),
            recall_score=round(recall, 4),
            f1_score=round(f1, 4),
            n_amostras_treino=len(X),
            n_amostras_validacao=0,
            arquivo_path=path,
            is_active=True,
            threshold_auto=0.90,
            treinado_por=uuid.UUID(user_id) if user_id else None,
            notas=f"CV F1 médio: {cv_scores.mean():.4f}",
        )
        db.add(versao)

        logger.info(
            "ml_treinamento_concluido",
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            amostras=len(X),
        )

        return {
            "sucesso": True,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "amostras": len(X),
            "cv_f1_mean": round(cv_scores.mean(), 4),
        }
