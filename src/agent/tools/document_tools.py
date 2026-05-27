from __future__ import annotations

import json

from ._db import query_df


def get_document_analysis(id_siniestro: str) -> dict:
    docs = query_df('SELECT * FROM document_ai_results WHERE id_siniestro = ?', (id_siniestro,))
    if docs.empty:
        return {'id_siniestro': id_siniestro, 'documentos': [], 'resumen': 'Sin análisis documental.'}
    total_score = float(docs['document_score'].sum())
    alerts = []
    for _, row in docs.iterrows():
        try:
            inconsistencias = json.loads(row['inconsistencias_json'] or '[]')
        except Exception:
            inconsistencias = []
        if inconsistencias:
            alerts.append({'id_documento': row['id_documento'], 'tipo': row['tipo_detectado'], 'inconsistencias': inconsistencias})
    return {
        'id_siniestro': id_siniestro,
        'document_score_total': round(total_score, 2),
        'documentos': docs.to_dict('records'),
        'alertas_documentales': alerts,
        'resumen': f'{len(alerts)} documento(s) con alertas documentales.' if alerts else 'Sin alertas documentales relevantes.',
    }
