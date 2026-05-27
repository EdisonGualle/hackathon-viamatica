from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from .consistency_checker import check_document_consistency
from .document_classifier import classify_document
from .generic_parser import parse_generic_document
from .invoice_analyzer import analyze_invoice
from .ocr import estimate_legibility, extract_text
from .police_report_analyzer import analyze_police_report
from .schemas import ClaimDocumentAssessment, DocumentAnalysisResult, DocumentFieldSet


def _analyze_fields(document_type: str, document_row: dict, text: str) -> DocumentFieldSet:
    if document_type == 'factura_taller':
        return analyze_invoice(text)
    if document_type == 'parte_policial':
        return analyze_police_report(text)
    return parse_generic_document(document_type, document_row)


def analyze_document(document_row: dict, claim_row: dict) -> DocumentAnalysisResult:
    text = extract_text(document_row)
    present = bool(int(document_row.get('presente', 0) or 0))
    document_type = classify_document(document_row, text)
    fields = _analyze_fields(document_type, document_row, text)
    legibility_score = estimate_legibility(document_row, text)
    inconsistencies, document_score, recommendation = check_document_consistency(
        claim_row=claim_row,
        document_type=document_type,
        fields=fields,
        legibility_score=legibility_score,
        presente=present,
    )
    return DocumentAnalysisResult(
        id_documento=str(document_row['id_documento']),
        id_siniestro=str(document_row['id_siniestro']),
        tipo_detectado=document_type,
        legibilidad_score=legibility_score,
        presente=present,
        campos_extraidos=fields,
        inconsistencias=inconsistencies,
        document_score=document_score,
        recomendacion=recommendation,
        metadata={
            'file_path': document_row.get('file_path'),
            'ocr_chars': len(text),
        },
    )


def analyze_claim_documents(id_siniestro: str, db_path: str | Path) -> ClaimDocumentAssessment:
    with sqlite3.connect(db_path) as conn:
        docs_df = pd.read_sql('SELECT * FROM documentos WHERE id_siniestro = ?', conn, params=(id_siniestro,))
        claim_df = pd.read_sql('SELECT * FROM siniestros WHERE id_siniestro = ?', conn, params=(id_siniestro,))
    if claim_df.empty:
        raise ValueError(f'No existe siniestro {id_siniestro}')
    claim_row = claim_df.iloc[0].to_dict()
    results = [analyze_document(row._asdict() if hasattr(row, '_asdict') else row.to_dict(), claim_row) for _, row in docs_df.iterrows()]
    inconsistencies = [item for result in results for item in result.inconsistencias]
    document_score = min(sum(result.document_score for result in results), 100.0)
    return ClaimDocumentAssessment(
        id_siniestro=id_siniestro,
        document_score=document_score,
        documentos_analizados=len(results),
        documentos_con_alerta=sum(1 for result in results if result.inconsistencias),
        inconsistencias=inconsistencies,
        resultados=results,
    )


def run_document_ai_pipeline(db_path: str | Path) -> pd.DataFrame:
    db_path = str(db_path)
    with sqlite3.connect(db_path) as conn:
        docs_df = pd.read_sql('SELECT * FROM documentos', conn)
        claims_df = pd.read_sql('SELECT * FROM siniestros', conn)

    claim_map = {row['id_siniestro']: row.to_dict() for _, row in claims_df.iterrows()}
    results = []
    for _, row in docs_df.iterrows():
        claim_row = claim_map[row['id_siniestro']]
        result = analyze_document(row.to_dict(), claim_row)
        results.append(
            {
                'id_documento': result.id_documento,
                'id_siniestro': result.id_siniestro,
                'tipo_detectado': result.tipo_detectado,
                'legibilidad_score': round(result.legibilidad_score, 3),
                'presente': int(result.presente),
                'campos_extraidos_json': json.dumps(result.campos_extraidos.__dict__, ensure_ascii=False),
                'inconsistencias_json': json.dumps([item.__dict__ for item in result.inconsistencias], ensure_ascii=False),
                'document_score': round(result.document_score, 2),
                'recomendacion': result.recomendacion,
            }
        )
    results_df = pd.DataFrame(results)
    if results_df.empty:
        return results_df

    doc_flags = results_df.copy()
    doc_flags['inconsistencia_detectada'] = doc_flags['inconsistencias_json'].map(lambda value: 1 if value and value != '[]' else 0)
    doc_flags = doc_flags[['id_documento', 'inconsistencia_detectada']]

    with sqlite3.connect(db_path) as conn:
        results_df.to_sql('document_ai_results', conn, if_exists='replace', index=False)
        documentos_df = pd.read_sql('SELECT * FROM documentos', conn)
        documentos_df = documentos_df.drop(columns=['inconsistencia_detectada'], errors='ignore').merge(doc_flags, on='id_documento', how='left')
        documentos_df['inconsistencia_detectada'] = documentos_df['inconsistencia_detectada'].fillna(0).astype(int)
        documentos_df.to_sql('documentos', conn, if_exists='replace', index=False)
    return results_df
