from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd

CRITICAL_RULES = {'RF-01', 'RF-02', 'RF-03', 'RF-04'}
YELLOW_RULES = {'RF-05', 'RF-06', 'RF-07'}


@dataclass
class RuleResult:
    codigo: str
    nombre: str
    tipo: str
    activada: bool
    nivel: str
    puntos: float = 0.0
    variable_principal: str = ''
    evidencia: str = ''
    explicacion: str = ''
    accion_sugerida: str = ''
    fuente_negocio: str = ''

    @property
    def descripcion(self) -> str:
        return self.nombre

    @property
    def detalle(self) -> str:
        return self.evidencia

    def as_dict(self) -> dict:
        return {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'activada': self.activada,
            'nivel': self.nivel,
            'puntos': round(float(self.puntos), 2),
            'variable_principal': self.variable_principal,
            'evidencia': self.evidencia,
            'explicacion': self.explicacion,
            'accion_sugerida': self.accion_sugerida,
            'fuente_negocio': self.fuente_negocio,
        }


@dataclass
class ScoreResult:
    id_siniestro: str
    score_reglas: float
    reglas_activadas: list[RuleResult] = field(default_factory=list)
    nivel: str = 'VERDE'
    explicacion: str = ''


RULE_ACTION_REVIEW = 'Revisión documental prioritaria por Unidad Antifraude'
RULE_ACTION_ESCALATE = 'Escalar a revisión especializada'


def _normalize_text(value: object) -> str:
    return str(value or '').strip().lower()


def _bool_value(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'si', 'sí', 'yes', 'y'}
    return bool(value)


def _rule(codigo: str, nombre: str, tipo: str, activada: bool, nivel: str, puntos: float, variable: str, evidencia: str, explicacion: str, accion: str) -> RuleResult:
    return RuleResult(
        codigo=codigo,
        nombre=nombre,
        tipo=tipo,
        activada=bool(activada),
        nivel=nivel,
        puntos=float(puntos if activada else 0),
        variable_principal=variable,
        evidencia=evidencia if activada else '',
        explicacion=explicacion if activada else '',
        accion_sugerida=accion if activada else '',
        fuente_negocio=f'reglas_canonicas/{codigo}',
    )


def rf01_perdida_total_robo(row: pd.Series) -> RuleResult:
    coverage = _normalize_text(row.get('cobertura'))
    ramo = _normalize_text(row.get('ramo'))
    coverage_aliases = {'ptxrb', 'perdida total por robo', 'pérdida total por robo'}
    activated = ramo == 'vehiculos' and coverage in coverage_aliases
    return _rule('RF-01', 'Cobertura PTxRB activada', 'regla_critica', activated, 'ROJO', 40, 'cobertura', f"Cobertura {row.get('cobertura')} en ramo Vehiculos.", 'La cobertura de pérdida total por robo exige validación reforzada por tipología crítica del reto.', RULE_ACTION_ESCALATE)


def rf02_falsificacion_documental(row: pd.Series, docs_df: pd.DataFrame) -> RuleResult:
    docs = docs_df[docs_df['id_siniestro'] == row['id_siniestro']]
    inconsistencias = int(docs['inconsistencia_detectada'].sum()) if not docs.empty else 0
    desc = _normalize_text(row.get('descripcion'))
    texto_sospechoso = any(token in desc for token in ['inconsistencia documental', 'adulter', 'falsific'])
    activated = inconsistencias > 0 or texto_sospechoso
    evidence = f'{inconsistencias} documento(s) con inconsistencia detectada.' if inconsistencias > 0 else 'Narrativa menciona inconsistencia documental.'
    return _rule('RF-02', 'Falsificación o adulteración documental', 'regla_critica', activated, 'ROJO', 35, 'documentos', evidence, 'La evidencia documental inconsistente es una señal crítica del reto.', RULE_ACTION_ESCALATE)


