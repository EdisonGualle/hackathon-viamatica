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
from document_ai import run_document_ai_pipeline
from explainability import run_explainability_pipeline
from models.fraud_model import entrenar_y_guardar
from nlp.narrative_similarity import calcular_similitudes, guardar_similitudes
from review import initialize_review_state
from rules.fraud_rules import CRITICAL_RULES, procesar_todos
from scoring import ComponentScores, compute_assessment


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

    print('\n[1/7] Generando dataset sintético...')
    generate_dataset()

    print('\n[2/7] Analizando documentos sintéticos...')
    document_ai_df = run_document_ai_pipeline(DB_PATH)
    print(f'Documentos analizados: {len(document_ai_df)}')

    print('\n[3/7] Ejecutando motor de reglas...')
    reglas_df = procesar_todos(DB_PATH)

    print('\n[4/7] Entrenando modelos ML...')
    model = entrenar_y_guardar(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        siniestros_df = pd.read_sql('SELECT * FROM siniestros', conn)
        polizas_df = pd.read_sql('SELECT * FROM polizas', conn)
    ml_df = model.predict(siniestros_df, polizas_df)

    print('\n[5/7] Calculando similitud de narrativas...')
    nlp_df, pares_df = calcular_similitudes(siniestros_df[['id_siniestro', 'descripcion']])
    guardar_similitudes(DB_PATH, nlp_df, pares_df)

    scores = reglas_df.merge(ml_df[['id_siniestro', 'score_ml']], on='id_siniestro', how='left')
    scores = scores.merge(nlp_df[['id_siniestro', 'score_nlp']], on='id_siniestro', how='left')
    scores['score_ml'] = scores['score_ml'].fillna(0).clip(0, 100)
    scores['score_nlp'] = scores['score_nlp'].fillna(0).clip(0, 100)

    def _assessment_for_row(row: pd.Series):
        active_rules = _parse_codes(row['reglas_activadas'])
        return compute_assessment(
            ComponentScores(
                score_reglas=row['score_reglas'],
                score_ml=row['score_ml'],
                score_nlp=row['score_nlp'],
            ),
            active_rules=active_rules & CRITICAL_RULES if active_rules & CRITICAL_RULES else active_rules,
            metadata={'id_siniestro': row['id_siniestro'], 'mode': 'pipeline'},
        )

    assessments = scores.apply(_assessment_for_row, axis=1)
    scores['score_final'] = assessments.map(lambda assessment: assessment.score_final)
    scores['nivel'] = assessments.map(lambda assessment: assessment.nivel_final)
    scores['explicacion'] = scores['explicacion_reglas']
    scores['confianza_ia'] = assessments.map(lambda assessment: assessment.confianza_ia)
    scores['scoring_breakdown_json'] = assessments.map(
        lambda assessment: json.dumps(
            {
                'weights': assessment.breakdown.weights,
                'weighted_components': assessment.breakdown.weighted_components,
                'raw_components': assessment.breakdown.raw_components,
                'critical_rules_triggered': assessment.breakdown.critical_rules_triggered,
                'critical_override': assessment.critical_override,
                'action': assessment.action,
            },
            ensure_ascii=False,
        )
    )
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
            'scoring_breakdown_json',
            'fecha_calculo',
        ]
    ].copy()

    with sqlite3.connect(DB_PATH) as conn:
        final_df.to_sql('scores_riesgo', conn, if_exists='replace', index=False)

    print('\n[6/7] Construyendo explainability auditable...')
    explain_df = run_explainability_pipeline(DB_PATH)
    print(f'Casos explicados: {len(explain_df)}')

    print('\n[7/7] Inicializando revisión humana...')
    initialize_review_state(DB_PATH)

    print('\nDistribución final:')
    print(final_df['nivel'].value_counts().to_string())
    print(f'Base de datos actualizada: {DB_PATH}')
    return final_df


if __name__ == '__main__':
    run_pipeline()
