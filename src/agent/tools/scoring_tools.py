from __future__ import annotations

import json

from ._db import query_df


def get_score_breakdown(id_siniestro: str) -> dict:
    df = query_df('SELECT * FROM scores_riesgo WHERE id_siniestro = ?', (id_siniestro,))
    if df.empty:
        return {}
    row = df.iloc[0].to_dict()
    try:
        row['scoring_breakdown'] = json.loads(row.get('scoring_breakdown_json') or '{}')
    except Exception:
        row['scoring_breakdown'] = {}
    return row


def run_new_claim_score(payload: dict) -> dict:
    from scoring import score_simulated_claim

    return score_simulated_claim(
        score_reglas=payload.get('score_reglas', 0),
        score_ml=payload.get('score_ml', 0),
        score_nlp=payload.get('score_nlp', 0),
        active_rules=payload.get('active_rules', []),
        factores=payload.get('factores', []),
        ratio_pct=payload.get('ratio_pct'),
        rule_details=payload.get('rule_details', []),
    )
