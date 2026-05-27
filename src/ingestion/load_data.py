"""
Pipeline principal: genera datos → aplica reglas → entrena ML → calcula NLP → guarda scores.
Ejecutar una vez antes de iniciar el dashboard.
"""
import json
import os
import sqlite3
import sys

import pandas as pd

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)
DB_PATH = os.path.normpath(os.path.join(ROOT_DIR, "fraudia.db"))

from data.synthetic.generate_dataset import main as gen_dataset
from models.fraud_model import entrenar_y_guardar
from nlp.narrative_similarity import calcular_similitudes, guardar_similitudes
from rules.fraud_rules import procesar_todos


def run_pipeline():
    print("=" * 60)
    print("  FRAUDIA CLAIMS — Pipeline de inicialización")
    print("=" * 60)

    # 1. Generar dataset
    print("\n[1/4] Generando dataset sintético...")
    gen_dataset()

    # 2. Motor de reglas
    print("\n[2/4] Ejecutando motor de reglas...")
    reglas_df = procesar_todos(DB_PATH)
    print(f"  Distribución niveles (reglas):")
    print(reglas_df["nivel_reglas"].value_counts().to_string())

    # 3. Modelo ML
    print("\n[3/4] Entrenando modelos ML...")
    model = entrenar_y_guardar(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    sins_df = pd.read_sql("SELECT * FROM siniestros", conn)
    pols_df = pd.read_sql("SELECT * FROM polizas", conn)
    conn.close()
    ml_df = model.predict(sins_df, pols_df)

    # 4. NLP similitud
    print("\n[4/4] Calculando similitud de narrativas (NLP)...")
    conn = sqlite3.connect(DB_PATH)
    desc_df = pd.read_sql("SELECT id_siniestro, descripcion FROM siniestros", conn)
    conn.close()
    score_nlp_df, pares_df = calcular_similitudes(desc_df)
    guardar_similitudes(DB_PATH, score_nlp_df, pares_df)

    # Combinar y guardar scores finales
    print("\nCombinando scores finales...")
    scores = reglas_df[["id_siniestro", "score_reglas", "nivel_reglas", "reglas_activadas", "explicacion_reglas"]].copy()
    scores = scores.merge(ml_df[["id_siniestro", "score_ml"]], on="id_siniestro", how="left")
    scores = scores.merge(score_nlp_df[["id_siniestro", "puntos_nlp"]], on="id_siniestro", how="left")
    scores["score_ml"] = scores["score_ml"].fillna(0)
    scores["puntos_nlp"] = scores["puntos_nlp"].fillna(0)

    # Score final ponderado: 45% reglas + 40% ML + 15% NLP
    scores["score_final"] = (
        0.45 * scores["score_reglas"]
        + 0.40 * scores["score_ml"]
        + 0.15 * scores["puntos_nlp"]
    ).round(2).clip(0, 100)

    # Confianza IA: basada en score_final y número de reglas activadas
    def _num_reglas(r):
        try:
            return len(json.loads(r)) if r and r != "[]" else 0
        except Exception:
            return 0

    scores["_n_reglas"] = scores["reglas_activadas"].apply(_num_reglas)
    scores["confianza_ia"] = (
        (scores["score_final"] * 0.8 + scores["_n_reglas"] * 3).clip(0, 97).round(1)
    )
    scores.drop(columns=["_n_reglas"], inplace=True)

    CRITICAS_ROJO = {"RF-01", "RF-02", "RF-03", "RF-04"}

    def nivel_final(row):
        # Reglas críticas fuerzan ROJO directamente
        reglas_act = row["reglas_activadas"] or "[]"
        activas = set(reglas_act.strip("[]").replace('"', '').split(",")) if reglas_act != "[]" else set()
        if activas & CRITICAS_ROJO:
            return "ROJO"
        # Score alto → ROJO
        if row["score_final"] >= 76:
            return "ROJO"
        # ML o reglas intermedias → AMARILLO
        if row["score_final"] >= 41 or row["score_ml"] >= 55:
            return "AMARILLO"
        return "VERDE"

    scores["nivel"] = scores.apply(nivel_final, axis=1)
    scores["explicacion"] = scores["explicacion_reglas"]
    scores["fecha_calculo"] = pd.Timestamp.now().isoformat()

    final_df = scores[[
        "id_siniestro", "score_reglas", "score_ml", "puntos_nlp",
        "score_final", "nivel", "reglas_activadas", "explicacion",
        "confianza_ia", "fecha_calculo"
    ]].rename(columns={"puntos_nlp": "score_nlp"})

    conn = sqlite3.connect(DB_PATH)
    final_df.to_sql("scores_riesgo", conn, if_exists="replace", index=False)
    conn.close()

    print("\n" + "=" * 60)
    print("  Pipeline completado exitosamente.")
    print(f"  Distribución final:")
    print(final_df["nivel"].value_counts().to_string())
    print(f"  Base de datos: {DB_PATH}")
    print("  Ejecuta ahora: python src/app/main.py")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
