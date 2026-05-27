from __future__ import annotations

import re
from pathlib import Path


HEADING_RE = re.compile(r'^(#+)\s+(.*)$', re.MULTILINE)


def chunk_document(document: dict, min_chars: int = 250) -> list[dict]:
    text = document['text']
    path = Path(document['path'])
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [_make_chunk(document, 'general', text.strip(), 0)]

    chunks = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group(2).strip()
        body = text[start:end].strip()
        if len(body) < min_chars and chunks:
            chunks[-1]['text'] += '\n\n' + body
            continue
        chunks.append(_make_chunk(document, heading, body, len(chunks)))
    return chunks


def _make_chunk(document: dict, heading: str, body: str, index: int) -> dict:
    lowered = body.lower()
    risk = 'ROJO' if 'rf-0' in lowered or 'crit' in lowered else ('AMARILLO' if 'senal' in lowered else 'GENERAL')
    return {
        'chunk_id': f"{document['document_id']}-{index:03d}",
        'document_id': document['document_id'],
        'document_version': document['document_version'],
        'section': heading,
        'topic': heading,
        'risk_level': risk,
        'entities': sorted({token.upper() for token in re.findall(r'RF-\d+|S\d+', body, flags=re.IGNORECASE)}),
        'source_type': document['source_type'],
        'path': document['path'],
        'text': body,
    }
