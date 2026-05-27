import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from ai_agent.claims_agent import answer_with_local_tools
from ingestion.load_data import run_pipeline


class AgentQuestionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_pipeline()

    def test_top_risk_question(self):
        answer = answer_with_local_tools('top 10 de mayor riesgo')
        self.assertIn('Top de mayor riesgo', answer)

    def test_normative_question_includes_source(self):
        answer = answer_with_local_tools('que significa RF-03')
        self.assertIn('Fuente:', answer)

    def test_claim_question_includes_expected_sections(self):
        answer = answer_with_local_tools('por que este siniestro fue marcado SIN-0017')
        for marker in ['Nivel:', 'Score:', 'Señales detectadas:', 'Fuente:', 'Nota ética:']:
            self.assertIn(marker, answer)


if __name__ == '__main__':
    unittest.main()
