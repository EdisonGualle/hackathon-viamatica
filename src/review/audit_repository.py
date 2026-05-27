from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def ensure_review_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS case_reviews (
            id_siniestro TEXT PRIMARY KEY,
            estado_actual TEXT NOT NULL,
            decision_humana TEXT,
            comentario TEXT,
            revisado_por TEXT,
            fecha_actualizacion TEXT NOT NULL
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS case_status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_siniestro TEXT NOT NULL,
            estado TEXT NOT NULL,
            comentario TEXT,
            actor TEXT,
            fecha_evento TEXT NOT NULL
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS audit_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_siniestro TEXT NOT NULL,
            reporte_markdown TEXT NOT NULL,
            generado_por TEXT NOT NULL,
            fecha_generacion TEXT NOT NULL
        )
        '''
    )


def bootstrap_case_reviews(conn: sqlite3.Connection, claim_ids: list[str]) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    for claim_id in claim_ids:
        conn.execute(
            '''
            INSERT OR IGNORE INTO case_reviews (
                id_siniestro, estado_actual, decision_humana, comentario, revisado_por, fecha_actualizacion
            ) VALUES (?, 'pendiente_revision', '', '', 'sistema', ?)
            ''',
            (claim_id, timestamp),
        )
        exists = conn.execute(
            'SELECT 1 FROM case_status_history WHERE id_siniestro = ? AND estado = ? LIMIT 1',
            (claim_id, 'pendiente_revision'),
        ).fetchone()
        if not exists:
            conn.execute(
                '''
                INSERT INTO case_status_history (id_siniestro, estado, comentario, actor, fecha_evento)
                VALUES (?, 'pendiente_revision', 'Estado inicial generado por pipeline.', 'sistema', ?)
                ''',
                (claim_id, timestamp),
            )
