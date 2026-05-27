from __future__ import annotations

import json

from .reason_codes import reason_label


def build_evidence_bundle(claim_row: dict, score_row: dict, document_rows: list[dict]) -> list[dict]:
    bundle: list[dict] = []
    try:
        rule_details = json.loads(score_row.get('detalle_reglas_json') or '[]')
    except Exception:
        rule_details = []

    for item in rule_details:
        bundle.append(
            {
                'source': 'rules',
                'code': item.get('codigo'),
                'label': reason_label(item.get('codigo', '')),
                'severity': 'ALTA' if item.get('codigo', '').startswith('RF-0') and item.get('codigo') in {'RF-01', 'RF-02', 'RF-03', 'RF-04'} else 'MEDIA',
                'detail': item.get('evidencia') or item.get('explicacion'),
                'variable': item.get('variable_principal'),
            }
        )

    for row in document_rows:
        try:
            alerts = json.loads(row.get('inconsistencias_json') or '[]')
        except Exception:
            alerts = []
        for alert in alerts:
            bundle.append(
                {
                    'source': 'document_ai',
                    'code': alert.get('codigo'),
                    'label': reason_label(alert.get('codigo', '')),
                    'severity': alert.get('severidad', 'MEDIA'),
                    'detail': alert.get('descripcion'),
                    'document_id': row.get('id_documento'),
                }
            )

    if score_row.get('score_ml', 0) >= 70:
        bundle.append(
            {
                'source': 'ml',
                'code': 'ML-ALTO',
                'label': 'Score ML elevado',
                'severity': 'MEDIA',
                'detail': f"El componente ML aporta {score_row.get('score_ml')} puntos de 100.",
            }
        )
    if score_row.get('score_nlp', 0) >= 70:
        bundle.append(
            {
                'source': 'nlp',
                'code': 'NLP-ALTO',
                'label': 'Similitud narrativa elevada',
                'severity': 'MEDIA',
                'detail': f"El componente NLP aporta {score_row.get('score_nlp')} puntos de 100.",
            }
        )
    return bundle
