from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / 'data' / 'synthetic'
DB_PATH = ROOT / 'fraudia.db'
TEST_CASES_PATH = DATA_DIR / 'test_cases_rules.csv'

NARRATIVES_NORMAL = [
    'Colision leve en interseccion con danos en defensa delantera y guardafango.',
    'Impacto por alcance en trafico lento con declaracion consistente del conductor.',
    'Rotura de parabrisas por proyeccion de piedra en carretera interprovincial.',
    'Afectacion por inundacion parcial en parqueadero luego de lluvia intensa.',
    'Choque lateral con tercero identificado y parte policial disponible.',
    'Daño menor en puerta posterior por maniobra de estacionamiento en centro comercial.',
]

NARRATIVES_SUSPICIOUS = [
    'El vehiculo aparecio abandonado sin rastro del tercero y con version poco consistente.',
    'El conductor reporta un impacto imposible de reconstruir con los danos observados.',
    'La narrativa presenta vacios relevantes sobre lugar, hora y tercero involucrado.',
    'Se reporta robo total con demora relevante y cambios recientes del asegurado.',
    'Existen inconsistencias entre la declaracion inicial y los documentos adjuntos.',
]

NARRATIVES_CLONED = [
    'El asegurado indica que dejo el vehiculo estacionado y al retornar ya no se encontraba en el lugar.',
    'El asegurado indica que dejo el vehiculo estacionado y al retornar ya no se encontraba en el lugar.',
    'El asegurado indica que dejo el vehiculo estacionado y al retornar ya no se encontraba en el lugar.',
]

DOCUMENT_TYPES = ['parte_policial', 'matricula', 'cedula', 'factura_taller', 'aviso_siniestro']
COVERAGES = ['RC', 'Todo Riesgo', 'PTxRB', 'Cristales', 'Inundacion']
BRANCHES = ['Vehiculos', 'Vehiculos', 'Vehiculos', 'Patrimoniales']
CITIES = ['Quito', 'Guayaquil', 'Cuenca', 'Manta', 'Ambato']


def build_asegurados(n: int = 24) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                'id_asegurado': f'ASG-{i:03d}',
                'nombre': f'Asegurado {i:03d}',
                'edad': random.randint(24, 72),
                'ciudad': random.choice(CITIES),
                'historial_siniestros': random.randint(0, 4),
                'cambio_reciente_datos_asegurado': 1 if i % 7 == 0 else 0,
                'en_lista_restrictiva': 1 if i in {22, 24} else 0,
            }
        )
    return pd.DataFrame(rows)


def build_proveedores(n: int = 20) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        pct_observados = round(random.uniform(0.03, 0.34), 2)
        if i == 13:
            pct_observados = 0.28
        if i == 20:
            pct_observados = 0.24
        rows.append(
            {
                'id_proveedor': f'PRV-{i:03d}',
                'nombre': f'Proveedor {i:03d}',
                'tipo': random.choice(['taller', 'grua', 'perito', 'clinica']),
                'en_lista_restrictiva': 1 if i in {3, 9} else 0,
                'pct_casos_observados': pct_observados,
            }
        )
    return pd.DataFrame(rows)


def build_polizas(asegurados: pd.DataFrame, n: int = 36) -> pd.DataFrame:
    rows = []
    today = datetime(2026, 5, 27)
    for i in range(1, n + 1):
        insured = asegurados.iloc[(i - 1) % len(asegurados)]
        start = today - timedelta(days=random.randint(20, 360))
        end = start + timedelta(days=365)
        ramo = random.choice(BRANCHES)
        cobertura = random.choice(COVERAGES if ramo == 'Vehiculos' else ['Incendio', 'Robo Contenido'])
        rows.append(
            {
                'id_poliza': f'POL-{i:03d}',
                'id_asegurado': insured['id_asegurado'],
                'ramo': ramo,
                'cobertura': cobertura,
                'inicio_vigencia': start.strftime('%Y-%m-%d'),
                'fin_vigencia': end.strftime('%Y-%m-%d'),
                'suma_asegurada': random.randint(8000, 45000),
                'prima': random.randint(350, 2200),
            }
        )
    return pd.DataFrame(rows)


