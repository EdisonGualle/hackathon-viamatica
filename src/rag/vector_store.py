from __future__ import annotations

from rag.retriever import LocalRetriever


class InMemoryVectorStore:
    def __init__(self, chunks: list[dict]):
        self.retriever = LocalRetriever(chunks)

    def search(self, question: str, top_k: int = 4) -> list[dict]:
        return self.retriever.search(question, top_k=top_k)
