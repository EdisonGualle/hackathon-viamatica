from __future__ import annotations

from pathlib import Path


def load_markdown_documents(base_path: str | Path) -> list[dict]:
    root = Path(base_path)
    documents = []
    for path in sorted(root.rglob('*.md')):
        text = path.read_text(encoding='utf-8')
        documents.append(
            {
                'document_id': path.stem,
                'document_version': '2026-05-27',
                'path': str(path),
                'text': text,
                'source_type': path.parent.name,
            }
        )
    return documents
