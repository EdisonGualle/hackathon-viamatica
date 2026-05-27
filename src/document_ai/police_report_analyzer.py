from __future__ import annotations

import re

from .schemas import DocumentFieldSet

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
PLATE_RE = re.compile(r'Placa:\s*([A-Z0-9\-]+)', re.IGNORECASE)


def analyze_police_report(text: str) -> DocumentFieldSet:
    dates = DATE_RE.findall(text)
    fecha_evento = dates[0] if dates else None
    fecha_emision = dates[1] if len(dates) > 1 else fecha_evento
    placa = None
    if match := PLATE_RE.search(text):
        placa = match.group(1).upper()
    return DocumentFieldSet(
        fecha_emision=fecha_emision,
        fecha_evento=fecha_evento,
        placa=placa,
        tipo_documento='parte_policial',
    )
