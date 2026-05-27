from __future__ import annotations

from ._db import query_df


def get_provider_risk_profile(id_proveedor: str) -> dict:
    df = query_df(
        '''
        SELECT s.id_proveedor, COUNT(*) AS total_casos,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.id_proveedor = ?
        GROUP BY s.id_proveedor
        ''',
        (id_proveedor,),
    )
    return df.iloc[0].to_dict() if not df.empty else {}
