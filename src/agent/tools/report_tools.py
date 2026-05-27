from __future__ import annotations

from review import generate_audit_report


def generate_case_audit_report(id_siniestro: str) -> str:
    return generate_audit_report('fraudia.db', id_siniestro, 'agent')


def recommend_next_actions(claim_detail: dict, document_analysis: dict) -> list[str]:
    actions = []
    if claim_detail.get('nivel') == 'ROJO':
        actions.append('Escalar a revisión especializada.')
    elif claim_detail.get('nivel') == 'AMARILLO':
        actions.append('Realizar revisión documental prioritaria.')
    if document_analysis.get('alertas_documentales'):
        actions.append('Validar documentos con contrapartes y confirmar campos inconsistentes.')
    if not actions:
        actions.append('Mantener monitoreo operativo normal.')
    return actions
