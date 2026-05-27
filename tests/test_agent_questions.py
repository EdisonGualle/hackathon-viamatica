import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from ai_agent.claims_agent import answer_with_local_tools
from tests._bootstrap import ensure_pipeline


class AgentQuestionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_pipeline()

    def test_top_risk_question(self):
        answer = answer_with_local_tools('top 10 de mayor riesgo')
        self.assertIn('Top de mayor riesgo', answer)

    def test_normative_question_includes_source(self):
        answer = answer_with_local_tools('que significa RF-03')
        self.assertIn('Fuente:', answer)

    def test_claim_question_includes_expected_sections(self):
        answer = answer_with_local_tools('por que este siniestro fue marcado SIN-0017')
        for marker in ['Nivel:', 'Score:', 'Señales detectadas:', 'Fuente del caso:', 'Fuente normativa:', 'Nota ética:']:
            self.assertIn(marker, answer)

    def test_claim_question_includes_document_and_reasoning_sections(self):
        answer = answer_with_local_tools('que evidencia documental tiene TC-X20')
        for marker in ['Análisis documental:', 'Alertas documentales:', 'Reason codes:', 'Recomendación:']:
            self.assertIn(marker, answer)

    def test_audit_report_question_returns_markdown_report(self):
        answer = answer_with_local_tools('genera reporte de auditoria TC-X20')
        self.assertIn('# Reporte de Auditoría - TC-X20', answer)

    def test_mixed_case_and_normative_question_includes_normative_criterion(self):
        answer = answer_with_local_tools('que significa RF-03 en el caso TC-X20')
        self.assertIn('Criterio normativo aplicable:', answer)
        self.assertIn('Fuente normativa:', answer)


if __name__ == '__main__':
    unittest.main()
