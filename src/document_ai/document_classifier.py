from __future__ import annotations


def classify_document(document_row: dict, text: str) -> str:
    raw_type = str(document_row.get('tipo_documento') or '').lower()
    if raw_type:
        return raw_type
    lowered = text.lower()
    if 'factura' in lowered:
        return 'factura_taller'
    if 'denuncia policial' in lowered or 'parte policial' in lowered:
        return 'parte_policial'
    if 'informe pericial' in lowered:
        return 'informe_pericial'
    if 'identificacion' in lowered or 'cedula' in lowered:
        return 'cedula'
    if 'aviso de siniestro' in lowered:
        return 'aviso_siniestro'
    return 'soporte_general'
