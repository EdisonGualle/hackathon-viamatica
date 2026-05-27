from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_SAMPLE_DIR = ROOT / 'data' / 'synthetic' / 'document_samples'


def _claim_number(claim_id: str) -> int:
    digits = ''.join(ch for ch in str(claim_id) if ch.isdigit())
    if digits:
        return int(digits[-6:])
    return sum(ord(ch) for ch in str(claim_id))


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _date(value: object) -> datetime:
    if value:
        return datetime.fromisoformat(str(value))
    return datetime(2026, 5, 27)


def _doc_profiles(claim: pd.Series) -> dict[str, dict]:
    claim_id = str(claim['id_siniestro'])
    desc = str(claim.get('descripcion') or '').lower()
    cobertura = str(claim.get('cobertura') or '').lower()
    documentos_completos = bool(int(claim.get('documentos_completos', 1) or 0))
    monto_reclamado = _safe_float(claim.get('monto_reclamado'))
    fecha_evento = _date(claim.get('fecha_ocurrencia'))
    dias_reporte = _safe_int(claim.get('dias_ocurr_reporte'))
    provider = str(claim.get('id_proveedor') or '')
    plate = str(claim.get('placa_vehiculo') or '')

    is_test_case = claim_id.startswith('TC-')
    if is_test_case:
        doc_inconsistent = claim_id in {'TC-RF02-P', 'TC-S11', 'TC-C06', 'TC-X20', 'TC-X05'}
        missing_police = cobertura == 'ptxrb' and claim_id in {'TC-RF06-P', 'TC-A05', 'TC-C02'}
        illegible = any(token in claim_id for token in ['TC-S08'])
        provider_mismatch = claim_id in {'TC-X20', 'TC-C06'}
        plate_mismatch = False
        monto_mismatch = claim_id in {'TC-S11', 'TC-X20'}
    else:
        doc_inconsistent = (
            'inconsistenc' in desc
            or 'falsific' in desc
            or 'adulter' in desc
            or claim_id.endswith(('7', '9'))
        )
        missing_police = cobertura == 'ptxrb' and (not documentos_completos or dias_reporte > 4)
        illegible = (not documentos_completos and claim_id.endswith(('4', '8'))) or claim_id.endswith('18')
        provider_mismatch = claim_id.endswith(('20', '06'))
        plate_mismatch = claim_id.endswith('10')
        monto_mismatch = monto_reclamado >= 15000 and (doc_inconsistent or not documentos_completos)

    invoice_date = fecha_evento + timedelta(days=1) if claim_id == 'TC-S11' else (fecha_evento - timedelta(days=6) if doc_inconsistent else fecha_evento + timedelta(days=1))
    police_event_date = fecha_evento - timedelta(days=1) if any(token in claim_id for token in ['X15']) else fecha_evento
    police_report_date = fecha_evento + timedelta(days=max(dias_reporte, 1))
    monto_doc = round(monto_reclamado * (0.62 if monto_mismatch else 0.98), 2)
    proveedor_doc = 'PRV-888' if provider_mismatch else provider
    placa_doc = 'ZZZ-999' if plate_mismatch else plate
    texto_ruido = 'ILEGIBLE ### BORRADO ###' if illegible else ''

    return {
        'aviso_siniestro': {
            'presente': True,
            'legibilidad_hint': 'media' if illegible else 'alta',
            'fecha_emision': fecha_evento.strftime('%Y-%m-%d'),
            'fecha_evento_doc': fecha_evento.strftime('%Y-%m-%d'),
            'monto_doc': monto_reclamado,
            'proveedor_doc': provider,
            'placa_doc': plate,
            'texto_documento': (
                f"AVISO DE SINIESTRO\nSiniestro: {claim_id}\nCobertura: {claim.get('cobertura')}\n"
                f"Fecha evento: {fecha_evento:%Y-%m-%d}\nMonto reclamado: {monto_reclamado:.2f}\n"
                f"Placa: {plate}\nNarrativa: {claim.get('descripcion')}\n{texto_ruido}"
            ).strip(),
        },
        'factura_taller': {
            'presente': True,
            'legibilidad_hint': 'baja' if illegible else 'alta',
            'fecha_emision': invoice_date.strftime('%Y-%m-%d'),
            'fecha_evento_doc': fecha_evento.strftime('%Y-%m-%d'),
            'monto_doc': monto_doc,
            'proveedor_doc': proveedor_doc,
            'placa_doc': placa_doc,
            'texto_documento': (
                f"FACTURA TALLER\nNumero: FAC-{claim_id}\nFecha emision: {invoice_date:%Y-%m-%d}\n"
                f"Proveedor: {proveedor_doc}\nMonto: {monto_doc:.2f}\nPlaca: {placa_doc}\n"
                f"Referencia siniestro: {claim_id}\n{texto_ruido}"
            ).strip(),
        },
        'parte_policial': {
            'presente': not missing_police,
            'legibilidad_hint': 'media' if illegible else 'alta',
            'fecha_emision': police_report_date.strftime('%Y-%m-%d'),
            'fecha_evento_doc': police_event_date.strftime('%Y-%m-%d'),
            'monto_doc': None,
            'proveedor_doc': '',
            'placa_doc': placa_doc,
            'texto_documento': (
                f"DENUNCIA POLICIAL\nSiniestro: {claim_id}\nFecha evento: {police_event_date:%Y-%m-%d}\n"
                f"Fecha denuncia: {police_report_date:%Y-%m-%d}\nPlaca: {placa_doc}\nLugar: {claim.get('ciudad')}\n{texto_ruido}"
            ).strip(),
        },
        'informe_pericial': {
            'presente': cobertura == 'ptxrb' or monto_reclamado >= 12000,
            'legibilidad_hint': 'alta',
            'fecha_emision': (fecha_evento + timedelta(days=2)).strftime('%Y-%m-%d'),
            'fecha_evento_doc': fecha_evento.strftime('%Y-%m-%d'),
            'monto_doc': monto_reclamado,
            'proveedor_doc': provider,
            'placa_doc': plate,
            'texto_documento': (
                f"INFORME PERICIAL\nCaso: {claim_id}\nFecha inspeccion: {(fecha_evento + timedelta(days=2)):%Y-%m-%d}\n"
                f"Placa: {plate}\nMonto estimado: {monto_reclamado:.2f}\nResultado: dano verificado."
            ).strip(),
        },
        'cedula': {
            'presente': documentos_completos,
            'legibilidad_hint': 'alta',
            'fecha_emision': fecha_evento.strftime('%Y-%m-%d'),
            'fecha_evento_doc': fecha_evento.strftime('%Y-%m-%d'),
            'monto_doc': None,
            'proveedor_doc': '',
            'placa_doc': '',
            'texto_documento': f"IDENTIFICACION\nAsegurado: {claim.get('id_asegurado')}\nDocumento valido.",
        },
    }


