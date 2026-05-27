from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calcular_similitudes(siniestros_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    textos = siniestros_df['descripcion'].fillna('').astype(str).tolist()
    ids = siniestros_df['id_siniestro'].tolist()

    if not textos:
        empty_scores = pd.DataFrame(columns=['id_siniestro', 'score_nlp', 'nivel_nlp'])
        empty_pairs = pd.DataFrame(columns=['id_siniestro_a', 'id_siniestro_b', 'similitud', 'nivel'])
        return empty_scores, empty_pairs

    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=1, max_features=6000)
    matrix = vectorizer.fit_transform(textos)
    sim_matrix = cosine_similarity(matrix)
    np.fill_diagonal(sim_matrix, 0)

    max_sim = sim_matrix.max(axis=1) * 100

    def level(score: float) -> str:
        if score > 85:
            return 'CLONADO'
        if score >= 70:
            return 'SIMILAR'
        return 'NORMAL'

    score_df = pd.DataFrame(
        {
            'id_siniestro': ids,
            'score_nlp': np.round(max_sim, 2),
            'nivel_nlp': [level(float(value)) for value in max_sim],
        }
    )

    pairs = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            score = round(float(sim_matrix[i][j] * 100), 2)
            if score >= 70:
                pairs.append(
                    {
                        'id_siniestro_a': ids[i],
                        'id_siniestro_b': ids[j],
                        'similitud': score,
                        'nivel': level(score),
                    }
                )

    pairs_df = pd.DataFrame(pairs) if pairs else pd.DataFrame(columns=['id_siniestro_a', 'id_siniestro_b', 'similitud', 'nivel'])
    return score_df, pairs_df


def guardar_similitudes(db_path: str, score_nlp_df: pd.DataFrame, pares_df: pd.DataFrame) -> None:
    with sqlite3.connect(db_path) as conn:
        score_nlp_df.to_sql('scores_nlp', conn, if_exists='replace', index=False)
        pares_df.to_sql('pares_similares', conn, if_exists='replace', index=False)


if __name__ == '__main__':
    import os

    db_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fraudia.db'))
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql('SELECT id_siniestro, descripcion FROM siniestros', conn)
    scores, pairs = calcular_similitudes(df)
    guardar_similitudes(db_path, scores, pairs)
    print(scores['nivel_nlp'].value_counts())
    print(f'Pares similares: {len(pairs)}')
