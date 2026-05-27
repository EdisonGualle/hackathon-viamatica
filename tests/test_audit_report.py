import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from ingestion.load_data import DB_PATH
from review import generate_audit_report, initialize_review_state, record_case_review
from tests._bootstrap import ensure_pipeline


class AuditReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_pipeline()
        initialize_review_state(DB_PATH)

    def test_generate_audit_report_persists_report(self):
        record_case_review(DB_PATH, 'TC-X20', 'revision_documental', 'Prueba automatica', 'qa', 'pendiente soporte adicional')
        report = generate_audit_report(DB_PATH, 'TC-X20', 'qa')
        self.assertIn('TC-X20', report)
        self.assertIn('Explicación auditable', report)
        self.assertIn('revision_documental', report)


if __name__ == '__main__':
    unittest.main()
