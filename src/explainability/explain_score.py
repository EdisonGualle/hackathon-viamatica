from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from .audit_trail import build_audit_trail
from .counterfactuals import build_counterfactuals
from .evidence_builder import build_evidence_bundle


def build_case_explainability(claim_row: dict, score_row: dict, document_rows: list[dict]) -> dict:
    evidence_bundle = build_evidence_bundle(claim_row, score_row, document_rows)
    reason_codes = []
    try:
        reason_codes = json.loads(score_row.get('reglas_activadas') or '[]')
    except Exception:
        reason_codes = []
    reason_codes.extend(item.get('code') for item in evidence_bundle if item.get('source') == 'document_ai')
    seen = set()
    reason_codes = [code for code in reason_codes if code and not (code in seen or seen.add(code))]
    counterfactuals = build_counterfactuals(score_row, evidence_bundle)
    audit_trail = build_audit_trail(claim_row, score_row, document_rows, evidence_bundle)
    return {
        'id_siniestro': claim_row['id_siniestro'],
        'reason_codes_json': json.dumps(reason_codes, ensure_ascii=False),
        'evidence_bundle_json': json.dumps(evidence_bundle, ensure_ascii=False),
        'counterfactual_json': json.dumps(counterfactuals, ensure_ascii=False),
        'audit_trail_json': json.dumps(audit_trail, ensure_ascii=False),
        'explicacion_auditable': _build_explanation_text(score_row, evidence_bundle, counterfactuals),
    }


def _build_explanation_text(score_row: dict, evidence_bundle: list[dict], counterfactuals: list[str]) -> str:
    top_evidence = '; '.join(item['detail'] for item in evidence_bundle[:3] if item.get('detail'))
    explanation = (
        f"Nivel {score_row.get('nivel')} con score {score_row.get('score_final')}. "
        f"La priorización se sostiene en: {top_evidence or 'sin evidencia consolidada adicional'}."
    )
    if counterfactuals:
        explanation += ' Contrafactual: ' + ' '.join(counterfactuals)
    return explanation


def run_explainability_pipeline(db_path: str | Path) -> pd.DataFrame:
    db_path = str(db_path)
    with sqlite3.connect(db_path) as conn:
        claims_df = pd.read_sql('SELECT * FROM siniestros', conn)
        scores_df = pd.read_sql('SELECT * FROM scores_riesgo', conn)
        doc_ai_df = pd.read_sql('SELECT * FROM document_ai_results', conn)

    records = []
    for _, claim_row in claims_df.iterrows():
        score_match = scores_df[scores_df['id_siniestro'] == claim_row['id_siniestro']]
        if score_match.empty:
            continue
        score_row = score_match.iloc[0].to_dict()
        document_rows = doc_ai_df[doc_ai_df['id_siniestro'] == claim_row['id_siniestro']].to_dict('records')
        records.append(build_case_explainability(claim_row.to_dict(), score_row, document_rows))

    explain_df = pd.DataFrame(records)
    with sqlite3.connect(db_path) as conn:
        explain_df.to_sql('case_explainability', conn, if_exists='replace', index=False)
    return explain_df
