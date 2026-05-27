from __future__ import annotations

import json


def build_audit_trail(claim_row: dict, score_row: dict, document_rows: list[dict], evidence_bundle: list[dict]) -> dict:
    try:
        scoring_breakdown = json.loads(score_row.get('scoring_breakdown_json') or '{}')
    except Exception:
        scoring_breakdown = {}
    return {
        'id_siniestro': claim_row.get('id_siniestro'),
        'fecha_calculo': score_row.get('fecha_calculo'),
        'versions': {
            'rules_version': 'canonical-2026-05-27',
            'scoring_version': 'scoring-core-v1',
            'document_ai_version': 'document-ai-v1',
            'explainability_version': 'explainability-v1',
        },
        'modules': ['rules', 'models', 'nlp', 'scoring', 'document_ai'],
        'inputs': {
            'id_poliza': claim_row.get('id_poliza'),
            'id_proveedor': claim_row.get('id_proveedor'),
            'documentos_analizados': len(document_rows),
        },
        'scores': {
            'score_reglas': score_row.get('score_reglas'),
            'score_ml': score_row.get('score_ml'),
            'score_nlp': score_row.get('score_nlp'),
            'score_final': score_row.get('score_final'),
            'nivel': score_row.get('nivel'),
        },
        'breakdown': scoring_breakdown,
        'evidence_count': len(evidence_bundle),
    }
