"""
API minima para demostrar integracion futura.
Ejecutar: uvicorn src.api.main:app --reload
"""
import os
import sqlite3

import pandas as pd
from fastapi import FastAPI

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(ROOT_DIR, "fraudia.db")

app = FastAPI(title="FRAUDIA Claims API", version="1.0.0")


def _query(sql: str, params: tuple = ()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df.to_dict("records")


@app.get("/health")
def health():
    return {"status": "ok", "database": os.path.exists(DB_PATH)}


@app.get("/claims/top-risk")
def top_risk(limit: int = 10):
    return _query("""
        SELECT s.id_siniestro, s.ramo, s.cobertura, s.id_proveedor,
               s.monto_reclamado, sr.score_final, sr.nivel, sr.reglas_activadas
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        ORDER BY sr.score_final DESC
        LIMIT ?
    """, (limit,))


@app.get("/claims/{claim_id}")
def claim_detail(claim_id: str):
    rows = _query("""
        SELECT s.*, sr.score_final, sr.score_reglas, sr.score_ml, sr.score_nlp,
               sr.nivel, sr.reglas_activadas, sr.explicacion
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.id_siniestro = ?
    """, (claim_id,))
    return rows[0] if rows else {"error": "claim_not_found"}


@app.get("/providers/ranking")
def provider_ranking(limit: int = 10):
    return _query("""
        SELECT s.id_proveedor, COALESCE(p.nombre, s.id_proveedor) AS nombre,
               COALESCE(p.tipo, 'N/D') AS tipo,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS alertas_rojas,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS alertas_amarillas,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        LEFT JOIN proveedores p ON p.id_proveedor = s.id_proveedor
        GROUP BY s.id_proveedor, p.nombre, p.tipo
        ORDER BY alertas_rojas DESC, score_promedio DESC
        LIMIT ?
    """, (limit,))
