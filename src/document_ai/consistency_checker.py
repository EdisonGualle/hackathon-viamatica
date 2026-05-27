from __future__ import annotations

from .schemas import DocumentFieldSet, DocumentInconsistency


def _severity(points: int) -> str:
    if points >= 12:
        return 'ALTA'
    if points >= 6:
        return 'MEDIA'
    return 'BAJA'


def check_document_consistency(claim_row: dict, document_type: str, fields: DocumentFieldSet, legibility_score: float, presente: bool) -> tuple[list[DocumentInconsistency], float, str]:
    inconsistencies: list[DocumentInconsistency] = []
    score = 0.0

    claim_date = str(claim_row.get('fecha_ocurrencia') or '')
    claim_amount = float(claim_row.get('monto_reclamado') or 0)
    claim_provider = str(claim_row.get('id_proveedor') or '')
    claim_plate = str(claim_row.get('placa_vehiculo') or '')
    cobertura = str(claim_row.get('cobertura') or '').lower()

    def add(code: str, description: str, points: float, field_name: str = ''):
        nonlocal score
        score += points
        inconsistencies.append(
            DocumentInconsistency(
                codigo=code,
                descripcion=description,
                severidad=_severity(int(points)),
                field_name=field_name,
            )
        )

    if not presente:
        if document_type == 'parte_policial' and cobertura == 'ptxrb':
            add('DOC-DENUNCIA-AUSENTE', 'No existe denuncia policial para un caso de robo.', 12, 'tipo_documento')
        return inconsistencies, min(score, 30.0), 'Solicitar el documento faltante y validar la completitud del expediente.' if inconsistencies else 'Sin alerta documental.'

    if legibility_score < 0.45:
        add('DOC-ILEGIBLE', 'El documento presenta legibilidad insuficiente para validación confiable.', 8, 'legibilidad_score')

    if document_type == 'factura_taller':
        if fields.fecha_emision and claim_date and fields.fecha_emision < claim_date:
            add('DOC-FECHA-PREVIA', 'La factura fue emitida antes de la fecha de ocurrencia del siniestro.', 12, 'fecha_emision')
        if fields.monto is not None and claim_amount > 0:
            ratio = abs(fields.monto - claim_amount) / claim_amount
            if ratio > 0.25:
                add('DOC-MONTO-INCONSISTENTE', 'El monto documental no es coherente con el monto reclamado.', 10, 'monto')
        if fields.proveedor and fields.proveedor != claim_provider:
            add('DOC-PROVEEDOR-DISTINTO', 'El proveedor del documento no coincide con el proveedor del caso.', 10, 'proveedor')
        if fields.placa and claim_plate and fields.placa != claim_plate:
            add('DOC-PLACA-DISTINTA', 'La placa del documento no coincide con el vehículo asegurado.', 9, 'placa')

    if document_type == 'parte_policial':
        if fields.fecha_evento and claim_date and fields.fecha_evento != claim_date:
            add('DOC-FECHA-EVENTO-DISTINTA', 'La fecha del evento en la denuncia no coincide con la del siniestro.', 8, 'fecha_evento')
        if fields.placa and claim_plate and fields.placa != claim_plate:
            add('DOC-PLACA-DISTINTA', 'La placa en la denuncia no coincide con el vehículo asegurado.', 9, 'placa')

    recommendation = 'Solicitar validación documental y confirmar soporte con las contrapartes.' if inconsistencies else 'Soporte documental consistente para esta evidencia.'
    return inconsistencies, min(score, 30.0), recommendation
