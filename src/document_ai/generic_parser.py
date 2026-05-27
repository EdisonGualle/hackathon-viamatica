from __future__ import annotations

from .schemas import DocumentFieldSet


def parse_generic_document(document_type: str, document_row: dict) -> DocumentFieldSet:
    return DocumentFieldSet(
        fecha_emision=document_row.get('fecha_emision'),
        fecha_evento=document_row.get('fecha_evento_doc'),
        monto=float(document_row['monto_doc']) if document_row.get('monto_doc') not in (None, '') else None,
        proveedor=document_row.get('proveedor_doc') or None,
        placa=document_row.get('placa_doc') or None,
        tipo_documento=document_type,
    )