def rf03_lista_restrictiva(row: pd.Series, proveedores_df: pd.DataFrame, asegurados_df: pd.DataFrame | None = None) -> RuleResult:
    actor_tipo = _normalize_text(row.get('actor_en_lista_restrictiva_tipo'))
    provider_id = row.get('id_proveedor')
    insured_id = row.get('id_asegurado')
    en_lista = False
    evidence = ''

    if actor_tipo == 'proveedor':
        en_lista = True
        evidence = f'Proveedor {provider_id} marcado en lista restrictiva.'
    elif actor_tipo == 'asegurado':
        en_lista = True
        evidence = f'Asegurado {insured_id} marcado en lista restrictiva.'
    elif _bool_value(row.get('beneficiario_en_lista')):
        en_lista = True
        evidence = f'Beneficiario {row.get("id_beneficiario", "N/D")} marcado en lista restrictiva.'
    else:
        provider = proveedores_df[proveedores_df['id_proveedor'] == provider_id]
        if not provider.empty and _bool_value(provider.iloc[0].get('en_lista_restrictiva')):
            en_lista = True
            evidence = f'Proveedor {provider_id} marcado en lista restrictiva.'
        elif asegurados_df is not None:
            insured = asegurados_df[asegurados_df['id_asegurado'] == insured_id]
            if not insured.empty and _bool_value(insured.iloc[0].get('en_lista_restrictiva')):
                en_lista = True
                evidence = f'Asegurado {insured_id} marcado en lista restrictiva.'

    return _rule('RF-03', 'Coincidencia con lista restrictiva', 'regla_critica', en_lista, 'ROJO', 35, 'actor_en_lista_restrictiva_tipo', evidence, 'La coincidencia exacta con una lista restrictiva obliga a revisión especializada.', RULE_ACTION_ESCALATE)


def rf04_dinamica_imposible(row: pd.Series) -> RuleResult:
    desc = _normalize_text(row.get('descripcion'))
    tokens = ['imposible', 'inexplicable', 'sin rastro', 'sin causa', 'poco consistente']
    activated = any(token in desc for token in tokens)
    return _rule('RF-04', 'Dinámica físicamente imposible', 'regla_critica', activated, 'ROJO', 30, 'descripcion', 'La narrativa contiene indicadores de imposibilidad física o inconsistencia severa.' if activated else '', 'La reconstrucción del evento resulta incompatible con la dinámica declarada.', RULE_ACTION_ESCALATE)


def rf05_borde_vigencia(row: pd.Series) -> RuleResult:
    dias_inicio = int(row.get('dias_inicio_poliza', 9999))
    dias_fin = int(row.get('dias_fin_poliza', 9999))
    borde = min(dias_inicio, dias_fin)
    activated = borde < 2
    return _rule('RF-05', 'Siniestro extremo al borde de vigencia', 'regla_amarilla', activated, 'AMARILLO', 10, 'dias_inicio_poliza', f'Siniestro ocurrido a {borde} día(s) del borde de vigencia.' if activated else '', 'La cercanía extrema al inicio o fin de vigencia requiere revisión documental.', RULE_ACTION_REVIEW)


def rf06_demora_robo(row: pd.Series) -> RuleResult:
    cobertura = _normalize_text(row.get('cobertura'))
    dias = int(row.get('dias_ocurr_reporte', 0))
    activated = cobertura == 'ptxrb' and dias > 4
    return _rule('RF-06', 'Demora atípica en denuncia de robo', 'regla_amarilla', activated, 'AMARILLO', 10, 'dias_ocurr_reporte', f'Denuncia de robo realizada {dias} días después del evento.' if activated else '', 'La demora superior al umbral del reto amerita revisión prioritaria.', RULE_ACTION_REVIEW)


def rf07_narrativa_clonada(row: pd.Series, siniestros_df: pd.DataFrame) -> RuleResult:
    desc = _normalize_text(row.get('descripcion'))
    repeated = siniestros_df[
        (siniestros_df['id_siniestro'] != row['id_siniestro'])
        & (siniestros_df['descripcion'].fillna('').str.strip().str.lower() == desc)
    ]
    activated = not repeated.empty and desc != ''
    return _rule('RF-07', 'Narrativa idéntica o clonada', 'regla_amarilla', activated, 'AMARILLO', 8, 'descripcion', f'Narrativa idéntica encontrada en {len(repeated)} siniestro(s).' if activated else '', 'La narrativa repetida es consistente con reutilización indebida de relato.', RULE_ACTION_REVIEW)


