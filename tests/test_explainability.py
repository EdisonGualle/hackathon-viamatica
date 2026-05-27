import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from explainability.explain_score import build_case_explainability


class ExplainabilityTest(unittest.TestCase):
    def test_build_case_explainability_outputs_expected_artifacts(self):
        claim = {
            'id_siniestro': 'SIN-1',
            'id_poliza': 'POL-1',
            'id_proveedor': 'PRV-001',
        }
        score = {
            'reglas_activadas': '["RF-03", "S11"]',
            'detalle_reglas_json': '[{"codigo":"RF-03","evidencia":"Proveedor PRV-001 marcado en lista restrictiva.","variable_principal":"id_proveedor"}]',
            'score_reglas': 76,
            'score_ml': 40,
            'score_nlp': 20,
            'score_final': 76,
            'nivel': 'ROJO',
            'fecha_calculo': '2026-05-27T00:00:00',
            'scoring_breakdown_json': '{"weights":{"score_reglas":0.45}}',
        }
        docs = [
            {
                'id_documento': 'DOC-1',
                'inconsistencias_json': '[{"codigo":"DOC-FECHA-PREVIA","descripcion":"Factura previa al evento","severidad":"ALTA"}]',
            }
        ]
        payload = build_case_explainability(claim, score, docs)
        self.assertIn('reason_codes_json', payload)
        self.assertIn('evidence_bundle_json', payload)
        self.assertIn('counterfactual_json', payload)
        self.assertIn('audit_trail_json', payload)
        self.assertIn('explicacion_auditable', payload)
        self.assertIn('RF-03', payload['reason_codes_json'])
        self.assertIn('DOC-FECHA-PREVIA', payload['reason_codes_json'])


if __name__ == '__main__':
    unittest.main()