def build_conductores(n: int = 24) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                'id_conductor': f'CON-{i:03d}',
                'nombre': f'Conductor {i:03d}',
                'edad': random.randint(21, 68),
                'historial_conductor_18m': random.randint(0, 4),
            }
        )
    return pd.DataFrame(rows)


def build_claim_row(index: int, poliza: pd.Series, asegurado: pd.Series, proveedor: pd.Series, conductor: pd.Series) -> dict:
    occurrence = datetime(2026, 5, 27) - timedelta(days=random.randint(0, 180))
    start = datetime.fromisoformat(poliza['inicio_vigencia'])
    end = datetime.fromisoformat(poliza['fin_vigencia'])
    dias_inicio = max((occurrence - start).days, 0)
    dias_fin = max((end - occurrence).days, 0)
    narrative_pool = NARRATIVES_NORMAL
    if index % 9 == 0:
        narrative_pool = NARRATIVES_SUSPICIOUS
    if index % 11 == 0:
        narrative_pool = NARRATIVES_CLONED
    description = random.choice(narrative_pool)
    coverage = poliza['cobertura']
    if index % 13 == 0:
        coverage = 'PTxRB'
    ramo = poliza['ramo']
    monto = random.randint(1200, int(poliza['suma_asegurada'] * 0.98))
    return {
        'id_siniestro': f'SIN-{index:04d}',
        'id_poliza': poliza['id_poliza'],
        'id_asegurado': asegurado['id_asegurado'],
        'id_proveedor': proveedor['id_proveedor'],
        'id_conductor': conductor['id_conductor'],
        'id_beneficiario': f'BEN-{((index - 1) % 10) + 1:03d}',
        'ramo': ramo,
        'cobertura': coverage,
        'ciudad': asegurado['ciudad'],
        'fecha_ocurrencia': occurrence.strftime('%Y-%m-%d'),
        'fecha_reporte': (occurrence + timedelta(days=random.randint(0, 8))).strftime('%Y-%m-%d'),
        'dias_ocurr_reporte': random.randint(0, 8),
        'dias_inicio_poliza': dias_inicio,
        'dias_fin_poliza': dias_fin,
        'monto_reclamado': monto,
        'documentos_completos': 0 if index % 8 == 0 else 1,
        'descripcion': description,
        'historial_siniestros': int(asegurado['historial_siniestros']),
        'historial_vehiculo_18m': random.randint(0, 4),
        'historial_conductor_18m': int(conductor['historial_conductor_18m']),
        'solo_rc_recurrente': 1 if index % 10 == 0 else 0,
        'sin_tercero_identificado': 1 if index % 7 == 0 else 0,
        'cambio_reciente_datos_asegurado': int(asegurado['cambio_reciente_datos_asegurado']),
        'actor_en_lista_restrictiva_tipo': 'proveedor' if proveedor['en_lista_restrictiva'] else ('asegurado' if asegurado['en_lista_restrictiva'] else ''),
        'beneficiario_en_lista': 1 if index % 19 == 0 else 0,
    }


def build_siniestros(polizas: pd.DataFrame, asegurados: pd.DataFrame, proveedores: pd.DataFrame, conductores: pd.DataFrame, n: int = 96) -> pd.DataFrame:
    rows = []
    for idx in range(1, n + 1):
        poliza = polizas.iloc[(idx - 1) % len(polizas)]
        asegurado = asegurados[asegurados['id_asegurado'] == poliza['id_asegurado']].iloc[0]
        proveedor = proveedores.iloc[(idx * 3) % len(proveedores)]
        conductor = conductores.iloc[(idx * 5) % len(conductores)]
        row = build_claim_row(idx, poliza, asegurado, proveedor, conductor)
        if idx % 15 == 0:
            row['descripcion'] = 'El conductor reporta un impacto imposible de reconstruir con los danos observados.'
        if idx % 17 == 0:
            row['dias_ocurr_reporte'] = 6
            row['cobertura'] = 'PTxRB'
        rows.append(row)
    return pd.DataFrame(rows)


