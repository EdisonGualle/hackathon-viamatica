from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from rag.loader import load_markdown_documents


def build_case_documents(db_path: str | Path, id_siniestro: str) -> list[dict]:
    with sqlite3.connect(db_path) as conn:
        explain = conn.execute('SELECT explicacion_auditable, evidence_bundle_json FROM case_explainability WHERE id_siniestro = ?', (id_siniestro,)).fetchone()
        docs = conn.execute('SELECT id_documento, inconsistencias_json, campos_extraidos_json FROM document_ai_results WHERE id_siniestro = ?', (id_siniestro,)).fetchall()
    documents = []
    if explain:
        documents.append(
            {
                'document_id': f'{id_siniestro}-explainability',
                'document_version': '2026-05-27',
                'source_type': 'case_explainability',
                'path': f'case://{id_siniestro}/explainability',
                'text': f"{explain[0]}\nEvidencia: {explain[1]}",
            }
        )
    for doc_id, inconsistencias_json, campos_json in docs:
        documents.append(
            {
                'document_id': doc_id,
                'document_version': '2026-05-27',
                'source_type': 'case_document',
                'path': f'case://{id_siniestro}/{doc_id}',
                'text': f"Campos: {campos_json}\nInconsistencias: {inconsistencias_json}",
            }
        )
    return documents


def build_knowledge_corpus(kb_root: str | Path) -> list[dict]:
    return load_markdown_documents(kb_root)
