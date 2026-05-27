import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from tests._bootstrap import ensure_pipeline


class ScoringPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = ensure_pipeline()

    def test_component_scales(self):
        for column in ['score_reglas', 'score_ml', 'score_nlp', 'score_final']:
            self.assertTrue(((self.df[column] >= 0) & (self.df[column] <= 100)).all(), column)

    def test_final_level_matches_thresholds_or_override(self):
        rojos = self.df[self.df['score_final'] >= 76]
        self.assertTrue((rojos['nivel'] == 'ROJO').all())
        amarillos = self.df[(self.df['score_final'] > 40) & (self.df['score_final'] < 76)]
        self.assertTrue((amarillos['nivel'] == 'AMARILLO').all())
        verdes = self.df[self.df['score_final'] <= 40]
        self.assertTrue((verdes['nivel'] == 'VERDE').all())


if __name__ == '__main__':
    unittest.main()