def signal_s01_borde_vigencia(row: pd.Series) -> RuleResult:
    borde = min(int(row.get('dias_inicio_poliza', 9999)), int(row.get('dias_fin_poliza', 9999)))
    if borde <= 10:
        pts = 8 if borde <= 5 else 4
        return _rule('S01', 'Reclamo cercano al borde de vigencia', 'senal_score', True, 'AMARILLO', pts, 'dias_inicio_poliza', f'Siniestro a {borde} día(s) del borde de vigencia.', 'La proximidad a la vigencia aumenta el riesgo operacional del caso.', RULE_ACTION_REVIEW)
    return _rule('S01', 'Reclamo cercano al borde de vigencia', 'senal_score', False, 'VERDE', 0, 'dias_inicio_poliza', '', '', '')


def signal_s02_demora_robo(row: pd.Series) -> RuleResult:
    dias = int(row.get('dias_ocurr_reporte', 0))
    cobertura = _normalize_text(row.get('cobertura'))
    activated = cobertura == 'ptxrb' and dias > 2
    pts = 5 if dias > 4 else 3
    return _rule('S02', 'Demora en denuncia por robo', 'senal_score', activated, 'AMARILLO', pts, 'dias_ocurr_reporte', f'Denuncia con {dias} día(s) de demora.' if activated else '', 'La demora en denuncias de robo incrementa el riesgo de inconsistencia.', RULE_ACTION_REVIEW)


def signal_s03_historial_asegurado(row: pd.Series) -> RuleResult:
    hist = int(row.get('historial_siniestros', 0))
    activated = hist >= 2
    pts = 8 if hist >= 4 else 5
    return _rule('S03', 'Alta frecuencia del asegurado', 'senal_score', activated, 'AMARILLO', pts, 'historial_siniestros', f'Asegurado con {hist} siniestro(s) en 18 meses.' if activated else '', 'La recurrencia del asegurado incrementa la prioridad de revisión.', RULE_ACTION_REVIEW)


def signal_s04_historial_vehiculo(row: pd.Series) -> RuleResult:
    hist = int(row.get('historial_vehiculo_18m', 0))
    activated = hist >= 2
    pts = 7 if hist >= 3 else 4
    return _rule('S04', 'Alta frecuencia del vehículo', 'senal_score', activated, 'AMARILLO', pts, 'historial_vehiculo_18m', f'Vehículo con {hist} siniestro(s) en 18 meses.' if activated else '', 'La recurrencia del vehículo es una señal de riesgo acumulado.', RULE_ACTION_REVIEW)


def signal_s05_historial_conductor(row: pd.Series) -> RuleResult:
    hist = int(row.get('historial_conductor_18m', 0))
    activated = hist >= 2
    pts = 7 if hist >= 3 else 4
    return _rule('S05', 'Alta frecuencia del conductor', 'senal_score', activated, 'AMARILLO', pts, 'historial_conductor_18m', f'Conductor con {hist} siniestro(s) en 18 meses.' if activated else '', 'La recurrencia del conductor amerita revisión adicional.', RULE_ACTION_REVIEW)


def signal_s06_solo_rc(row: pd.Series) -> RuleResult:
    activated = _bool_value(row.get('solo_rc_recurrente')) and _normalize_text(row.get('cobertura')) == 'rc'
    return _rule('S06', 'Recurrencia solo RC', 'senal_score', activated, 'AMARILLO', 5, 'solo_rc_recurrente', 'El asegurado presenta recurrencia de siniestros solo RC.' if activated else '', 'La recurrencia concentrada en RC es una señal de observación del reto.', RULE_ACTION_REVIEW)


