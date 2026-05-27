from __future__ import annotations

from ._db import query_df


def find_related_claim_network(id_siniestro: str) -> list[dict]:
    df = query_df(
        '''
        SELECT s2.id_siniestro, s2.id_proveedor, s2.id_asegurado, sr.score_final, sr.nivel
        FROM siniestros s1
        JOIN siniestros s2 ON s1.id_proveedor = s2.id_proveedor AND s1.id_siniestro <> s2.id_siniestro
        JOIN scores_riesgo sr ON sr.id_siniestro = s2.id_siniestro
        WHERE s1.id_siniestro = ?
        ORDER BY sr.score_final DESC
        LIMIT 15
        ''',
        (id_siniestro,),
    )
    return df.to_dict('records')
