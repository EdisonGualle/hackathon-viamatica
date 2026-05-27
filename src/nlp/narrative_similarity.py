"""
Módulo NLP para detección de similitud entre narrativas de siniestros.
Usa TF-IDF + cosine similarity. Sin costo, sin API externa.
Detecta narrativas clonadas (>85% similitud) y similares (70-84%).
"""
import sqlite3

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calcular_similitudes(siniestros_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula similitud TF-IDF entre todas las descripciones.
    Retorna DataFrame con pares similares y score de similitud NLP por siniestro.
    """
    descripciones = siniestros_df["descripcion"].fillna("").tolist()
    ids = siniestros_df["id_siniestro"].tolist()

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=1,
        max_features=5000,
    )
    tfidf_matrix = vectorizer.fit_transform(descripciones)
    sim_matrix = cosine_similarity(tfidf_matrix)

    # Score NLP por siniestro: máxima similitud con cualquier otro siniestro
    np.fill_diagonal(sim_matrix, 0)
    max_sim_por_siniestro = sim_matrix.max(axis=1)

    score_nlp_df = pd.DataFrame({
        "id_siniestro": ids,
        "score_nlp_similitud": np.round(max_sim_por_siniestro * 100, 2),
    })

    # Puntaje: >85% similitud → 8 pts, 70-84% → 4 pts
    def pts_similitud(s):
        if s > 85:
            return 8
        elif s >= 70:
            return 4
        return 0

    score_nlp_df["puntos_nlp"] = score_nlp_df["score_nlp_similitud"].apply(pts_similitud)
    score_nlp_df["nivel_nlp"] = score_nlp_df["score_nlp_similitud"].apply(
        lambda s: "CLONADO" if s > 85 else ("SIMILAR" if s >= 70 else "NORMAL")
    )

    # Pares con alta similitud (para el grafo y el agente)
    pares = []
    n = len(ids)
    for i in range(n):
        for j in range(i + 1, n):
            sim = sim_matrix[i][j]
            if sim >= 0.70:
                pares.append({
                    "id_siniestro_a": ids[i],
                    "id_siniestro_b": ids[j],
                    "similitud": round(float(sim) * 100, 2),
                    "nivel": "CLONADO" if sim > 0.85 else "SIMILAR",
                })

    pares_df = pd.DataFrame(pares) if pares else pd.DataFrame(
        columns=["id_siniestro_a", "id_siniestro_b", "similitud", "nivel"]
    )

    return score_nlp_df, pares_df


def guardar_similitudes(db_path: str, score_nlp_df: pd.DataFrame, pares_df: pd.DataFrame):
    conn = sqlite3.connect(db_path)
    score_nlp_df.to_sql("scores_nlp", conn, if_exists="replace", index=False)
    pares_df.to_sql("pares_similares", conn, if_exists="replace", index=False)
    conn.close()
    print(f"  Scores NLP: {len(score_nlp_df)} siniestros procesados.")
    print(f"  Pares similares: {len(pares_df)} pares detectados (>=70% similitud).")


if __name__ == "__main__":
    import os
    db_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "fraudia.db")
    )
    conn = sqlite3.connect(db_path)
    sins_df = pd.read_sql("SELECT id_siniestro, descripcion FROM siniestros", conn)
    conn.close()

    print("Calculando similitudes de narrativas...")
    score_nlp_df, pares_df = calcular_similitudes(sins_df)
    guardar_similitudes(db_path, score_nlp_df, pares_df)
    print("Niveles NLP:")
    print(score_nlp_df["nivel_nlp"].value_counts())