def build_documentos(siniestros: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, sin in siniestros.iterrows():
        for doc in DOCUMENT_TYPES:
            inconsistente = 1 if (doc in {'factura_taller', 'parte_policial'} and sin['id_siniestro'].endswith(('7', '9'))) else 0
            rows.append(
                {
                    'id_documento': f"DOC-{sin['id_siniestro']}-{doc}",
                    'id_siniestro': sin['id_siniestro'],
                    'tipo_documento': doc,
                    'inconsistencia_detectada': inconsistente,
                }
            )
    return pd.DataFrame(rows)


def build_test_cases() -> pd.DataFrame:
    cases = []

    def add(case_id: str, objetivo: str, rule_id: str, nivel: str, tipo: str, **kwargs):
        base = {
            'id_siniestro': case_id,
            'objetivo': objetivo,
            'regla_esperada': rule_id,
            'nivel_esperado': nivel,
            'tipo_caso': tipo,
            'id_poliza': f'POL-{case_id}',
            'id_asegurado': f'ASG-{case_id}',
            'id_proveedor': 'PRV-001',
            'id_conductor': f'CON-{case_id}',
            'id_beneficiario': f'BEN-{case_id}',
            'ramo': 'Vehiculos',
            'cobertura': 'Todo Riesgo',
            'ciudad': 'Quito',
            'dias_inicio_poliza': 45,
            'dias_fin_poliza': 180,
            'dias_ocurr_reporte': 1,
            'historial_siniestros': 0,
            'historial_vehiculo_18m': 0,
            'historial_conductor_18m': 0,
            'solo_rc_recurrente': 0,
            'sin_tercero_identificado': 0,
            'cambio_reciente_datos_asegurado': 0,
            'documentos_completos': 1,
            'monto_reclamado': 8000,
            'suma_asegurada': 16000,
            'actor_en_lista_restrictiva_tipo': '',
            'beneficiario_en_lista': 0,
            'descripcion': 'Colision leve con tercero identificado y documentos consistentes.',
        }
        base.update(kwargs)
        cases.append(base)

    add('TC-RF01-P', 'PTxRB activa RF-01', 'RF-01', 'ROJO', 'positivo', cobertura='PTxRB')
    add('TC-RF01-N', 'Perdida total generica no activa RF-01', 'RF-01', 'VERDE', 'negativo', cobertura='Perdida Total')
    add('TC-RF02-P', 'Documento inconsistente activa RF-02', 'RF-02', 'ROJO', 'positivo', descripcion='Version con inconsistencia documental evidente.')
    add('TC-RF02-N', 'Documentos consistentes no activan RF-02', 'RF-02', 'VERDE', 'negativo')
    add('TC-RF03-P', 'Proveedor en lista activa RF-03', 'RF-03', 'ROJO', 'positivo', actor_en_lista_restrictiva_tipo='proveedor')
    add('TC-RF03-N', 'Actor limpio no activa RF-03', 'RF-03', 'VERDE', 'negativo')
    add('TC-RF04-P', 'Dinamica imposible activa RF-04', 'RF-04', 'ROJO', 'positivo', descripcion='El conductor reporta un impacto imposible de reconstruir con los danos observados.')
    add('TC-RF04-N', 'Dinamica consistente no activa RF-04', 'RF-04', 'VERDE', 'negativo')
    add('TC-RF05-P', 'Borde de vigencia activa RF-05', 'RF-05', 'AMARILLO', 'positivo', dias_inicio_poliza=1)
    add('TC-RF05-N', 'Sin borde de vigencia no activa RF-05', 'RF-05', 'VERDE', 'negativo', dias_inicio_poliza=50)
    add('TC-RF06-P', 'Demora de robo activa RF-06', 'RF-06', 'AMARILLO', 'positivo', cobertura='PTxRB', dias_ocurr_reporte=6)
    add('TC-RF06-N', 'Robo reportado rapido no activa RF-06', 'RF-06', 'VERDE', 'negativo', cobertura='PTxRB', dias_ocurr_reporte=1)
    add('TC-RF07-P', 'Narrativa clonada activa RF-07', 'RF-07', 'AMARILLO', 'positivo', descripcion=NARRATIVES_CLONED[0])
    add('TC-RF07-N', 'Narrativa distinta no activa RF-07', 'RF-07', 'VERDE', 'negativo', descripcion=NARRATIVES_NORMAL[0])

    signal_specs = [
        ('TC-S01', 'S01', 'AMARILLO', dict(dias_inicio_poliza=4)),
        ('TC-S02', 'S02', 'AMARILLO', dict(dias_ocurr_reporte=8)),
        ('TC-S03', 'S03', 'AMARILLO', dict(historial_siniestros=4)),
        ('TC-S04', 'S04', 'AMARILLO', dict(historial_vehiculo_18m=3)),
        ('TC-S05', 'S05', 'AMARILLO', dict(historial_conductor_18m=3)),
        ('TC-S06', 'S06', 'AMARILLO', dict(solo_rc_recurrente=1, cobertura='RC')),
        ('TC-S07', 'S07', 'AMARILLO', dict(actor_en_lista_restrictiva_tipo='proveedor')),
        ('TC-S08', 'S08', 'AMARILLO', dict(documentos_completos=0)),
        ('TC-S09', 'S09', 'AMARILLO', dict(descripcion='La narrativa presenta vacios relevantes sobre lugar, hora y tercero involucrado.')),
        ('TC-S10', 'S10', 'AMARILLO', dict(sin_tercero_identificado=1)),
        ('TC-S11', 'S11', 'AMARILLO', dict(descripcion='Existen inconsistencias entre la declaracion inicial y los documentos adjuntos.')),
        ('TC-S12', 'S12', 'AMARILLO', dict(dias_ocurr_reporte=5)),
        ('TC-S13', 'S13', 'AMARILLO', dict(descripcion=NARRATIVES_CLONED[0])),
        ('TC-S14', 'S14', 'AMARILLO', dict(monto_reclamado=15400, suma_asegurada=16000)),
    ]
    for case_id, rule_id, nivel, payload in signal_specs:
        add(case_id, f'Caso dirigido para {rule_id}', rule_id, nivel, 'positivo', **payload)

    combo_specs = [
        ('TC-C01', 'RF-03 + S08', 'ROJO', dict(actor_en_lista_restrictiva_tipo='proveedor', documentos_completos=0)),
        ('TC-C02', 'RF-01 + RF-06', 'ROJO', dict(cobertura='PTxRB', dias_ocurr_reporte=7)),
        ('TC-C03', 'RF-04 + S10', 'ROJO', dict(descripcion='El conductor reporta un impacto imposible de reconstruir con los danos observados.', sin_tercero_identificado=1)),
        ('TC-C04', 'S03 + S04 + S05', 'AMARILLO', dict(historial_siniestros=4, historial_vehiculo_18m=3, historial_conductor_18m=3)),
        ('TC-C05', 'S12 + S14', 'AMARILLO', dict(dias_ocurr_reporte=6, monto_reclamado=15800, suma_asegurada=16000)),
        ('TC-C06', 'RF-02 + RF-03', 'ROJO', dict(actor_en_lista_restrictiva_tipo='proveedor', descripcion='Existen inconsistencias entre la declaracion inicial y los documentos adjuntos.')),
    ]
    for case_id, objetivo, nivel, payload in combo_specs:
        add(case_id, objetivo, objetivo, nivel, 'combinado', **payload)

    clean_specs = [
        'TC-N01', 'TC-N02', 'TC-N03', 'TC-N04'
    ]
    for case_id in clean_specs:
        add(case_id, 'Caso limpio de control', 'NINGUNA', 'VERDE', 'limpio')

    agent_specs = [
        ('TC-A01', 'caso con proveedor observado para preguntas del agente', 'RF-03', 'ROJO', dict(actor_en_lista_restrictiva_tipo='proveedor')),
        ('TC-A02', 'caso con narrativa clonada para preguntas del agente', 'RF-07', 'AMARILLO', dict(descripcion=NARRATIVES_CLONED[0])),
        ('TC-A03', 'caso con monto atipico para preguntas del agente', 'S14', 'AMARILLO', dict(monto_reclamado=15900, suma_asegurada=16000)),
        ('TC-A04', 'caso con borde de vigencia para preguntas del agente', 'RF-05', 'AMARILLO', dict(dias_inicio_poliza=1)),
        ('TC-A05', 'caso con demora de robo para preguntas del agente', 'RF-06', 'AMARILLO', dict(cobertura='PTxRB', dias_ocurr_reporte=7)),
    ]
    for case_id, objetivo, rule_id, nivel, payload in agent_specs:
        add(case_id, objetivo, rule_id, nivel, 'agente', **payload)

    extra_specs = [
        ('TC-X01', 'Concentrar alertas rojas en PRV-003 para dashboard', 'RF-03', 'ROJO', 'dashboard', dict(id_proveedor='PRV-003', actor_en_lista_restrictiva_tipo='proveedor', ciudad='Quito')),
        ('TC-X02', 'Concentrar alertas rojas en PRV-003 para red', 'RF-04', 'ROJO', 'red', dict(id_proveedor='PRV-003', descripcion='El conductor reporta un impacto imposible de reconstruir con los danos observados.', ciudad='Quito')),
        ('TC-X03', 'Concentrar alertas rojas en PRV-009 para dashboard', 'RF-03', 'ROJO', 'dashboard', dict(id_proveedor='PRV-009', actor_en_lista_restrictiva_tipo='proveedor', ciudad='Guayaquil')),
        ('TC-X04', 'Proveedor recurrente y documentos faltantes', 'S07', 'AMARILLO', 'dashboard', dict(id_proveedor='PRV-013', documentos_completos=0, dias_ocurr_reporte=5, ciudad='Guayaquil')),
        ('TC-X05', 'Ciudad Quito con combinacion critica', 'RF-02', 'ROJO', 'dashboard', dict(ciudad='Quito', descripcion='Existen inconsistencias entre la declaracion inicial y los documentos adjuntos.')),
        ('TC-X06', 'Ciudad Guayaquil con robo tardio critico', 'RF-06', 'ROJO', 'dashboard', dict(ciudad='Guayaquil', cobertura='PTxRB', dias_ocurr_reporte=6)),
        ('TC-X07', 'Caso de monto extremo para bandeja', 'S14', 'AMARILLO', 'bandeja', dict(monto_reclamado=15950, suma_asegurada=16000, dias_ocurr_reporte=5, documentos_completos=0, ciudad='Cuenca')),
        ('TC-X08', 'Caso limpio de control adicional para dashboard', 'NINGUNA', 'VERDE', 'limpio', dict(ciudad='Manta')),
        ('TC-X09', 'Asegurado en lista restrictiva', 'RF-03', 'ROJO', 'bandeja', dict(id_asegurado='ASG-X09', actor_en_lista_restrictiva_tipo='asegurado', ciudad='Quito')),
        ('TC-X10', 'Beneficiario en lista restrictiva', 'RF-03', 'ROJO', 'bandeja', dict(beneficiario_en_lista=1, ciudad='Ambato')),
        ('TC-X11', 'Solo RC recurrente con historial', 'S06', 'AMARILLO', 'score', dict(cobertura='RC', solo_rc_recurrente=1, historial_siniestros=3, ciudad='Manta')),
        ('TC-X12', 'Vehiculo y conductor recurrentes', 'S04', 'AMARILLO', 'score', dict(historial_vehiculo_18m=4, historial_conductor_18m=4, ciudad='Cuenca')),
        ('TC-X13', 'Narrativa clonada para red de relaciones', 'RF-07', 'AMARILLO', 'red', dict(descripcion=NARRATIVES_CLONED[0], dias_ocurr_reporte=5, documentos_completos=0, ciudad='Quito')),
        ('TC-X14', 'Narrativa clonada espejo para red de relaciones', 'RF-07', 'AMARILLO', 'red', dict(descripcion=NARRATIVES_CLONED[0], dias_ocurr_reporte=5, documentos_completos=0, ciudad='Quito')),
        ('TC-X15', 'Sin tercero identificado y dinamica sospechosa', 'S10', 'AMARILLO', 'score', dict(sin_tercero_identificado=1, historial_siniestros=2, documentos_completos=0, descripcion='La narrativa presenta vacios relevantes sobre lugar, hora y tercero involucrado.', ciudad='Guayaquil')),
        ('TC-X16', 'Cambio reciente del asegurado y robo total', 'RF-01', 'ROJO', 'agente', dict(cobertura='PTxRB', cambio_reciente_datos_asegurado=1, dias_ocurr_reporte=5, ciudad='Quito')),
        ('TC-X17', 'Borde exacto de vigencia y documentos completos', 'RF-05', 'AMARILLO', 'simulador', dict(dias_inicio_poliza=1, dias_fin_poliza=364, documentos_completos=0, dias_ocurr_reporte=4, ciudad='Cuenca')),
        ('TC-X18', 'Reporte tardio sin critica para simulador', 'S12', 'AMARILLO', 'simulador', dict(dias_ocurr_reporte=8, documentos_completos=0, ciudad='Ambato')),
        ('TC-X19', 'Proveedor observado y monto alto para simulador', 'RF-03', 'ROJO', 'simulador', dict(id_proveedor='PRV-003', actor_en_lista_restrictiva_tipo='proveedor', monto_reclamado=15800, suma_asegurada=16000, ciudad='Quito')),
        ('TC-X20', 'Caso integral para agente y cumplimiento', 'RF-02', 'ROJO', 'agente', dict(id_proveedor='PRV-009', actor_en_lista_restrictiva_tipo='proveedor', descripcion='Existen inconsistencias entre la declaracion inicial y los documentos adjuntos.', dias_ocurr_reporte=6, documentos_completos=0, ciudad='Guayaquil')),
    ]
    for case_id, objetivo, rule_id, nivel, tipo, payload in extra_specs:
        add(case_id, objetivo, rule_id, nivel, tipo, **payload)

    return pd.DataFrame(cases)


def build_test_case_asegurados(test_cases: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {
            'id_asegurado': row['id_asegurado'],
            'nombre': f"Asegurado {row['id_asegurado']}",
            'edad': 39,
            'ciudad': row.get('ciudad', 'Quito'),
            'historial_siniestros': int(row.get('historial_siniestros', 0)),
            'cambio_reciente_datos_asegurado': int(row.get('cambio_reciente_datos_asegurado', 0)),
            'en_lista_restrictiva': 1 if row.get('actor_en_lista_restrictiva_tipo') == 'asegurado' else 0,
        }
        for _, row in test_cases.iterrows()
    ])


