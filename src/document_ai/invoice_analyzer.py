from __future__ import annotations

import re

from .schemas import DocumentFieldSet

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
AMOUNT_RE = re.compile(r'Monto:\s*([0-9]+(?:\.[0-9]+)?)', re.IGNORECASE)
PROVIDER_RE = re.compile(r'Proveedor:\s*([A-Z0-9\-]+)', re.IGNORECASE)
PLATE_RE = re.compile(r'Placa:\s*([A-Z0-9\-]+)', re.IGNORECASE)


def analyze_invoice(text: str) -> DocumentFieldSet:
    fecha = None
    monto = None
    proveedor = None
    placa = None
    if match := DATE_RE.search(text):
        fecha = match.group(1)
    if match := AMOUNT_RE.search(text):
        monto = float(match.group(1))
    if match := PROVIDER_RE.search(text):
        proveedor = match.group(1).upper()
    if match := PLATE_RE.search(text):
        placa = match.group(1).upper()
    return DocumentFieldSet(
        fecha_emision=fecha,
        monto=monto,
        proveedor=proveedor,
        placa=placa,
        tipo_documento='factura_taller',
    )