def signal_s07_proveedor_recurrente(row: pd.Series, proveedores_df: pd.DataFrame) -> RuleResult:
    provider = proveedores_df[proveedores_df['id_proveedor'] == row.get('id_proveedor')]
    pct = float(provider.iloc[0]['pct_casos_observados']) if not provider.empty else 0.0
    activated = pct >= 0.2
    pts = 7 if pct >= 0.3 else 4
    return _rule('S07', 'Proveedor recurrente observado', 'senal_score', activated, 'AMARILLO', pts, 'id_proveedor', f'Proveedor con {pct:.0%} de casos observados.' if activated else '', 'La concentración de casos observados en el proveedor incrementa riesgo.', RULE_ACTION_REVIEW)


def signal_s08_documentos_incompletos(row: pd.Series) -> RuleResult:
    activated = not _bool_value(row.get('documentos_completos', 1))
    return _rule('S08', 'Documentos incompletos', 'senal_score', activated, 'AMARILLO', 5, 'documentos_completos', 'El expediente tiene documentos faltantes o incompletos.' if activated else '', 'La falta de soporte documental incrementa la incertidumbre del caso.', RULE_ACTION_REVIEW)


def signal_s09_dinamica_sospechosa(row: pd.Series) -> RuleResult:
    desc = _normalize_text(row.get('descripcion'))
    tokens = ['vacios relevantes', 'poco consistente', 'sin rastro', 'abandona', 'huyo']
    activated = any(token in desc for token in tokens)
    return _rule('S09', 'Dinámica sospechosa', 'senal_score', activated, 'AMARILLO', 5, 'descripcion', 'La narrativa presenta vacíos o consistencia débil.' if activated else '', 'La descripción requiere validación adicional por consistencia narrativa.', RULE_ACTION_REVIEW)


def signal_s10_sin_tercero(row: pd.Series) -> RuleResult:
    activated = _bool_value(row.get('sin_tercero_identificado'))
    return _rule('S10', 'Evento sin tercero identificado', 'senal_score', activated, 'AMARILLO', 5, 'sin_tercero_identificado', 'El evento se reporta sin tercero identificado.' if activated else '', 'La ausencia de tercero identificado incrementa necesidad de verificación.', RULE_ACTION_REVIEW)


def signal_s11_documentos_inconsistentes(row: pd.Series, docs_df: pd.DataFrame) -> RuleResult:
    docs = docs_df[docs_df['id_siniestro'] == row['id_siniestro']]
    inconsistencias = int(docs['inconsistencia_detectada'].sum()) if not docs.empty else 0
    desc = _normalize_text(row.get('descripcion'))
    activated = inconsistencias > 0 or 'inconsistencias' in desc
    pts = 6 if inconsistencias > 0 else 4
    return _rule('S11', 'Documentos inconsistentes', 'senal_score', activated, 'AMARILLO', pts, 'documentos', f'Se detectan {inconsistencias} inconsistencia(s) documentales.' if inconsistencias > 0 else 'La narrativa menciona inconsistencias documentales.', 'Las inconsistencias documentales elevan el riesgo operativo del caso.', RULE_ACTION_REVIEW)


def signal_s12_reporte_tardio(row: pd.Series) -> RuleResult:
    dias = int(row.get('dias_ocurr_reporte', 0))
    activated = dias >= 4
    pts = 5 if dias >= 7 else 3
    return _rule('S12', 'Reporte tardío general', 'senal_score', activated, 'AMARILLO', pts, 'dias_ocurr_reporte', f'Reporte realizado {dias} días después del evento.' if activated else '', 'El retraso general de reporte amerita revisión documental.', RULE_ACTION_REVIEW)


def signal_s14_monto_cercano(row: pd.Series, polizas_df: pd.DataFrame) -> RuleResult:
    poliza = polizas_df[polizas_df['id_poliza'] == row.get('id_poliza')]
    suma = float(poliza.iloc[0]['suma_asegurada']) if not poliza.empty else float(row.get('suma_asegurada', 0) or 0)
    monto = float(row.get('monto_reclamado', 0) or 0)
    ratio = monto / suma if suma else 0.0
    activated = ratio >= 0.9
    pts = 7 if ratio >= 0.95 else 4
    return _rule('S14', 'Monto cercano a suma asegurada', 'senal_score', activated, 'AMARILLO', pts, 'monto_reclamado', f'Monto reclamado equivale al {ratio:.0%} de la suma asegurada.' if activated else '', 'La cercanía del monto a la suma asegurada incrementa el riesgo de revisión.', RULE_ACTION_REVIEW)


