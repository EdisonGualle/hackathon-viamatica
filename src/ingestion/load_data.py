from __future__ import annotations

import json
import os
import sqlite3
import sys

import pandas as pd

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)
DB_PATH = os.path.normpath(os.path.join(ROOT_DIR, 'fraudia.db'))

from data.synthetic.generate_dataset import main as generate_dataset
from models.fraud_model import entrenar_y_guardar
from nlp.narrative_similarity import calcular_similitudes, guardar_similitudes
from rules.fraud_rules import CRITICAL_RULES, procesar_todos


def _parse_codes(raw: str) -> set[str]:
    try:
        values = json.loads(raw or '[]')
        return {str(value) for value in values}
    except Exception:
        return set()


def run_pipeline() -> pd.DataFrame:
    print('=' * 60)
    print('FRAUDIA CLAIMS - Pipeline de inicializacion')
    print('=' * 60)

    print('\n[1/4] Generando dataset sintético...')
    generate_dataset()

    print('\n[2/4] Ejecutando motor de reglas...')
    reglas_df = procesar_todos(DB_PATH)

    print('\n[3/4] Entrenando modelos ML...')
    model = entrenar_y_guardar(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        siniestros_df = pd.read_sql('SELECT * FROM siniestros', conn)
        polizas_df = pd.read_sql('SELECT * FROM polizas', conn)
    ml_df = model.predict(siniestros_df, polizas_df)

    print('\n[4/4] Calculando similitud de narrativas...')
    nlp_df, pares_df = calcular_similitudes(siniestros_df[['id_siniestro', 'descripcion']])
    guardar_similitudes(DB_PATH, nlp_df, pares_df)

    scores = reglas_df.merge(ml_df[['id_siniestro', 'score_ml']], on='id_siniestro', how='left')
    scores = scores.merge(nlp_df[['id_siniestro', 'score_nlp']], on='id_siniestro', how='left')
    scores['score_ml'] = scores['score_ml'].fillna(0).clip(0, 100)
    scores['score_nlp'] = scores['score_nlp'].fillna(0).clip(0, 100)

    scores['score_final'] = (
        0.45 * scores['score_reglas'] + 0.40 * scores['score_ml'] + 0.15 * scores['score_nlp']
    ).round(2).clip(0, 100)

    def nivel_final(row: pd.Series) -> str:
        if _parse_codes(row['reglas_activadas']) & CRITICAL_RULES:
            return 'ROJO'
        if row['score_final'] >= 76:
            return 'ROJO'
        if row['score_final'] >= 41:
            return 'AMARILLO'
        return 'VERDE'

    scores['nivel'] = scores.apply(nivel_final, axis=1)
    scores['explicacion'] = scores['explicacion_reglas']
    scores['confianza_ia'] = (0.7 * scores['score_final'] + 0.3 * scores['score_ml']).round(1).clip(0, 99)
    scores['fecha_calculo'] = pd.Timestamp.now().isoformat()

    final_df = scores[
        [
            'id_siniestro',
            'score_reglas',
            'score_ml',
            'score_nlp',
            'score_final',
            'nivel',
            'reglas_activadas',
            'detalle_reglas_json',
            'explicacion',
            'confianza_ia',
            'fecha_calculo',
        ]
    ].copy()

    with sqlite3.connect(DB_PATH) as conn:
        final_df.to_sql('scores_riesgo', conn, if_exists='replace', index=False)

    print('\nDistribución final:')
    print(final_df['nivel'].value_counts().to_string())
    print(f'Base de datos actualizada: {DB_PATH}')
    return final_df


if __name__ == '__main__':
    run_pipeline()
