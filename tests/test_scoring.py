import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from ingestion.load_data import run_pipeline


class ScoringPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = run_pipeline()

    def test_component_scales(self):
        for column in ['score_reglas', 'score_ml', 'score_nlp', 'score_final']:
            self.assertTrue(((self.df[column] >= 0) & (self.df[column] <= 100)).all(), column)

    def test_final_level_matches_thresholds_or_override(self):
        rojos = self.df[self.df['score_final'] >= 76]
        self.assertTrue((rojos['nivel'] == 'ROJO').all())
        verdes = self.df[self.df['score_final'] < 41]
        self.assertTrue(((verdes['nivel'] == 'VERDE') | (verdes['nivel'] == 'ROJO')).all())


if __name__ == '__main__':
    unittest.main()
