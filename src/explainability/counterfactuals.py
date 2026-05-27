from __future__ import annotations


def build_counterfactuals(score_row: dict, evidence_bundle: list[dict]) -> list[str]:
    counterfactuals: list[str] = []
    codes = {item.get('code') for item in evidence_bundle}
    if 'RF-03' in codes:
        counterfactuals.append('Sin la coincidencia con lista restrictiva el caso perdería la escalada crítica inmediata.')
    if 'RF-02' in codes or 'DOC-FECHA-PREVIA' in codes or 'DOC-PROVEEDOR-DISTINTO' in codes:
        counterfactuals.append('Con documentación consistente y validada, el caso bajaría su prioridad de revisión.')
    if 'S14' in codes:
        counterfactuals.append('Con un monto reclamado materialmente menor frente a la suma asegurada, el score bajaría.')
    if 'RF-05' in codes or 'S01' in codes:
        counterfactuals.append('Si el evento no ocurriera cerca del borde de vigencia, el caso perdería esa señal temporal.')
    if not counterfactuals and float(score_row.get('score_final', 0) or 0) > 40:
        counterfactuals.append('Sin las señales activas actuales, el caso podría bajar al nivel inmediato inferior.')
    return counterfactuals[:3]
