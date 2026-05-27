from __future__ import annotations

from typing import Iterable

from .score_schema import Assessment, ComponentScores, RuleEvidence, ScoreBreakdown
from .scoring_config import SCORING_CONFIG
from .thresholds import AMARILLO_MIN, CRITICAL_RULES, ROJO_MIN, VERDE_MAX


def _clip_0_100(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)


def _normalize_rule_codes(rules: Iterable[str | RuleEvidence]) -> list[str]:
    codes = []
    for item in rules:
        if isinstance(item, RuleEvidence):
            codes.append(item.codigo)
        else:
            codes.append(str(item))
    return [code for code in codes if code]


def is_critical_triggered(active_rules: Iterable[str | RuleEvidence]) -> list[str]:
    codes = _normalize_rule_codes(active_rules)
    return sorted({code for code in codes if code in CRITICAL_RULES})


def determine_level(score_final: float, active_rules: Iterable[str | RuleEvidence]) -> tuple[str, bool, list[str]]:
    critical = is_critical_triggered(active_rules)
    if critical:
        return 'ROJO', True, critical
    if score_final >= ROJO_MIN:
        return 'ROJO', False, critical
    if score_final > VERDE_MAX:
        return 'AMARILLO', False, critical
    return 'VERDE', False, critical


def compute_confidence(score_final: float, score_ml: float, active_rules: Iterable[str | RuleEvidence]) -> float:
    rule_count = len(_normalize_rule_codes(active_rules))
    confidence = 0.7 * float(score_final) + 0.2 * float(score_ml) + 0.1 * min(rule_count * 10, 30)
    return round(max(0.0, min(99.0, confidence)), 1)


def recommend_action_for_level(level: str) -> str:
    return SCORING_CONFIG['actions'][level]


def build_breakdown(components: ComponentScores, active_rules: Iterable[str | RuleEvidence]) -> ScoreBreakdown:
    weights = dict(SCORING_CONFIG['weights'])
    raw = {
        'score_reglas': _clip_0_100(components.score_reglas),
        'score_ml': _clip_0_100(components.score_ml),
        'score_nlp': _clip_0_100(components.score_nlp),
    }
    weighted = {name: round(raw[name] * weight, 2) for name, weight in weights.items()}
    return ScoreBreakdown(
        weights=weights,
        weighted_components=weighted,
        raw_components=raw,
        critical_rules_triggered=is_critical_triggered(active_rules),
    )


def compute_assessment(components: ComponentScores, active_rules: Iterable[str | RuleEvidence], metadata: dict | None = None) -> Assessment:
    normalized_rules = _normalize_rule_codes(active_rules)
    breakdown = build_breakdown(components, active_rules)
    score_final = _clip_0_100(sum(breakdown.weighted_components.values()))
    level, critical_override, critical_rules = determine_level(score_final, active_rules)
    if critical_override and score_final < ROJO_MIN:
        score_final = float(ROJO_MIN)
    yellow_override = False
    if not critical_override and level == 'VERDE' and normalized_rules:
        score_final = max(float(AMARILLO_MIN), float(score_final))
        level = 'AMARILLO'
        yellow_override = True
    confidence = compute_confidence(score_final, components.score_ml, active_rules)
    return Assessment(
        score_final=round(score_final, 2),
        nivel_final=level,
        confianza_ia=confidence,
        critical_override=critical_override,
        action=recommend_action_for_level(level),
        breakdown=ScoreBreakdown(
            weights=breakdown.weights,
            weighted_components=breakdown.weighted_components,
            raw_components=breakdown.raw_components,
            critical_rules_triggered=critical_rules,
        ),
        reason_codes=_normalize_rule_codes(active_rules),
        metadata={**(metadata or {}), 'yellow_override': yellow_override},
    )


def score_simulated_claim(*, score_reglas: float, score_ml: float, score_nlp: float, active_rules: Iterable[str | RuleEvidence], factores: list[str] | None = None, ratio_pct: float | None = None, rule_details: list[dict] | None = None) -> dict:
    assessment = compute_assessment(
        ComponentScores(score_reglas=score_reglas, score_ml=score_ml, score_nlp=score_nlp),
        active_rules=active_rules,
        metadata={'mode': 'simulator'},
    )
    return {
        'nivel': assessment.nivel_final,
        'score_final': assessment.score_final,
        'score_reglas': round(score_reglas, 1),
        'score_ml': round(score_ml, 1),
        'score_nlp': round(score_nlp, 1),
        'confianza': assessment.confianza_ia,
        'reglas': rule_details or [],
        'accion': assessment.action,
        'factores': factores or [],
        'ratio': ratio_pct,
        'criticas': assessment.breakdown.critical_rules_triggered,
    }