def build_document_records_from_claims(siniestros: pd.DataFrame) -> pd.DataFrame:
    DOCUMENT_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for _, claim in siniestros.iterrows():
        claim_id = str(claim['id_siniestro'])
        claim_dir = DOCUMENT_SAMPLE_DIR / claim_id
        claim_dir.mkdir(parents=True, exist_ok=True)
        for doc_type, profile in _doc_profiles(claim).items():
            present = bool(profile['presente'])
            file_name = f"{doc_type}.txt"
            file_path = claim_dir / file_name
            text = profile['texto_documento'] if present else ''
            if present:
                file_path.write_text(text, encoding='utf-8')
            rows.append(
                {
                    'id_documento': f'DOC-{claim_id}-{doc_type}',
                    'id_siniestro': claim_id,
                    'tipo_documento': doc_type,
                    'nombre_archivo': file_name,
                    'file_path': str(file_path),
                    'presente': 1 if present else 0,
                    'texto_documento': text,
                    'texto_ocr': text,
                    'legibilidad_hint': profile['legibilidad_hint'],
                    'fecha_emision': profile['fecha_emision'],
                    'fecha_evento_doc': profile['fecha_evento_doc'],
                    'monto_doc': profile['monto_doc'],
                    'proveedor_doc': profile['proveedor_doc'],
                    'placa_doc': profile['placa_doc'],
                    'inconsistencia_seed': 0,
                    'inconsistencia_detectada': 0,
                }
            )
    return pd.DataFrame(rows)


def build_vehiculos_from_claims(siniestros: pd.DataFrame) -> pd.DataFrame:
    unique = siniestros[['id_vehiculo', 'placa_vehiculo', 'chasis_vehiculo']].drop_duplicates().copy()
    if unique.empty:
        return pd.DataFrame(columns=['id_vehiculo', 'placa', 'chasis', 'marca', 'modelo', 'anio'])
    marcas = ['Chevrolet', 'Kia', 'Toyota', 'Hyundai', 'Mazda']
    modelos = ['Sedan', 'SUV', 'Pickup', 'Hatchback', 'Camioneta']
    rows = []
    for idx, row in enumerate(unique.itertuples(index=False), start=1):
        rows.append(
            {
                'id_vehiculo': row.id_vehiculo,
                'placa': row.placa_vehiculo,
                'chasis': row.chasis_vehiculo,
                'marca': marcas[(idx - 1) % len(marcas)],
                'modelo': modelos[(idx - 1) % len(modelos)],
                'anio': 2016 + ((idx - 1) % 8),
            }
        )
    return pd.DataFrame(rows)


def build_beneficiarios_from_claims(siniestros: pd.DataFrame) -> pd.DataFrame:
    unique = siniestros[['id_beneficiario', 'beneficiario_en_lista']].drop_duplicates().copy()
    rows = []
    for row in unique.itertuples(index=False):
        rows.append(
            {
                'id_beneficiario': row.id_beneficiario,
                'nombre': f'Beneficiario {row.id_beneficiario}',
                'en_lista_restrictiva': int(row.beneficiario_en_lista or 0),
            }
        )
    return pd.DataFrame(rows)
