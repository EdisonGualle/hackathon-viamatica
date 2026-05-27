from __future__ import annotations

from pathlib import Path


def extract_text(document_row: dict) -> str:
    if not int(document_row.get('presente', 0) or 0):
        return ''
    text = str(document_row.get('texto_ocr') or document_row.get('texto_documento') or '')
    if text:
        return text.strip()
    path = str(document_row.get('file_path') or '').strip()
    if path and Path(path).exists():
        return Path(path).read_text(encoding='utf-8').strip()
    return ''


def estimate_legibility(document_row: dict, text: str) -> float:
    hint = str(document_row.get('legibilidad_hint') or 'alta').lower()
    if not int(document_row.get('presente', 0) or 0):
        return 0.0
    if 'ilegible' in text.lower() or '###' in text:
        return 0.18
    if hint == 'alta':
        return 0.95 if len(text) > 30 else 0.82
    if hint == 'media':
        return 0.72 if len(text) > 20 else 0.58
    if hint == 'baja':
        return 0.42 if len(text) > 15 else 0.28
    return 0.65