def build_test_case_polizas(test_cases: pd.DataFrame) -> pd.DataFrame:
    base_date = datetime(2026, 5, 27)
    rows = []
    for _, row in test_cases.iterrows():
        inicio = base_date - timedelta(days=int(row.get('dias_inicio_poliza', 45)))
        fin = base_date + timedelta(days=int(row.get('dias_fin_poliza', 180)))
        rows.append(
            {
                'id_poliza': row['id_poliza'],
                'id_asegurado': row['id_asegurado'],
                'ramo': row['ramo'],
                'cobertura': row['cobertura'],
                'inicio_vigencia': inicio.strftime('%Y-%m-%d'),
                'fin_vigencia': fin.strftime('%Y-%m-%d'),
                'suma_asegurada': int(row.get('suma_asegurada', 16000)),
                'prima': 950,
            }
        )
    return pd.DataFrame(rows)


def build_test_case_conductores(test_cases: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {
            'id_conductor': row['id_conductor'],
            'nombre': f"Conductor {row['id_conductor']}",
            'edad': 41,
            'historial_conductor_18m': int(row.get('historial_conductor_18m', 0)),
        }
        for _, row in test_cases.iterrows()
    ])


def build_test_case_siniestros(test_cases: pd.DataFrame) -> pd.DataFrame:
    base_date = datetime(2026, 5, 27)
    rows = []
    for _, row in test_cases.iterrows():
        ocurrencia = base_date
        reporte = base_date + timedelta(days=int(row.get('dias_ocurr_reporte', 1)))
        rows.append(
            {
                'id_siniestro': row['id_siniestro'],
                'id_poliza': row['id_poliza'],
                'id_asegurado': row['id_asegurado'],
                'id_proveedor': row['id_proveedor'],
                'id_conductor': row['id_conductor'],
                'id_beneficiario': row['id_beneficiario'],
                'ramo': row['ramo'],
                'cobertura': row['cobertura'],
                'ciudad': row.get('ciudad', 'Quito'),
                'fecha_ocurrencia': ocurrencia.strftime('%Y-%m-%d'),
                'fecha_reporte': reporte.strftime('%Y-%m-%d'),
                'dias_ocurr_reporte': int(row.get('dias_ocurr_reporte', 1)),
                'dias_inicio_poliza': int(row.get('dias_inicio_poliza', 45)),
                'dias_fin_poliza': int(row.get('dias_fin_poliza', 180)),
                'monto_reclamado': int(row.get('monto_reclamado', 8000)),
                'documentos_completos': int(row.get('documentos_completos', 1)),
                'descripcion': row['descripcion'],
                'historial_siniestros': int(row.get('historial_siniestros', 0)),
                'historial_vehiculo_18m': int(row.get('historial_vehiculo_18m', 0)),
                'historial_conductor_18m': int(row.get('historial_conductor_18m', 0)),
                'solo_rc_recurrente': int(row.get('solo_rc_recurrente', 0)),
                'sin_tercero_identificado': int(row.get('sin_tercero_identificado', 0)),
                'cambio_reciente_datos_asegurado': int(row.get('cambio_reciente_datos_asegurado', 0)),
                'actor_en_lista_restrictiva_tipo': row.get('actor_en_lista_restrictiva_tipo', ''),
                'beneficiario_en_lista': int(row.get('beneficiario_en_lista', 0)),
            }
        )
    return pd.DataFrame(rows)


