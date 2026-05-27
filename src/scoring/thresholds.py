from __future__ import annotations

from .scoring_config import SCORING_CONFIG

VERDE_MAX = SCORING_CONFIG['thresholds']['verde_max']
AMARILLO_MIN = VERDE_MAX + 1
AMARILLO_MAX = SCORING_CONFIG['thresholds']['amarillo_max']
ROJO_MIN = SCORING_CONFIG['thresholds']['rojo_min']
CRITICAL_RULES = tuple(SCORING_CONFIG['critical_rules'])
