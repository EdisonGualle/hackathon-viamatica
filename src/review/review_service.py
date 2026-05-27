from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .audit_repository import bootstrap_case_reviews, ensure_review_tables


VALID_STATES = {
    'pendiente_revision',
    'revision_documental',
    'requiere_campo',
    'escalado_antifraude',
    'descartado',
    'caso_observado',
    'cerrado',
}


def initialize_review_state(db_path: str | Path) -> None:
    db_path = str(db_path)
    with sqlite3.connect(db_path) as conn:
        ensure_review_tables(conn)
        claims = pd.read_sql('SELECT id_siniestro FROM siniestros', conn)
        bootstrap_case_reviews(conn, claims['id_siniestro'].tolist())
        conn.commit()


def record_case_review(db_path: str | Path, id_siniestro: str, estado: str, comentario: str = '', actor: str = 'analista', decision_humana: str = '') -> None:
    if estado not in VALID_STATES:
        raise ValueError(f'Estado no soportado: {estado}')
    db_path = str(db_path)
    timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        ensure_review_tables(conn)
        conn.execute(
            '''
            INSERT INTO case_status_history (id_siniestro, estado, comentario, actor, fecha_evento)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (id_siniestro, estado, comentario, actor, timestamp),
        )
        conn.execute(
            '''
            INSERT INTO case_reviews (id_siniestro, estado_actual, decision_humana, comentario, revisado_por, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id_siniestro) DO UPDATE SET
                estado_actual=excluded.estado_actual,
                decision_humana=excluded.decision_humana,
                comentario=excluded.comentario,
                revisado_por=excluded.revisado_por,
                fecha_actualizacion=excluded.fecha_actualizacion
            ''',
            (id_siniestro, estado, decision_humana, comentario, actor, timestamp),
        )
        conn.commit()


def generate_audit_report(db_path: str | Path, id_siniestro: str, generated_by: str = 'sistema') -> str:
    db_path = str(db_path)
    with sqlite3.connect(db_path) as conn:
        claim = pd.read_sql('SELECT * FROM siniestros WHERE id_siniestro = ?', conn, params=(id_siniestro,))
        score = pd.read_sql('SELECT * FROM scores_riesgo WHERE id_siniestro = ?', conn, params=(id_siniestro,))
        explain = pd.read_sql('SELECT * FROM case_explainability WHERE id_siniestro = ?', conn, params=(id_siniestro,))
        review = pd.read_sql('SELECT * FROM case_reviews WHERE id_siniestro = ?', conn, params=(id_siniestro,))
        history = pd.read_sql('SELECT * FROM case_status_history WHERE id_siniestro = ? ORDER BY fecha_evento', conn, params=(id_siniestro,))
    if claim.empty or score.empty:
        raise ValueError(f'No existe información suficiente para {id_siniestro}')

    claim_row = claim.iloc[0].to_dict()
    score_row = score.iloc[0].to_dict()
    explain_row = explain.iloc[0].to_dict() if not explain.empty else {}
    review_row = review.iloc[0].to_dict() if not review.empty else {'estado_actual': 'pendiente_revision'}

    history_text = history[['estado', 'comentario', 'actor', 'fecha_evento']].to_string(index=False) if not history.empty else 'Sin historial.'

    report = f"""# Reporte de Auditoría - {id_siniestro}

## Resultado
- Nivel: {score_row.get('nivel')}
- Score final: {score_row.get('score_final')}
- Confianza IA: {score_row.get('confianza_ia')}
- Estado humano: {review_row.get('estado_actual')}

## Hechos del caso
- Ramo: {claim_row.get('ramo')}
- Cobertura: {claim_row.get('cobertura')}
- Proveedor: {claim_row.get('id_proveedor')}
- Monto reclamado: {claim_row.get('monto_reclamado')}

## Explicación auditable
{explain_row.get('explicacion_auditable', score_row.get('explicacion', 'Sin explicación disponible.'))}

## Reason codes
{explain_row.get('reason_codes_json', '[]')}

## Historial de revisión
{history_text}

## Nota ética
El sistema prioriza revisión humana y no emite una acusación automática.
"""

    with sqlite3.connect(db_path) as conn:
        ensure_review_tables(conn)
        conn.execute(
            'INSERT INTO audit_reports (id_siniestro, reporte_markdown, generado_por, fecha_generacion) VALUES (?, ?, ?, ?)',
            (id_siniestro, report, generated_by, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return report
