import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from scoring import ComponentScores, compute_assessment, recommend_action_for_level, score_simulated_claim


class ScoringServiceTest(unittest.TestCase):
    def test_formula_uses_canonical_weights(self):
        assessment = compute_assessment(
            ComponentScores(score_reglas=100, score_ml=50, score_nlp=20),
            active_rules=[],
        )
        self.assertEqual(assessment.score_final, 68.0)
        self.assertEqual(assessment.nivel_final, 'AMARILLO')

    def test_critical_rule_forces_red(self):
        assessment = compute_assessment(
            ComponentScores(score_reglas=10, score_ml=0, score_nlp=0),
            active_rules=['RF-03'],
        )
        self.assertEqual(assessment.nivel_final, 'ROJO')
        self.assertTrue(assessment.critical_override)
        self.assertGreaterEqual(assessment.score_final, 76.0)
        self.assertIn('RF-03', assessment.breakdown.critical_rules_triggered)

    def test_recommendation_is_owned_by_scoring(self):
        self.assertEqual(
            recommend_action_for_level('ROJO'),
            'Escalar a revisión especializada reforzada.',
        )
        self.assertEqual(
            recommend_action_for_level('AMARILLO'),
            'Revisión documental prioritaria por Unidad Antifraude.',
        )

    def test_simulated_claim_uses_same_source_of_truth(self):
        result = score_simulated_claim(
            score_reglas=12,
            score_ml=10,
            score_nlp=5,
            active_rules=['RF-02'],
            factores=['factor demo'],
            ratio_pct=42.0,
            rule_details=[{'codigo': 'RF-02', 'critico': True}],
        )
        self.assertEqual(result['nivel'], 'ROJO')
        self.assertGreaterEqual(result['score_final'], 76.0)
        self.assertEqual(result['accion'], 'Escalar a revisión especializada reforzada.')
        self.assertEqual(result['criticas'], ['RF-02'])


if __name__ == '__main__':
    unittest.main()
