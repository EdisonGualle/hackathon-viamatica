from __future__ import annotations

from agent.memory import CaseMemory
from agent.tools.claim_tools import compare_claim_with_policy, find_similar_narratives, get_claim_detail
from agent.tools.document_tools import get_document_analysis
from agent.tools.graph_tools import find_related_claim_network
from agent.tools.provider_tools import get_provider_risk_profile
from agent.tools.report_tools import generate_case_audit_report, recommend_next_actions
from agent.tools.scoring_tools import get_score_breakdown


class FraudiaAgentV2:
    def __init__(self) -> None:
        self.memory = CaseMemory()

    def analyze_case(self, id_siniestro: str) -> dict:
        claim = get_claim_detail(id_siniestro)
        if not claim:
            return {}
        documents = get_document_analysis(id_siniestro)
        breakdown = get_score_breakdown(id_siniestro)
        related = find_related_claim_network(id_siniestro)
        similar = find_similar_narratives(id_siniestro)
        policy = compare_claim_with_policy(id_siniestro)
        provider = get_provider_risk_profile(claim.get('id_proveedor')) if claim.get('id_proveedor') else {}
        actions = recommend_next_actions(claim, documents)
        self.memory.remember(id_siniestro, f"Analizado con {len(actions)} acción(es) sugerida(s).")
        return {
            'claim': claim,
            'documents': documents,
            'breakdown': breakdown,
            'policy': policy,
            'provider': provider,
            'related_network': related,
            'similar_narratives': similar,
            'recommended_actions': actions,
            'memory': self.memory.recall(id_siniestro),
        }

    def generate_audit_report(self, id_siniestro: str) -> str:
        return generate_case_audit_report(id_siniestro)
