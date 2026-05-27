from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ComponentScores:
    score_reglas: float
    score_ml: float
    score_nlp: float
    score_documental: float = 0.0
    score_red: float = 0.0


@dataclass
class RuleEvidence:
    codigo: str
    nombre: str = ''
    tipo: str = ''
    puntos: float = 0.0
    evidencia: str = ''
    explicacion: str = ''
    variable_principal: str = ''
    fuente_negocio: str = ''
    activada: bool = True


@dataclass
class ScoreBreakdown:
    weights: dict[str, float]
    weighted_components: dict[str, float]
    raw_components: dict[str, float]
    critical_rules_triggered: list[str] = field(default_factory=list)


@dataclass
class Assessment:
    score_final: float
    nivel_final: str
    confianza_ia: float
    critical_override: bool
    action: str
    breakdown: ScoreBreakdown
    reason_codes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
