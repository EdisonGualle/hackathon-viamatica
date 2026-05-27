import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from rules.fraud_rules import calcular_score_reglas


class ExtendedRulesTest(unittest.TestCase):
    def setUp(self):
        self.siniestros = pd.DataFrame([
            {
                'id_siniestro': 'SIN-BASE',
                'id_poliza': 'POL-1',
                'id_proveedor': 'PRV-1',
                'id_asegurado': 'ASG-1',
                'ramo': 'Vehiculos',
                'cobertura': 'Todo Riesgo',
                'descripcion': 'Colision leve con tercero identificado y documentos consistentes.',
                'dias_inicio_poliza': 60,
                'dias_fin_poliza': 200,
                'dias_ocurr_reporte': 1,
                'documentos_completos': 1,
                'historial_siniestros': 0,
                'historial_vehiculo_18m': 0,
                'historial_conductor_18m': 0,
                'solo_rc_recurrente': 0,
                'sin_tercero_identificado': 0,
                'cambio_reciente_datos_asegurado': 0,
                'monto_reclamado': 8000,
                'actor_en_lista_restrictiva_tipo': '',
                'beneficiario_en_lista': 0,
            }
        ])
        self.polizas = pd.DataFrame([{'id_poliza': 'POL-1', 'suma_asegurada': 16000}])
        self.proveedores = pd.DataFrame([
            {'id_proveedor': 'PRV-1', 'en_lista_restrictiva': 0, 'pct_casos_observados': 0.1},
            {'id_proveedor': 'PRV-X', 'en_lista_restrictiva': 1, 'pct_casos_observados': 0.4},
        ])
        self.docs = pd.DataFrame([
            {'id_siniestro': 'SIN-BASE', 'inconsistencia_detectada': 0},
        ])
        self.asegurados = pd.DataFrame([
            {'id_asegurado': 'ASG-1', 'en_lista_restrictiva': 0},
            {'id_asegurado': 'ASG-X', 'en_lista_restrictiva': 1},
        ])

    def _score(self, **overrides):
        row = self.siniestros.iloc[0].copy()
        for key, value in overrides.items():
            row[key] = value
        return calcular_score_reglas(row, self.siniestros, self.polizas, self.proveedores, self.docs, self.asegurados)

    def test_rf01_requires_exact_ptxrb(self):
        red = self._score(cobertura='PTxRB')
        self.assertEqual(red.nivel, 'ROJO')
        self.assertTrue(any(item.codigo == 'RF-01' for item in red.reglas_activadas))

        clean = self._score(cobertura='Perdida Total')
        self.assertFalse(any(item.codigo == 'RF-01' for item in clean.reglas_activadas))

    def test_rf03_supports_actor_type(self):
        score = self._score(actor_en_lista_restrictiva_tipo='proveedor')
        self.assertTrue(any(item.codigo == 'RF-03' for item in score.reglas_activadas))
        self.assertEqual(score.nivel, 'ROJO')

    def test_signal_s14_amount_near_sum(self):
        score = self._score(monto_reclamado=15500)
        self.assertTrue(any(item.codigo == 'S14' for item in score.reglas_activadas))


if __name__ == '__main__':
    unittest.main()
