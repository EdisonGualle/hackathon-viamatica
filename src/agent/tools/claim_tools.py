from __future__ import annotations

import json

from ._db import query_df


def get_claim_detail(id_siniestro: str) -> dict:
    df = query_df(
        '''
        SELECT s.*, sr.score_reglas, sr.score_ml, sr.score_nlp, sr.score_final, sr.nivel,
               sr.reglas_activadas, sr.detalle_reglas_json, sr.explicacion, sr.confianza_ia,
               ce.explicacion_auditable, ce.reason_codes_json
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        LEFT JOIN case_explainability ce ON ce.id_siniestro = s.id_siniestro
        WHERE s.id_siniestro = ?
        ''',
        (id_siniestro,),
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def compare_claim_with_policy(id_siniestro: str) -> dict:
    df = query_df(
        '''
        SELECT s.id_siniestro, s.monto_reclamado, p.suma_asegurada, p.cobertura, p.ramo,
               ROUND(100.0 * s.monto_reclamado / p.suma_asegurada, 1) AS pct_suma
        FROM siniestros s
        JOIN polizas p ON p.id_poliza = s.id_poliza
        WHERE s.id_siniestro = ?
        ''',
        (id_siniestro,),
    )
    return df.iloc[0].to_dict() if not df.empty else {}


def find_similar_narratives(id_siniestro: str) -> list[dict]:
    df = query_df(
        '''
        SELECT * FROM pares_similares
        WHERE id_siniestro_a = ? OR id_siniestro_b = ?
        ORDER BY similitud DESC
        LIMIT 10
        ''',
        (id_siniestro, id_siniestro),
    )
    return df.to_dict('records')
