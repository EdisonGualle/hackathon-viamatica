from __future__ import annotations

import json
import os
import pickle
import sqlite3
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
MODEL_PATH = os.path.join(MODEL_DIR, 'fraud_model.pkl')
METRICS_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'metricas_modelo.md')
FEATURES = [
    'dias_inicio_poliza',
    'dias_fin_poliza',
    'dias_ocurr_reporte',
    'historial_siniestros',
    'historial_vehiculo_18m',
    'historial_conductor_18m',
    'documentos_completos',
    'solo_rc_recurrente',
    'sin_tercero_identificado',
    'cambio_reciente_datos_asegurado',
    'ratio_suma_asegurada',
    'es_ptxrb',
    'es_rc',
]


@dataclass
class FraudModel:
    scaler: StandardScaler
    iso_forest: IsolationForest
    classifier: RandomForestClassifier
    feature_names: list[str]
    metrics: dict

    def predict(self, siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame) -> pd.DataFrame:
        features = build_features(siniestros_df, polizas_df, fit_schema=self.feature_names)
        x = self.scaler.transform(features[self.feature_names].fillna(0))

        iso_raw = -self.iso_forest.score_samples(x)
        iso_norm = minmax_0_100(iso_raw)
        clf_prob = self.classifier.predict_proba(x)[:, 1] * 100
        score_ml = np.round(0.45 * iso_norm + 0.55 * clf_prob, 2)

        return pd.DataFrame(
            {
                'id_siniestro': siniestros_df['id_siniestro'].values,
                'score_ml': score_ml,
                'score_iso_forest': np.round(iso_norm, 2),
                'score_classifier': np.round(clf_prob, 2),
            }
        )

    def save(self) -> None:
        os.makedirs(MODEL_DIR, exist_ok=True)
        with open(MODEL_PATH, 'wb') as handle:
            pickle.dump(self, handle)

    @classmethod
    def load(cls) -> 'FraudModel':
        with open(MODEL_PATH, 'rb') as handle:
            return pickle.load(handle)


def minmax_0_100(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    low = values.min()
    high = values.max()
    if np.isclose(low, high):
        return np.full_like(values, 50.0, dtype=float)
    return 100 * (values - low) / (high - low)


def build_features(siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame, fit_schema: list[str] | None = None) -> pd.DataFrame:
    df = siniestros_df.copy()
    policy_cols = polizas_df[['id_poliza', 'suma_asegurada']].copy()
    df = df.merge(policy_cols, on='id_poliza', how='left')
    df['ratio_suma_asegurada'] = np.where(df['suma_asegurada'] > 0, df['monto_reclamado'] / df['suma_asegurada'], 0.0)
    df['es_ptxrb'] = (df['cobertura'].fillna('').str.lower() == 'ptxrb').astype(int)
    df['es_rc'] = (df['cobertura'].fillna('').str.lower() == 'rc').astype(int)

    for col in FEATURES:
        if col not in df.columns:
            df[col] = 0

    schema = fit_schema or FEATURES
    return df[['id_siniestro'] + schema]


def build_labels(siniestros_df: pd.DataFrame) -> pd.Series:
    desc = siniestros_df['descripcion'].fillna('').str.lower()
    rule_like = (
        (siniestros_df['cobertura'].fillna('').str.lower() == 'ptxrb')
        | (siniestros_df['dias_ocurr_reporte'].fillna(0) > 4)
        | (siniestros_df['historial_siniestros'].fillna(0) >= 3)
        | (siniestros_df['historial_vehiculo_18m'].fillna(0) >= 3)
        | (siniestros_df['historial_conductor_18m'].fillna(0) >= 3)
        | (siniestros_df['monto_reclamado'].fillna(0) >= siniestros_df.get('monto_reclamado', 0).quantile(0.9))
        | desc.str.contains('imposible|inconsistenc|sin rastro|abandona', regex=True)
    )
    return rule_like.astype(int)


def train_model(siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame) -> FraudModel:
    labels = build_labels(siniestros_df)
    features = build_features(siniestros_df, polizas_df)
    x = features[FEATURES].fillna(0)
    y = labels.values

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y if len(set(y)) > 1 else None
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    iso = IsolationForest(n_estimators=200, contamination=0.18, random_state=42)
    iso.fit(x_train_scaled)

    clf = RandomForestClassifier(n_estimators=250, max_depth=8, min_samples_leaf=2, random_state=42, class_weight='balanced')
    clf.fit(x_train_scaled, y_train)

    test_prob = clf.predict_proba(x_test_scaled)[:, 1]
    test_pred = (test_prob >= 0.5).astype(int)
    metrics = {
        'train_size': int(len(x_train)),
        'test_size': int(len(x_test)),
        'holdout_accuracy': round(float(accuracy_score(y_test, test_pred)), 4),
        'holdout_auc': round(float(roc_auc_score(y_test, test_prob)) if len(set(y_test)) > 1 else 0.5, 4),
        'positive_rate': round(float(y.mean()), 4),
        'feature_names': FEATURES,
    }

    model = FraudModel(scaler=scaler, iso_forest=iso, classifier=clf, feature_names=FEATURES, metrics=metrics)
    model.save()
    write_metrics(metrics)
    return model


def write_metrics(metrics: dict) -> None:
    content = f"""# Metricas del Modelo\n\nFecha: 2026-05-27\n\n## Resumen\n- Train size: `{metrics['train_size']}`\n- Test size: `{metrics['test_size']}`\n- Holdout accuracy: `{metrics['holdout_accuracy']}`\n- Holdout AUC: `{metrics['holdout_auc']}`\n- Positive rate sintetica: `{metrics['positive_rate']}`\n\n## Notas\n- El modelo ML es auxiliar al score y no sustituye las reglas críticas.\n- La evaluación usa `train/test split` separado.\n- Los resultados son defendibles para MVP, pero limitados por datos sintéticos.\n"""
    with open(METRICS_PATH, 'w', encoding='utf-8') as handle:
        handle.write(content)


def entrenar_y_guardar(db_path: str) -> FraudModel:
    with sqlite3.connect(db_path) as conn:
        siniestros_df = pd.read_sql('SELECT * FROM siniestros', conn)
        polizas_df = pd.read_sql('SELECT * FROM polizas', conn)
    return train_model(siniestros_df, polizas_df)


if __name__ == '__main__':
    db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fraudia.db'))
    model = entrenar_y_guardar(db_path)
    print(json.dumps(model.metrics, indent=2))
