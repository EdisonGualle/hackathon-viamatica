import os
import sys
import unittest

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from rules.fraud_rules import calcular_score_reglas


def _base_row(**overrides):
    row = {
        "id_siniestro": "SIN-TEST",
        "id_poliza": "POL-TEST",
        "id_proveedor": "PRV-OK",
        "ramo": "Vehiculos",
        "cobertura": "Choque",
        "descripcion": "Choque leve con soporte completo",
        "dias_inicio_poliza": 120,
        "dias_fin_poliza": 120,
        "dias_ocurr_reporte": 1,
        "documentos_completos": 1,
        "historial_siniestros": 0,
        "monto_reclamado": 1000,
    }
    row.update(overrides)
    return pd.Series(row)


def _fixtures():
    siniestros = pd.DataFrame([_base_row().to_dict()])
    polizas = pd.DataFrame([{"id_poliza": "POL-TEST", "suma_asegurada": 50000}])
    proveedores = pd.DataFrame([
        {"id_proveedor": "PRV-OK", "en_lista_restrictiva": 0, "pct_casos_observados": 0.0},
        {"id_proveedor": "PRV-BLOCK", "en_lista_restrictiva": 1, "pct_casos_observados": 0.8},
    ])
    docs = pd.DataFrame([{
        "id_siniestro": "SIN-TEST",
        "inconsistencia_detectada": 0,
        "entregado": 1,
    }])
    return siniestros, polizas, proveedores, docs


def _score(row):
    siniestros, polizas, proveedores, docs = _fixtures()
    return calcular_score_reglas(row, siniestros, polizas, proveedores, docs)


class FraudRulesTest(unittest.TestCase):
    def test_rf01_perdida_total_robo_forces_red(self):
        result = _score(_base_row(cobertura="Perdida Total por Robo"))
        self.assertEqual(result.nivel, "ROJO")
        self.assertTrue(any(r.codigo == "RF-01" for r in result.reglas_activadas))

    def test_rf03_restrictive_provider_forces_red(self):
        result = _score(_base_row(id_proveedor="PRV-BLOCK"))
        self.assertEqual(result.nivel, "ROJO")
        self.assertTrue(any(r.codigo == "RF-03" for r in result.reglas_activadas))

    def test_rf04_impossible_dynamics_forces_red(self):
        result = _score(_base_row(descripcion="Relato imposible y sin rastro del tercero"))
        self.assertEqual(result.nivel, "ROJO")
        self.assertTrue(any(r.codigo == "RF-04" for r in result.reglas_activadas))

    def test_policy_border_activates_yellow_signal(self):
        result = _score(_base_row(dias_inicio_poliza=1, dias_fin_poliza=300))
        self.assertTrue(any(r.codigo == "RF-05" for r in result.reglas_activadas))
        self.assertTrue(any(r.codigo == "S01" for r in result.reglas_activadas))

    def test_clean_case_remains_green(self):
        result = _score(_base_row())
        self.assertEqual(result.nivel, "VERDE")
        self.assertEqual(result.score_reglas, 0)


if __name__ == "__main__":
    unittest.main()
