import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from rag.knowledge_service import KnowledgeService


class RagTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeService()

    def test_retrieves_rf03_definition(self):
        answer = self.kb.answer('que significa RF-03')
        self.assertTrue(answer['sources'])
        joined = ' '.join(answer['sources'])
        self.assertIn('reglas_canonicas', joined)

    def test_returns_sources(self):
        payload = self.kb.query('que evidencia revisar en RF-02')
        self.assertTrue(payload['citations'])


if __name__ == '__main__':
    unittest.main()
