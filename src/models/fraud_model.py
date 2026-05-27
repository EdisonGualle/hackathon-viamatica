"""
Modelos de ML para detección de fraude:
- Isolation Forest (anomalías, no supervisado)
- XGBoost (clasificación supervisada con etiqueta simulada)
Combina ambos scores en un score_ml ponderado.
"""
import json
import os
import pickle
import sqlite3

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    XGBOOST_AVAILABLE = False

FEATURES = [
    "dias_inicio_poliza",
    "dias_fin_poliza",
    "dias_ocurr_reporte",
    "historial_siniestros",
    "documentos_completos",
    "monto_reclamado",
    "monto_estimado",
    "ratio_monto_estimado",   # calculada
    "es_robo",                # calculada
    "es_vehiculos",           # calculada
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


def _build_features(siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame) -> pd.DataFrame:
    df = siniestros_df.copy()
    pol = polizas_df[["id_poliza", "suma_asegurada"]].copy()
    df = df.merge(pol, on="id_poliza", how="left")

    df["ratio_monto_estimado"] = np.where(
        df["monto_estimado"] > 0,
        df["monto_reclamado"] / df["monto_estimado"],
        1.0
    )
    df["ratio_suma_asegurada"] = np.where(
        df["suma_asegurada"] > 0,
        df["monto_reclamado"] / df["suma_asegurada"],
        0.0
    )
    df["es_robo"] = df["cobertura"].str.lower().str.contains("robo").astype(int)
    df["es_vehiculos"] = df["ramo"].str.lower().str.contains("vehiculos").astype(int)
    df["dias_inicio_poliza"] = df["dias_inicio_poliza"].clip(0, 365)
    df["dias_fin_poliza"] = df["dias_fin_poliza"].clip(0, 365)
    df["dias_ocurr_reporte"] = df["dias_ocurr_reporte"].clip(0, 60)

    return df


class FraudModel:
    def __init__(self):
        self.iso_forest = None
        self.classifier = None
        self.scaler = StandardScaler()
        self.trained = False

    def train(self, siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame):
        df = _build_features(siniestros_df, polizas_df)
        feats_cols = [c for c in FEATURES if c in df.columns]
        X = df[feats_cols].fillna(0).values
        y = df["etiqueta_fraude"].values

        X_scaled = self.scaler.fit_transform(X)

        # Isolation Forest (no supervisado)
        self.iso_forest = IsolationForest(
            n_estimators=200,
            contamination=0.2,
            random_state=42,
        )
        self.iso_forest.fit(X_scaled)

        # Clasificador supervisado
        if XGBOOST_AVAILABLE:
            self.classifier = XGBClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                scale_pos_weight=4,
                eval_metric="logloss",
                random_state=42,
            )
        else:
            self.classifier = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
            )
        self.classifier.fit(X_scaled, y)
        self.trained = True
        self.feats_cols = feats_cols
        print(f"Modelo entrenado con {len(X)} siniestros. Features: {feats_cols}")

    def predict(self, siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame) -> pd.DataFrame:
        df = _build_features(siniestros_df, polizas_df)
        X = df[self.feats_cols].fillna(0).values
        X_scaled = self.scaler.transform(X)

        # Isolation Forest: anomaly score normalizado a [0, 100]
        iso_scores = self.iso_forest.score_samples(X_scaled)
        iso_min, iso_max = iso_scores.min(), iso_scores.max()
        iso_norm = 100 * (1 - (iso_scores - iso_min) / (iso_max - iso_min + 1e-9))

        # Clasificador: probabilidad de fraude → [0, 100]
        clf_proba = self.classifier.predict_proba(X_scaled)[:, 1] * 100

        # Score ML ponderado: 40% isolation + 60% classifier
        score_ml = 0.40 * iso_norm + 0.60 * clf_proba

        resultado = pd.DataFrame({
            "id_siniestro": df["id_siniestro"].values,
            "score_ml": np.round(score_ml, 2),
            "score_iso_forest": np.round(iso_norm, 2),
            "score_classifier": np.round(clf_proba, 2),
        })
        return resultado

    def save(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(os.path.join(MODEL_DIR, "fraud_model.pkl"), "wb") as f:
            pickle.dump(self, f)
        print(f"Modelo guardado en {MODEL_DIR}/fraud_model.pkl")

    @classmethod
    def load(cls) -> "FraudModel":
        path = os.path.join(MODEL_DIR, "fraud_model.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError("Modelo no encontrado. Ejecuta primero el pipeline.")
        with open(path, "rb") as f:
            return pickle.load(f)


def entrenar_y_guardar(db_path: str):
    conn = sqlite3.connect(db_path)
    siniestros_df = pd.read_sql("SELECT * FROM siniestros", conn)
    polizas_df = pd.read_sql("SELECT * FROM polizas", conn)
    conn.close()

    model = FraudModel()
    model.train(siniestros_df, polizas_df)
    model.save()
    return model


if __name__ == "__main__":
    db_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "fraudia.db")
    )
    model = entrenar_y_guardar(db_path)
    conn = sqlite3.connect(db_path)
    sins = pd.read_sql("SELECT * FROM siniestros LIMIT 5", conn)
    pols = pd.read_sql("SELECT * FROM polizas", conn)
    conn.close()
    preds = model.predict(sins, pols)
    print(preds)
