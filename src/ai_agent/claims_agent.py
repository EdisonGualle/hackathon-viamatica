from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from typing import Any

import pandas as pd

SRC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from rag.knowledge_service import KnowledgeService

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fraudia.db'))


class FraudiaAgent:
    def __init__(self) -> None:
        self.kb = KnowledgeService()

    def chat(self, question: str) -> str:
        return answer_with_local_tools(question, self.kb)


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _query_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(sql, conn, params=params)


def _normalize(text: str) -> str:
    text = text.lower().strip()
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'
    }
    for src, target in replacements.items():
        text = text.replace(src, target)
    return text


def _extract_claim_id(text: str) -> str | None:
    match = re.search(r'(sin-\d{4}|tc-[a-z0-9-]+)', text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def _format_records(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return 'Sin resultados.'
    rows = []
    for _, row in df.iterrows():
        parts = [f'{column}: {row[column]}' for column in columns if column in df.columns]
        rows.append('- ' + ' | '.join(parts))
    return '\n'.join(rows)


def top_risk(limit: int = 10) -> str:
    df = _query_df(
        '''
        SELECT s.id_siniestro, s.ramo, s.cobertura, s.id_asegurado, s.id_proveedor,
               s.monto_reclamado, sr.score_final, sr.nivel, sr.reglas_activadas
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        ORDER BY sr.score_final DESC, sr.nivel DESC
        LIMIT ?
        ''',
        (limit,),
    )
    return _format_records(df, ['id_siniestro', 'nivel', 'score_final', 'cobertura', 'id_proveedor', 'monto_reclamado'])


def claim_detail(claim_id: str) -> dict:
    df = _query_df(
        '''
        SELECT s.*, sr.score_reglas, sr.score_ml, sr.score_nlp, sr.score_final,
               sr.nivel, sr.reglas_activadas, sr.detalle_reglas_json, sr.explicacion
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.id_siniestro = ?
        ''',
        (claim_id,),
    )
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def providers_ranking(limit: int = 10) -> str:
    df = _query_df(
        '''
        SELECT s.id_proveedor, COALESCE(p.nombre, s.id_proveedor) AS proveedor,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        LEFT JOIN proveedores p ON p.id_proveedor = s.id_proveedor
        GROUP BY s.id_proveedor, proveedor
        ORDER BY rojos DESC, score_promedio DESC
        LIMIT ?
        ''',
        (limit,),
    )
    return _format_records(df, ['id_proveedor', 'proveedor', 'rojos', 'amarillos', 'score_promedio'])


def suspicious_by_city() -> str:
    df = _query_df(
        '''
        SELECT ciudad,
               COUNT(*) AS total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY ciudad
        ORDER BY rojos DESC, amarillos DESC
        '''
    )
    return _format_records(df, ['ciudad', 'rojos', 'amarillos', 'score_promedio'])


def suspicious_by_ramo() -> str:
    df = _query_df(
        '''
        SELECT ramo,
               COUNT(*) AS total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY ramo
        ORDER BY rojos DESC, score_promedio DESC
        '''
    )
    return _format_records(df, ['ramo', 'rojos', 'amarillos', 'score_promedio'])


def high_frequency_insureds(limit: int = 10) -> str:
    df = _query_df(
        '''
        SELECT id_asegurado, COUNT(*) AS total_siniestros,
               ROUND(AVG(sr.score_final), 1) AS score_promedio,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY id_asegurado
        HAVING total_siniestros >= 2
        ORDER BY total_siniestros DESC, score_promedio DESC
        LIMIT ?
        ''',
        (limit,),
    )
    return _format_records(df, ['id_asegurado', 'total_siniestros', 'rojos', 'score_promedio'])


def missing_documents() -> str:
    df = _query_df(
        '''
        SELECT s.id_siniestro, s.documentos_completos, sr.nivel, sr.score_final
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.documentos_completos = 0
        ORDER BY sr.score_final DESC
        LIMIT 20
        '''
    )
    return _format_records(df, ['id_siniestro', 'nivel', 'score_final'])


def atypical_amounts() -> str:
    df = _query_df(
        '''
        SELECT s.id_siniestro, s.monto_reclamado, p.suma_asegurada,
               ROUND(100.0 * s.monto_reclamado / p.suma_asegurada, 1) AS pct_suma,
               sr.nivel, sr.score_final
        FROM siniestros s
        JOIN polizas p ON p.id_poliza = s.id_poliza
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE p.suma_asegurada > 0 AND (1.0 * s.monto_reclamado / p.suma_asegurada) >= 0.9
        ORDER BY pct_suma DESC
        LIMIT 20
        '''
    )
    return _format_records(df, ['id_siniestro', 'pct_suma', 'nivel', 'score_final'])


def near_policy_border() -> str:
    df = _query_df(
        '''
        SELECT s.id_siniestro, s.dias_inicio_poliza, s.dias_fin_poliza, sr.nivel, sr.score_final
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.dias_inicio_poliza <= 30 OR s.dias_fin_poliza <= 30
        ORDER BY CASE WHEN s.dias_inicio_poliza < s.dias_fin_poliza THEN s.dias_inicio_poliza ELSE s.dias_fin_poliza END ASC
        LIMIT 20
        '''
    )
    return _format_records(df, ['id_siniestro', 'dias_inicio_poliza', 'dias_fin_poliza', 'nivel', 'score_final'])


def repeated_patterns() -> str:
    df = _query_df(
        '''
        SELECT id_siniestro_a, id_siniestro_b, similitud, nivel
        FROM pares_similares
        ORDER BY similitud DESC
        LIMIT 20
        '''
    )
    return _format_records(df, ['id_siniestro_a', 'id_siniestro_b', 'similitud', 'nivel'])


def executive_summary() -> str:
    df = _query_df(
        '''
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               SUM(CASE WHEN nivel = 'VERDE' THEN 1 ELSE 0 END) AS verdes,
               ROUND(AVG(score_final), 1) AS score_promedio
        FROM scores_riesgo
        '''
    )
    if df.empty:
        return 'Sin datos.'
    row = df.iloc[0].to_dict()
    return (
        f"Portafolio total: {row['total']} siniestros\n"
        f"ROJO: {row['rojos']} | AMARILLO: {row['amarillos']} | VERDE: {row['verdes']}\n"
        f"Score promedio: {row['score_promedio']}"
    )


def _format_claim_response(claim: dict, kb: KnowledgeService | None = None) -> str:
    if not claim:
        return 'No encontré el siniestro solicitado.'
    rules = json.loads(claim.get('reglas_activadas') or '[]')
    detalle = []
    try:
        detalle = json.loads(claim.get('detalle_reglas_json') or '[]')
    except Exception:
        detalle = []

    fuentes = []
    if kb and rules:
        rag = kb.answer(' '.join(rules))
        fuentes = rag.get('sources', [])

    señales = ', '.join(rules) if rules else 'Ninguna'
    hechos = f"Ramo {claim['ramo']}, cobertura {claim['cobertura']}, proveedor {claim['id_proveedor']}, monto {claim['monto_reclamado']}"
    recomendacion = 'Continuar flujo normal con monitoreo operativo.'
    if claim['nivel'] == 'AMARILLO':
        recomendacion = 'Revisión documental prioritaria.'
    if claim['nivel'] == 'ROJO':
        recomendacion = 'Revisión especializada reforzada.'
    fuente_txt = '\n'.join(f'- {source}' for source in fuentes) if fuentes else '- SQL transaccional / motor de reglas'
    return (
        f"Nivel: {claim['nivel']}\n"
        f"Score: {claim['score_final']}\n"
        f"Señales detectadas: {señales}\n"
        f"Hechos del caso: {hechos}\n"
        f"Explicación de negocio: {claim['explicacion']}\n"
        f"Recomendación: {recomendacion}\n"
        f"Fuente:\n{fuente_txt}\n"
        f"Nota ética: el sistema identifica posible fraude y no sustituye la decisión humana."
    )


def _answer_normative(question: str, kb: KnowledgeService) -> str:
    payload = kb.answer(question)
    sources = payload.get('sources', [])
    source_text = '\n'.join(f'- {source}' for source in sources) if sources else '- Sin fuente recuperada'
    return f"{payload['answer']}\n\nFuente:\n{source_text}\nNota ética: el sistema solo entrega criterio documental de apoyo."


def answer_with_local_tools(question: str, kb: KnowledgeService | None = None) -> str:
    kb = kb or KnowledgeService()
    normalized = _normalize(question)
    claim_id = _extract_claim_id(question)

    normative_markers = ['que significa', 'regla', 'rf-', 'evidencia revisar', 'diferencia hay entre', 'guardrail', 'playbook']
    if any(marker in normalized for marker in normative_markers) and not claim_id:
        return _answer_normative(question, kb)

    if claim_id:
        claim = claim_detail(claim_id)
        if claim:
            return _format_claim_response(claim, kb)

    if 'top 10' in normalized or 'mayor riesgo' in normalized:
        return 'Top de mayor riesgo:\n' + top_risk(10)
    if 'proveedor' in normalized and ('alerta' in normalized or 'ranking' in normalized):
        return 'Proveedores con mayor concentración de alertas:\n' + providers_ranking(10)
    if 'ramo' in normalized:
        return 'Concentración por ramo:\n' + suspicious_by_ramo()
    if 'ciudad' in normalized:
        return 'Concentración por ciudad:\n' + suspicious_by_city()
    if 'asegurado' in normalized and 'frecuencia' in normalized:
        return 'Asegurados con mayor frecuencia:\n' + high_frequency_insureds(10)
    if 'documento' in normalized and ('falt' in normalized or 'incomplet' in normalized):
        return 'Documentos faltantes o incompletos:\n' + missing_documents()
    if 'monto' in normalized and ('atip' in normalized or 'cercano' in normalized):
        return 'Montos atípicos:\n' + atypical_amounts()
    if 'inicio de poliza' in normalized or 'borde de vigencia' in normalized:
        return 'Siniestros cerca del borde de vigencia:\n' + near_policy_border()
    if 'patron' in normalized or 'repetid' in normalized or 'clonad' in normalized:
        return 'Patrones repetidos:\n' + repeated_patterns()
    if 'resumen ejecutivo' in normalized:
        return 'Resumen ejecutivo:\n' + executive_summary()
    if 'que revisar primero' in normalized or 'priorizar' in normalized:
        return 'Prioridad sugerida:\n' + top_risk(5)

    return (
        'Resumen ejecutivo:\n' + executive_summary() + '\n\n'
        'Top 5 de revisión prioritaria:\n' + top_risk(5)
    )
