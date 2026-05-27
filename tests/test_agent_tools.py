import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from ingestion.load_data import DB_PATH
from agent.fraudia_agent import FraudiaAgentV2
from rag.knowledge_service import KnowledgeService
from tests._bootstrap import ensure_pipeline


class AgentToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_pipeline()
        cls.agent = FraudiaAgentV2()
        cls.kb = KnowledgeService()

    def test_agent_v2_can_analyze_case(self):
        payload = self.agent.analyze_case('TC-X20')
        self.assertIn('claim', payload)
        self.assertIn('documents', payload)
        self.assertIn('recommended_actions', payload)
        self.assertTrue(payload['recommended_actions'])

    def test_rag_case_answer_returns_sources(self):
        payload = self.kb.answer_case('TC-X20', 'que evidencia documental tiene este caso')
        self.assertIn('sources', payload)
        self.assertTrue(payload['sources'])


if __name__ == '__main__':
    unittest.main()