def build_test_case_documentos(test_cases: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in test_cases.iterrows():
        for doc in DOCUMENT_TYPES:
            inconsistente = 0
            if row['regla_esperada'] == 'RF-02':
                inconsistente = 1 if doc in {'parte_policial', 'factura_taller'} else 0
            elif row['regla_esperada'] == 'S11':
                inconsistente = 1 if doc == 'factura_taller' else 0
            rows.append(
                {
                    'id_documento': f"DOC-{row['id_siniestro']}-{doc}",
                    'id_siniestro': row['id_siniestro'],
                    'tipo_documento': doc,
                    'inconsistencia_detectada': inconsistente,
                }
            )
    return pd.DataFrame(rows)


def persist_tables(db_path: Path, asegurados: pd.DataFrame, proveedores: pd.DataFrame, polizas: pd.DataFrame, conductores: pd.DataFrame, siniestros: pd.DataFrame, documentos: pd.DataFrame) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        asegurados.to_sql('asegurados', conn, if_exists='replace', index=False)
        proveedores.to_sql('proveedores', conn, if_exists='replace', index=False)
        polizas.to_sql('polizas', conn, if_exists='replace', index=False)
        conductores.to_sql('conductores', conn, if_exists='replace', index=False)
        siniestros.to_sql('siniestros', conn, if_exists='replace', index=False)
        documentos.to_sql('documentos', conn, if_exists='replace', index=False)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    asegurados = build_asegurados()
    proveedores = build_proveedores()
    polizas = build_polizas(asegurados)
    conductores = build_conductores()
    siniestros = build_siniestros(polizas, asegurados, proveedores, conductores)
    documentos = build_documentos(siniestros)
    test_cases = build_test_cases()

    asegurados_tc = build_test_case_asegurados(test_cases)
    polizas_tc = build_test_case_polizas(test_cases)
    conductores_tc = build_test_case_conductores(test_cases)
    siniestros_tc = build_test_case_siniestros(test_cases)
    documentos_tc = build_test_case_documentos(test_cases)

    asegurados = pd.concat([asegurados, asegurados_tc], ignore_index=True)
    polizas = pd.concat([polizas, polizas_tc], ignore_index=True)
    conductores = pd.concat([conductores, conductores_tc], ignore_index=True)
    siniestros = pd.concat([siniestros, siniestros_tc], ignore_index=True)
    documentos = pd.concat([documentos, documentos_tc], ignore_index=True)

    persist_tables(DB_PATH, asegurados, proveedores, polizas, conductores, siniestros, documentos)
    test_cases.to_csv(TEST_CASES_PATH, index=False)

    print(f'Base sintetica generada en: {DB_PATH}')
    print(f'Casos dirigidos generados en: {TEST_CASES_PATH}')
    print(f'Siniestros creados: {len(siniestros)}')
    print(f'Casos dirigidos: {len(test_cases)}')


if __name__ == '__main__':
    main()
