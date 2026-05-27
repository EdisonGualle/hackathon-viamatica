from __future__ import annotations

RULE_REASON_LABELS = {
    'RF-01': 'Cobertura crítica PTxRB',
    'RF-02': 'Inconsistencia documental crítica',
    'RF-03': 'Coincidencia con lista restrictiva',
    'RF-04': 'Dinámica físicamente imposible',
    'RF-05': 'Siniestro extremo al borde de vigencia',
    'RF-06': 'Demora atípica en denuncia de robo',
    'RF-07': 'Narrativa clonada o repetida',
}

DOCUMENT_REASON_LABELS = {
    'DOC-FECHA-PREVIA': 'Factura previa al evento',
    'DOC-PROVEEDOR-DISTINTO': 'Proveedor documental inconsistente',
    'DOC-MONTO-INCONSISTENTE': 'Monto documental inconsistente',
    'DOC-PLACA-DISTINTA': 'Placa documental inconsistente',
    'DOC-DENUNCIA-AUSENTE': 'Denuncia ausente para robo',
    'DOC-ILEGIBLE': 'Documento ilegible',
    'DOC-FECHA-EVENTO-DISTINTA': 'Fecha de evento inconsistente',
}


def reason_label(code: str) -> str:
    if code in RULE_REASON_LABELS:
        return RULE_REASON_LABELS[code]
    if code in DOCUMENT_REASON_LABELS:
        return DOCUMENT_REASON_LABELS[code]
    if code.startswith('S'):
        return f'Señal {code}'
    return code
