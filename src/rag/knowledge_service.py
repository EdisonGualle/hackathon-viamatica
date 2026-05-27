from __future__ import annotations

from pathlib import Path

from rag.chunker import chunk_document
from rag.loader import load_markdown_documents
from rag.retriever import LocalRetriever

ROOT = Path(__file__).resolve().parents[2]
KB_ROOT = ROOT / 'knowledge_base'


class KnowledgeService:
    def __init__(self, kb_root: str | Path = KB_ROOT):
        self.kb_root = Path(kb_root)
        self.documents = load_markdown_documents(self.kb_root)
        chunks = []
        for document in self.documents:
            chunks.extend(chunk_document(document))
        self.retriever = LocalRetriever(chunks)

    def query(self, question: str, top_k: int = 4) -> dict:
        results = self.retriever.search(question, top_k=top_k)
        summary = []
        for chunk in results:
            summary.append(
                {
                    'chunk_id': chunk['chunk_id'],
                    'section': chunk['section'],
                    'path': chunk['path'],
                    'source_type': chunk['source_type'],
                    'score': chunk['score'],
                    'text': chunk['text'],
                }
            )
        citations = [f"{item['section']} - {item['path']}" for item in summary]
        return {'question': question, 'results': summary, 'citations': citations}

    def answer(self, question: str, top_k: int = 4) -> dict:
        payload = self.query(question, top_k=top_k)
        if not payload['results']:
            return {'answer': 'No se encontró fundamento documental suficiente en la base de conocimiento.', 'sources': []}
        texts = []
        for item in payload['results']:
            snippet = item['text'].strip().replace('\n', ' ')
            texts.append(f"[{item['section']}] {snippet[:280]}")
        return {'answer': ' '.join(texts), 'sources': payload['citations']}
