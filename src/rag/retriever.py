from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LocalRetriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 2))
        corpus = [chunk['text'] for chunk in chunks]
        self.matrix = self.vectorizer.fit_transform(corpus) if corpus else None

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.chunks or self.matrix is None:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).flatten()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[:top_k]
        rows = []
        for idx, score in ranked:
            if score <= 0:
                continue
            chunk = dict(self.chunks[idx])
            chunk['score'] = round(float(score), 4)
            rows.append(chunk)
        return rows

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.chunks)