def _build_all_rules(row: pd.Series, siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame, proveedores_df: pd.DataFrame, docs_df: pd.DataFrame, asegurados_df: pd.DataFrame | None = None) -> list[RuleResult]:
    return [
        rf01_perdida_total_robo(row),
        rf02_falsificacion_documental(row, docs_df),
        rf03_lista_restrictiva(row, proveedores_df, asegurados_df),
        rf04_dinamica_imposible(row),
        rf05_borde_vigencia(row),
        rf06_demora_robo(row),
        rf07_narrativa_clonada(row, siniestros_df),
        signal_s01_borde_vigencia(row),
        signal_s02_demora_robo(row),
        signal_s03_historial_asegurado(row),
        signal_s04_historial_vehiculo(row),
        signal_s05_historial_conductor(row),
        signal_s06_solo_rc(row),
        signal_s07_proveedor_recurrente(row, proveedores_df),
        signal_s08_documentos_incompletos(row),
        signal_s09_dinamica_sospechosa(row),
        signal_s10_sin_tercero(row),
        signal_s11_documentos_inconsistentes(row, docs_df),
        signal_s12_reporte_tardio(row),
        signal_s14_monto_cercano(row, polizas_df),
    ]


def _serialize_codes(results: Iterable[RuleResult]) -> str:
    return json.dumps([result.codigo for result in results if result.activada], ensure_ascii=True)


def _serialize_details(results: Iterable[RuleResult]) -> str:
    return json.dumps([result.as_dict() for result in results if result.activada], ensure_ascii=True)


def _build_explanation(results: list[RuleResult]) -> str:
    active = [result for result in results if result.activada]
    if not active:
        return 'Sin señales activadas de posible fraude.'
    return ' | '.join(f'{result.codigo}: {result.evidencia or result.explicacion}' for result in active)


def calcular_score_reglas(row: pd.Series, siniestros_df: pd.DataFrame, polizas_df: pd.DataFrame, proveedores_df: pd.DataFrame, docs_df: pd.DataFrame, asegurados_df: pd.DataFrame | None = None) -> ScoreResult:
    results = _build_all_rules(row, siniestros_df, polizas_df, proveedores_df, docs_df, asegurados_df)
    active = [result for result in results if result.activada]
    critical_active = [result for result in active if result.codigo in CRITICAL_RULES]
    base_score = sum(result.puntos for result in active)
    score = min(round(base_score, 2), 100.0)

    if critical_active:
        nivel = 'ROJO'
        score = max(score, 76.0)
    elif score >= 41:
        nivel = 'AMARILLO'
    else:
        nivel = 'VERDE'

    return ScoreResult(
        id_siniestro=str(row['id_siniestro']),
        score_reglas=score,
        reglas_activadas=active,
        nivel=nivel,
        explicacion=_build_explanation(results),
    )


def procesar_todos(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    siniestros_df = pd.read_sql('SELECT * FROM siniestros', conn)
    polizas_df = pd.read_sql('SELECT * FROM polizas', conn)
    proveedores_df = pd.read_sql('SELECT * FROM proveedores', conn)
    docs_df = pd.read_sql('SELECT * FROM documentos', conn)
    asegurados_df = pd.read_sql('SELECT * FROM asegurados', conn)
    conn.close()

    rows = []
    for _, row in siniestros_df.iterrows():
        score = calcular_score_reglas(row, siniestros_df, polizas_df, proveedores_df, docs_df, asegurados_df)
        rows.append(
            {
                'id_siniestro': score.id_siniestro,
                'score_reglas': score.score_reglas,
                'nivel_reglas': score.nivel,
                'reglas_activadas': _serialize_codes(score.reglas_activadas),
                'detalle_reglas_json': _serialize_details(score.reglas_activadas),
                'explicacion_reglas': score.explicacion,
            }
        )

    return pd.DataFrame(rows)
