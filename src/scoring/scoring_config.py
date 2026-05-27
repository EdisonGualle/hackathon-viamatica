from __future__ import annotations

SCORING_CONFIG = {
    'weights': {
        'score_reglas': 0.45,
        'score_ml': 0.40,
        'score_nlp': 0.15,
    },
    'thresholds': {
        'verde_max': 40.0,
        'amarillo_max': 75.0,
        'rojo_min': 76.0,
    },
    'critical_rules': ['RF-01', 'RF-02', 'RF-03', 'RF-04'],
    'actions': {
        'VERDE': 'Continuar flujo normal con monitoreo operativo.',
        'AMARILLO': 'Revisión documental prioritaria por Unidad Antifraude.',
        'ROJO': 'Escalar a revisión especializada reforzada.',
    },
}
