import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from document_ai.service import analyze_document


class DocumentAITest(unittest.TestCase):
    def test_invoice_previous_to_event_is_detected(self):
        claim = {
            'id_siniestro': 'SIN-1',
            'fecha_ocurrencia': '2026-05-27',
            'monto_reclamado': 8000,
            'id_proveedor': 'PRV-001',
            'placa_vehiculo': 'ABC-123',
            'cobertura': 'Todo Riesgo',
        }
        document = {
            'id_documento': 'DOC-1',
            'id_siniestro': 'SIN-1',
            'tipo_documento': 'factura_taller',
            'presente': 1,
            'texto_ocr': 'FACTURA TALLER\nFecha emision: 2026-05-20\nProveedor: PRV-001\nMonto: 8000.00\nPlaca: ABC-123',
            'legibilidad_hint': 'alta',
            'file_path': '',
        }
        result = analyze_document(document, claim)
        codes = {item.codigo for item in result.inconsistencias}
        self.assertIn('DOC-FECHA-PREVIA', codes)
        self.assertGreater(result.document_score, 0)

    def test_missing_police_report_for_robbery_is_detected(self):
        claim = {
            'id_siniestro': 'SIN-2',
            'fecha_ocurrencia': '2026-05-27',
            'monto_reclamado': 10000,
            'id_proveedor': 'PRV-001',
            'placa_vehiculo': 'ABC-123',
            'cobertura': 'PTxRB',
        }
        document = {
            'id_documento': 'DOC-2',
            'id_siniestro': 'SIN-2',
            'tipo_documento': 'parte_policial',
            'presente': 0,
            'texto_ocr': '',
            'legibilidad_hint': 'alta',
            'file_path': '',
        }
        result = analyze_document(document, claim)
        codes = {item.codigo for item in result.inconsistencias}
        self.assertIn('DOC-DENUNCIA-AUSENTE', codes)


if __name__ == '__main__':
    unittest.main()
