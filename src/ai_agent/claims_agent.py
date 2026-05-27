from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from typing import Any

import pandas as pd

SRC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from agent.fraudia_agent import FraudiaAgentV2
from rag.knowledge_service import KnowledgeService
from scoring import recommend_action_for_level

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "fraudia.db"))


class FraudiaAgent:
    def __init__(self) -> None:
        self.kb = KnowledgeService()
        self.agent_v2 = FraudiaAgentV2()

    def chat(self, question: str) -> str:
        return answer_with_local_tools(question, self.kb, self.agent_v2)


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _query_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    with _conn() as conn:
        return pd.read_sql(sql, conn, params=params)


def _normalize(text: str) -> str:
    text = text.lower().strip()
    replacements = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for src, target in replacements.items():
        text = text.replace(src, target)
    return text


def _extract_claim_id(text: str) -> str | None:
    match = re.search(r"(sin-\d{4}|tc-[a-z0-9-]+)", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def _format_records(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "Sin resultados."
    rows = []
    for _, row in df.iterrows():
        parts = [f"{column}: {row[column]}" for column in columns if column in df.columns]
        rows.append("- " + " | ".join(parts))
    return "\n".join(rows)


def top_risk(limit: int = 10) -> str:
    df = _query_df(
        """
        SELECT s.id_siniestro, s.ramo, s.cobertura, s.id_asegurado, s.id_proveedor,
               s.monto_reclamado, sr.score_final, sr.nivel, sr.reglas_activadas
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        ORDER BY sr.score_final DESC, sr.nivel DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _format_records(
        df, ["id_siniestro", "nivel", "score_final", "cobertura", "id_proveedor", "monto_reclamado"]
    )


def providers_ranking(limit: int = 10) -> str:
    df = _query_df(
        """
        SELECT s.id_proveedor, COALESCE(p.nombre, s.id_proveedor) AS proveedor,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        LEFT JOIN proveedores p ON p.id_proveedor = s.id_proveedor
        GROUP BY s.id_proveedor, proveedor
        ORDER BY rojos DESC, score_promedio DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _format_records(df, ["id_proveedor", "proveedor", "rojos", "amarillos", "score_promedio"])


def suspicious_by_city() -> str:
    df = _query_df(
        """
        SELECT ciudad,
               COUNT(*) AS total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY ciudad
        ORDER BY rojos DESC, amarillos DESC
        """
    )
    return _format_records(df, ["ciudad", "rojos", "amarillos", "score_promedio"])


def suspicious_by_ramo() -> str:
    df = _query_df(
        """
        SELECT ramo,
               COUNT(*) AS total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               ROUND(AVG(sr.score_final), 1) AS score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY ramo
        ORDER BY rojos DESC, score_promedio DESC
        """
    )
    return _format_records(df, ["ramo", "rojos", "amarillos", "score_promedio"])


def high_frequency_insureds(limit: int = 10) -> str:
    df = _query_df(
        """
        SELECT id_asegurado, COUNT(*) AS total_siniestros,
               ROUND(AVG(sr.score_final), 1) AS score_promedio,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        GROUP BY id_asegurado
        HAVING total_siniestros >= 2
        ORDER BY total_siniestros DESC, score_promedio DESC
        LIMIT ?
        """,
        (limit,),
    )
    return _format_records(df, ["id_asegurado", "total_siniestros", "rojos", "score_promedio"])


def missing_documents() -> str:
    df = _query_df(
        """
        SELECT s.id_siniestro, s.documentos_completos, sr.nivel, sr.score_final
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.documentos_completos = 0
        ORDER BY sr.score_final DESC
        LIMIT 20
        """
    )
    return _format_records(df, ["id_siniestro", "nivel", "score_final"])


def atypical_amounts() -> str:
    df = _query_df(
        """
        SELECT s.id_siniestro, s.monto_reclamado, p.suma_asegurada,
               ROUND(100.0 * s.monto_reclamado / p.suma_asegurada, 1) AS pct_suma,
               sr.nivel, sr.score_final
        FROM siniestros s
        JOIN polizas p ON p.id_poliza = s.id_poliza
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE p.suma_asegurada > 0 AND (1.0 * s.monto_reclamado / p.suma_asegurada) >= 0.9
        ORDER BY pct_suma DESC
        LIMIT 20
        """
    )
    return _format_records(df, ["id_siniestro", "pct_suma", "nivel", "score_final"])


def near_policy_border() -> str:
    df = _query_df(
        """
        SELECT s.id_siniestro, s.dias_inicio_poliza, s.dias_fin_poliza, sr.nivel, sr.score_final
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
        WHERE s.dias_inicio_poliza <= 30 OR s.dias_fin_poliza <= 30
        ORDER BY CASE WHEN s.dias_inicio_poliza < s.dias_fin_poliza THEN s.dias_inicio_poliza ELSE s.dias_fin_poliza END ASC
        LIMIT 20
        """
    )
    return _format_records(df, ["id_siniestro", "dias_inicio_poliza", "dias_fin_poliza", "nivel", "score_final"])


def repeated_patterns() -> str:
    df = _query_df(
        """
        SELECT id_siniestro_a, id_siniestro_b, similitud, nivel
        FROM pares_similares
        ORDER BY similitud DESC
        LIMIT 20
        """
    )
    return _format_records(df, ["id_siniestro_a", "id_siniestro_b", "similitud", "nivel"])


def executive_summary() -> str:
    df = _query_df(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN nivel = 'ROJO' THEN 1 ELSE 0 END) AS rojos,
               SUM(CASE WHEN nivel = 'AMARILLO' THEN 1 ELSE 0 END) AS amarillos,
               SUM(CASE WHEN nivel = 'VERDE' THEN 1 ELSE 0 END) AS verdes,
               ROUND(AVG(score_final), 1) AS score_promedio
        FROM scores_riesgo
        """
    )
    if df.empty:
        return "Sin datos."
    row = df.iloc[0].to_dict()
    return (
        f"Portafolio total: {row['total']} siniestros\n"
        f"ROJO: {row['rojos']} | AMARILLO: {row['amarillos']} | VERDE: {row['verdes']}\n"
        f"Score promedio: {row['score_promedio']}"
    )


def _safe_json_list(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if not raw:
        return []
    try:
        value = json.loads(raw)
        return value if isinstance(value, list) else []
    except Exception:
        return []


def _format_sources(label: str, sources: list[str]) -> str:
    if not sources:
        return f"{label}:\n- Sin fuente recuperada"
    return f"{label}:\n" + "\n".join(f"- {source}" for source in sources)


def _format_document_alerts(document_payload: dict) -> str:
    alerts = document_payload.get("alertas_documentales") or []
    if not alerts:
        return "Sin alertas documentales relevantes."
    lines = []
    for alert in alerts[:5]:
        inconsistencias = alert.get("inconsistencias") or []
        codes = ", ".join(item.get("codigo", "N/D") for item in inconsistencias[:3])
        lines.append(f"- {alert.get('id_documento')} ({alert.get('tipo')}): {codes}")
    return "\n".join(lines)


def _format_related_network(related_network: list[dict]) -> str:
    if not related_network:
        return "Sin relaciones relevantes adicionales por proveedor."
    lines = []
    for item in related_network[:5]:
        lines.append(
            f"- {item.get('id_siniestro')} | proveedor {item.get('id_proveedor')} | "
            f"nivel {item.get('nivel')} | score {item.get('score_final')}"
        )
    return "\n".join(lines)


def _format_similar_narratives(similar_narratives: list[dict], claim_id: str) -> str:
    if not similar_narratives:
        return "No se detectaron narrativas similares materialmente relevantes."
    lines = []
    for item in similar_narratives[:5]:
        related = item.get("id_siniestro_b") if item.get("id_siniestro_a") == claim_id else item.get("id_siniestro_a")
        lines.append(f"- {related} | similitud {item.get('similitud')} | nivel {item.get('nivel')}")
    return "\n".join(lines)


def _format_claim_response(payload: dict, kb: KnowledgeService, question: str = "") -> str:
    claim = payload.get("claim") or {}
    if not claim:
        return "No encontré el siniestro solicitado."

    breakdown = payload.get("breakdown") or {}
    documents = payload.get("documents") or {}
    policy = payload.get("policy") or {}
    provider = payload.get("provider") or {}
    related_network = payload.get("related_network") or []
    similar_narratives = payload.get("similar_narratives") or []
    recommended_actions = payload.get("recommended_actions") or [recommend_action_for_level(claim.get("nivel", "VERDE"))]
    memory = payload.get("memory") or []

    rules = _safe_json_list(claim.get("reglas_activadas"))
    reason_codes = _safe_json_list(claim.get("reason_codes_json"))
    scoring_breakdown = breakdown.get("scoring_breakdown") or {}
    rule_details = _safe_json_list(breakdown.get("detalle_reglas_json"))

    rag_case = kb.answer_case(claim["id_siniestro"], question or "explicacion documental y evidencia del caso")
    rag_rules = kb.answer(question or " ".join(reason_codes or rules or ["criterio de riesgo"]))
    provider_summary = (
        f"Proveedor {provider.get('id_proveedor')} con {provider.get('rojos', 0)} caso(s) rojo(s) "
        f"y score promedio {provider.get('score_promedio', 'N/D')}"
        if provider
        else f"Proveedor {claim.get('id_proveedor')} sin perfil agregado adicional."
    )
    policy_summary = (
        f"Monto reclamado {claim.get('monto_reclamado')} sobre suma asegurada {policy.get('suma_asegurada', 'N/D')} "
        f"({policy.get('pct_suma', 'N/D')}%)."
        if policy
        else "Sin contraste adicional contra póliza."
    )
    hechos = (
        f"Ramo {claim.get('ramo')}, cobertura {claim.get('cobertura')}, proveedor {claim.get('id_proveedor')}, "
        f"asegurado {claim.get('id_asegurado')}, monto {claim.get('monto_reclamado')}. {policy_summary}"
    )
    explanation = claim.get("explicacion_auditable") or claim.get("explicacion") or "Sin explicación disponible."
    if documents.get("alertas_documentales"):
        explanation += " Evidencia documental: " + documents.get("resumen", "")
    score_line = (
        f"Score: {claim.get('score_final')} "
        f"(reglas {claim.get('score_reglas')}, ML {claim.get('score_ml')}, NLP {claim.get('score_nlp')}, "
        f"documental {documents.get('document_score_total', 0)})"
    )
    breakdown_text = (
        f"- action: {scoring_breakdown.get('action', recommend_action_for_level(claim.get('nivel', 'VERDE')))}\n"
        f"- override_critico: {scoring_breakdown.get('critical_override', False)}\n"
        f"- componentes: reglas={scoring_breakdown.get('score_reglas', claim.get('score_reglas'))}, "
        f"ml={scoring_breakdown.get('score_ml', claim.get('score_ml'))}, "
        f"nlp={scoring_breakdown.get('score_nlp', claim.get('score_nlp'))}"
    )
    actions_text = "\n".join(f"{idx}. {action}" for idx, action in enumerate(recommended_actions, start=1))
    rule_detail_text = "Sin detalle granular adicional."
    if rule_details:
        detail_lines = []
        for item in rule_details[:5]:
            detail_lines.append(
                f"- {item.get('codigo')} | {item.get('nivel')} | {item.get('evidencia')} | puntos {item.get('puntos')}"
            )
        rule_detail_text = "\n".join(detail_lines)
    memory_text = "\n".join(f"- {item}" for item in memory) if memory else "- Sin memoria previa del caso."

    mixed_normative_text = ""
    normalized_question = _normalize(question) if question else ""
    if any(marker in normalized_question for marker in ["que significa", "regla", "rf-", "diferencia", "evidencia revisar", "playbook", "guardrail"]):
        mixed_normative_text = f"\nCriterio normativo aplicable: {rag_rules.get('answer', 'Sin criterio adicional recuperado.')}\n"

    return (
        f"Nivel: {claim.get('nivel')}\n"
        f"{score_line}\n"
        f"Confianza IA: {claim.get('confianza_ia', breakdown.get('confianza_ia', 'N/D'))}%\n"
        f"Señales detectadas: {', '.join(rules) if rules else 'Ninguna'}\n"
        f"Hechos del caso: {hechos}\n"
        f"Explicación de negocio: {explanation}\n"
        f"Reason codes: {', '.join(reason_codes) if reason_codes else 'Sin reason codes adicionales'}\n"
        f"Desglose del score:\n{breakdown_text}\n"
        f"Detalle de reglas:\n{rule_detail_text}\n"
        f"Análisis documental:\n{documents.get('resumen', 'Sin análisis documental.')}\n"
        f"Alertas documentales:\n{_format_document_alerts(documents)}\n"
        f"Perfil del proveedor: {provider_summary}\n"
        f"Red relacionada:\n{_format_related_network(related_network)}\n"
        f"Patrones narrativos:\n{_format_similar_narratives(similar_narratives, claim['id_siniestro'])}\n"
        f"Memoria del caso:\n{memory_text}\n"
        f"Recomendación:\n{actions_text}\n"
        f"{mixed_normative_text}"
        f"{_format_sources('Fuente del caso', rag_case.get('sources', []))}\n"
        f"{_format_sources('Fuente normativa', rag_rules.get('sources', []))}\n"
        "Nota ética: el sistema identifica posible fraude y prioriza revisión humana, no emite acusación automática."
    )


def _answer_normative(question: str, kb: KnowledgeService) -> str:
    payload = kb.answer(question)
    sources = payload.get("sources", [])
    source_text = "\n".join(f"- {source}" for source in sources) if sources else "- Sin fuente recuperada"
    return (
        f"{payload['answer']}\n\n"
        f"Fuente:\n{source_text}\n"
        "Nota ética: el sistema solo entrega criterio documental de apoyo."
    )


def answer_with_local_tools(question: str, kb: KnowledgeService | None = None, agent_v2: FraudiaAgentV2 | None = None) -> str:
    kb = kb or KnowledgeService()
    agent_v2 = agent_v2 or FraudiaAgentV2()
    normalized = _normalize(question)
    claim_id = _extract_claim_id(question)

    normative_markers = ["que significa", "regla", "rf-", "evidencia revisar", "diferencia hay entre", "guardrail", "playbook"]
    if any(marker in normalized for marker in normative_markers) and not claim_id:
        return _answer_normative(question, kb)

    if claim_id:
        if "reporte" in normalized and "auditor" in normalized:
            return agent_v2.generate_audit_report(claim_id)
        payload = agent_v2.analyze_case(claim_id)
        if payload:
            return _format_claim_response(payload, kb, question)

    if "top 10" in normalized or "mayor riesgo" in normalized:
        return "Top de mayor riesgo:\n" + top_risk(10)
    if "proveedor" in normalized and ("alerta" in normalized or "ranking" in normalized):
        return "Proveedores con mayor concentración de alertas:\n" + providers_ranking(10)
    if "ramo" in normalized:
        return "Concentración por ramo:\n" + suspicious_by_ramo()
    if "ciudad" in normalized:
        return "Concentración por ciudad:\n" + suspicious_by_city()
    if "asegurado" in normalized and "frecuencia" in normalized:
        return "Asegurados con mayor frecuencia:\n" + high_frequency_insureds(10)
    if "documento" in normalized and ("falt" in normalized or "incomplet" in normalized):
        return "Documentos faltantes o incompletos:\n" + missing_documents()
    if "monto" in normalized and ("atip" in normalized or "cercano" in normalized):
        return "Montos atípicos:\n" + atypical_amounts()
    if "inicio de poliza" in normalized or "borde de vigencia" in normalized:
        return "Siniestros cerca del borde de vigencia:\n" + near_policy_border()
    if "patron" in normalized or "repetid" in normalized or "clonad" in normalized:
        return "Patrones repetidos:\n" + repeated_patterns()
    if "resumen ejecutivo" in normalized:
        return "Resumen ejecutivo:\n" + executive_summary()
    if "que revisar primero" in normalized or "priorizar" in normalized:
        return "Prioridad sugerida:\n" + top_risk(5)

    return "Resumen ejecutivo:\n" + executive_summary() + "\n\n" + "Top 5 de revisión prioritaria:\n" + top_risk(5)
