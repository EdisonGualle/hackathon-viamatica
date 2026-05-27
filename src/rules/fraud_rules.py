"""
Motor de reglas de negocio para detección de fraude.
Implementa todas las señales de la sección 7 y reglas críticas RF-01 a RF-07.
"""
import json
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd


@dataclass
class RuleResult:
    codigo: str
    descripcion: str
    puntos: float
    nivel: str          # VERDE / AMARILLO / ROJO
    activada: bool
    detalle: str = ""


@dataclass
class ScoreResult:
    id_siniestro: str
    score_reglas: float
    reglas_activadas: list[RuleResult] = field(default_factory=list)
    nivel: str = "VERDE"
    explicacion: str = ""


# ──────────────────────────────────────────────
# REGLAS CRÍTICAS (RF)
# ──────────────────────────────────────────────

def rf01_perdida_total_robo(row: pd.Series) -> Optional[RuleResult]:
    """RF-01: Cobertura Pérdida Total por Robo — ROJO automático solo PTxRB."""
    activada = (
        "perdida total" in str(row.get("cobertura", "")).lower()
        and str(row.get("ramo", "")).lower() == "vehiculos"
    )
    return RuleResult(
        codigo="RF-01",
        descripcion="Cobertura Pérdida Total por Robo",
        puntos=20 if activada else 0,
        nivel="ROJO",
        activada=activada,
        detalle="Cobertura de robo / pérdida total detectada." if activada else "",
    )


def rf02_falsificacion_documental(row: pd.Series, docs_df: pd.DataFrame) -> Optional[RuleResult]:
    """RF-02: Evidencia de Falsificación o Adulteración Documental — ROJO."""
    docs_sin = docs_df[docs_df["id_siniestro"] == row["id_siniestro"]]
    inconsistencias = docs_sin["inconsistencia_detectada"].sum() if len(docs_sin) > 0 else 0
    activada = inconsistencias > 0
    return RuleResult(
        codigo="RF-02",
        descripcion="Falsificación o Adulteración Documental",
        puntos=10 if activada else 0,
        nivel="ROJO",
        activada=activada,
        detalle=f"{int(inconsistencias)} documento(s) con inconsistencias detectadas." if activada else "",
    )


def rf03_lista_restrictiva(row: pd.Series, proveedores_df: pd.DataFrame) -> Optional[RuleResult]:
    """RF-03: Asegurado, Beneficiario o Proveedor en Lista Restrictiva — ROJO."""
    prv = proveedores_df[proveedores_df["id_proveedor"] == row.get("id_proveedor")]
    en_lista = bool(prv["en_lista_restrictiva"].values[0]) if len(prv) > 0 else False
    return RuleResult(
        codigo="RF-03",
        descripcion="Coincidencia con Lista Restrictiva",
        puntos=10 if en_lista else 0,
        nivel="ROJO",
        activada=en_lista,
        detalle=f"Proveedor {row.get('id_proveedor')} registrado en lista restrictiva." if en_lista else "",
    )


def rf04_dinamica_imposible(row: pd.Series) -> Optional[RuleResult]:
    """RF-04: Dinámica del Accidente Físicamente Imposible — ROJO."""
    desc = str(row.get("descripcion", "")).lower()
    palabras_clave = ["imposible", "ilógico", "sin causa", "sin rastro", "inexplicable", "fuga", "huyo", "abandono"]
    activada = any(p in desc for p in palabras_clave)
    return RuleResult(
        codigo="RF-04",
        descripcion="Dinámica del Accidente Físicamente Imposible",
        puntos=6 if activada else 0,
        nivel="ROJO",
        activada=activada,
        detalle="Descripción contiene indicadores de dinámica físicamente imposible o inconsistente." if activada else "",
    )


def rf05_borde_vigencia_extremo(row: pd.Series) -> Optional[RuleResult]:
    """RF-05: Siniestro Extremo al Borde de Vigencia (< 48 hrs) — AMARILLO."""
    dias_inicio = int(row.get("dias_inicio_poliza", 9999))
    dias_fin = int(row.get("dias_fin_poliza", 9999))
    activada = dias_inicio <= 2 or dias_fin <= 2
    return RuleResult(
        codigo="RF-05",
        descripcion="Siniestro al Borde de Vigencia (<48h)",
        puntos=8 if activada else 0,
        nivel="AMARILLO",
        activada=activada,
        detalle=f"Siniestro ocurrido a {min(dias_inicio, dias_fin)} día(s) del borde de vigencia." if activada else "",
    )


def rf06_demora_denuncia_robo(row: pd.Series) -> Optional[RuleResult]:
    """RF-06: Demora Atípica en Denuncia de Robo (>4 días) — AMARILLO."""
    es_robo = "robo" in str(row.get("cobertura", "")).lower()
    dias = int(row.get("dias_ocurr_reporte", 0))
    activada = es_robo and dias > 4
    puntos = 8 if dias > 2 else (4 if dias > 1 else 0)
    return RuleResult(
        codigo="RF-06",
        descripcion="Demora Atípica en Denuncia de Robo",
        puntos=puntos if activada else 0,
        nivel="AMARILLO",
        activada=activada,
        detalle=f"Denuncia de robo realizada {dias} días después del evento." if activada else "",
    )


def rf07_narrativa_identica(row: pd.Series, siniestros_df: pd.DataFrame) -> Optional[RuleResult]:
    """RF-07: Narrativa Idéntica (Clonada) — se complementa con NLP. Aquí detección básica."""
    desc = str(row.get("descripcion", "")).strip().lower()
    misma_desc = siniestros_df[
        (siniestros_df["descripcion"].str.strip().str.lower() == desc)
        & (siniestros_df["id_siniestro"] != row["id_siniestro"])
    ]
    activada = len(misma_desc) > 0
    return RuleResult(
        codigo="RF-07",
        descripcion="Narrativa Idéntica (Clonada)",
        puntos=8 if activada else 0,
        nivel="AMARILLO",
        activada=activada,
        detalle=f"Descripción idéntica encontrada en {len(misma_desc)} siniestro(s)." if activada else "",
    )


# ──────────────────────────────────────────────
# SEÑALES DE PUNTUACIÓN (sección 7)
# ──────────────────────────────────────────────

def s01_borde_vigencia(row: pd.Series) -> RuleResult:
    dias = min(int(row.get("dias_inicio_poliza", 9999)), int(row.get("dias_fin_poliza", 9999)))
    if dias <= 10:
        pts, det = 8, f"Siniestro ocurrido a solo {dias} día(s) del borde de vigencia."
    elif dias <= 30:
        pts, det = 4, f"Siniestro ocurrido a {dias} días del borde de vigencia."
    else:
        pts, det = 0, ""
    return RuleResult("S01", "Reclamo cercano al borde de vigencia", pts, "AMARILLO", pts > 0, det)


def s02_demora_reporte(row: pd.Series) -> RuleResult:
    dias = int(row.get("dias_ocurr_reporte", 0))
    if dias > 7:
        pts, det = 5, f"Reporte realizado {dias} días después del siniestro."
    elif dias >= 4:
        pts, det = 3, f"Reporte con {dias} días de demora."
    else:
        pts, det = 0, ""
    return RuleResult("S02", "Reporte tardío del siniestro", pts, "AMARILLO", pts > 0, det)


def s03_alta_frecuencia_asegurado(row: pd.Series) -> RuleResult:
    hist = int(row.get("historial_siniestros", 0))
    if hist >= 3:
        pts, det = 8, f"Asegurado con {hist} siniestros en los últimos 18 meses."
    elif hist == 2:
        pts, det = 4, f"Asegurado con {hist} siniestros recientes."
    else:
        pts, det = 0, ""
    return RuleResult("S03", "Alta frecuencia de reclamos del asegurado", pts, "AMARILLO", pts > 0, det)


def s04_documentos_incompletos(row: pd.Series) -> RuleResult:
    completos = int(row.get("documentos_completos", 1))
    activada = completos == 0
    return RuleResult(
        "S04", "Documentos incompletos",
        4 if activada else 0,
        "AMARILLO", activada,
        "El expediente tiene documentos faltantes o incompletos." if activada else "",
    )


def s05_monto_cercano_suma(row: pd.Series, polizas_df: pd.DataFrame) -> RuleResult:
    pol = polizas_df[polizas_df["id_poliza"] == row.get("id_poliza")]
    if len(pol) == 0:
        return RuleResult("S05", "Monto cercano a suma asegurada", 0, "AMARILLO", False)
    suma = float(pol["suma_asegurada"].values[0])
    monto = float(row.get("monto_reclamado", 0))
    ratio = monto / suma if suma > 0 else 0
    if ratio > 0.95:
        pts, det = 5, f"Monto reclamado ({monto:,.0f}) es el {ratio*100:.0f}% de la suma asegurada."
    elif ratio > 0.50:
        pts, det = 4, f"Monto reclamado representa el {ratio*100:.0f}% de la suma asegurada."
    else:
        pts, det = 0, ""
    return RuleResult("S05", "Monto cercano o superior a suma asegurada", pts, "AMARILLO", pts > 0, det)


def s06_proveedor_recurrente(row: pd.Series, proveedores_df: pd.DataFrame) -> RuleResult:
    prv = proveedores_df[proveedores_df["id_proveedor"] == row.get("id_proveedor")]
    if len(prv) == 0:
        return RuleResult("S06", "Proveedor recurrente", 0, "AMARILLO", False)
    en_lista = bool(prv["en_lista_restrictiva"].values[0])
    pct_obs = float(prv["pct_casos_observados"].values[0])
    if en_lista:
        pts, det = 10, f"Proveedor {row.get('id_proveedor')} en lista restrictiva."
    elif pct_obs > 0.2:
        pts, det = 5, f"Proveedor con {pct_obs*100:.0f}% de casos observados."
    else:
        pts, det = 0, ""
    return RuleResult("S06", "Beneficiario / Proveedor recurrente", pts, "AMARILLO" if not en_lista else "ROJO", pts > 0, det)


def s07_demora_denuncia_robo(row: pd.Series) -> RuleResult:
    es_robo = "robo" in str(row.get("cobertura", "")).lower()
    dias = int(row.get("dias_ocurr_reporte", 0))
    horas_aprox = dias * 24
    if es_robo:
        if horas_aprox > 48:
            pts, det = 8, f"Denuncia de robo con {dias} días de demora (>{48}h)."
        elif horas_aprox >= 24:
            pts, det = 4, f"Denuncia de robo entre 24-48h después del evento."
        else:
            pts, det = 0, ""
    else:
        pts, det = 0, ""
    return RuleResult("S07", "Demora en denuncia por robo", pts, "AMARILLO", pts > 0, det)


# ──────────────────────────────────────────────
# MOTOR PRINCIPAL
# ──────────────────────────────────────────────

def calcular_score_reglas(
    row: pd.Series,
    siniestros_df: pd.DataFrame,
    polizas_df: pd.DataFrame,
    proveedores_df: pd.DataFrame,
    docs_df: pd.DataFrame,
) -> ScoreResult:
    """Calcula el score de reglas para un siniestro y retorna todas las reglas activadas."""
    reglas: list[RuleResult] = []

    # Reglas críticas
    reglas.append(rf01_perdida_total_robo(row))
    reglas.append(rf02_falsificacion_documental(row, docs_df))
    reglas.append(rf03_lista_restrictiva(row, proveedores_df))
    reglas.append(rf04_dinamica_imposible(row))
    reglas.append(rf05_borde_vigencia_extremo(row))
    reglas.append(rf06_demora_denuncia_robo(row))
    reglas.append(rf07_narrativa_identica(row, siniestros_df))

    # Señales de puntuación
    reglas.append(s01_borde_vigencia(row))
    reglas.append(s02_demora_reporte(row))
    reglas.append(s03_alta_frecuencia_asegurado(row))
    reglas.append(s04_documentos_incompletos(row))
    reglas.append(s05_monto_cercano_suma(row, polizas_df))
    reglas.append(s06_proveedor_recurrente(row, proveedores_df))
    reglas.append(s07_demora_denuncia_robo(row))

    activas = [r for r in reglas if r.activada]
    score = min(100.0, sum(r.puntos for r in activas))

    # Reglas críticas del reto que fuerzan ROJO
    CRITICAS_ROJO = {"RF-01", "RF-02", "RF-03", "RF-04"}
    fuerza_rojo = any(r.codigo in CRITICAS_ROJO and r.activada for r in reglas)
    if fuerza_rojo or score >= 76:
        nivel = "ROJO"
    elif score >= 41:
        nivel = "AMARILLO"
    else:
        nivel = "VERDE"

    codigos_activos = json.dumps([r.codigo for r in activas])
    explicacion = _generar_explicacion_texto(activas, nivel, score)

    return ScoreResult(
        id_siniestro=row["id_siniestro"],
        score_reglas=score,
        reglas_activadas=activas,
        nivel=nivel,
        explicacion=explicacion,
    )


def _generar_explicacion_texto(activas: list[RuleResult], nivel: str, score: float) -> str:
    if not activas:
        return "No se detectaron señales de riesgo. El caso puede continuar el flujo normal."
    detalles = " ".join([f"[{r.codigo}] {r.detalle}" for r in activas if r.detalle])
    nivel_texto = {"ROJO": "ALTO", "AMARILLO": "MEDIO", "VERDE": "BAJO"}[nivel]
    return (
        f"Nivel de riesgo {nivel_texto} (score de reglas: {score:.0f}/100). "
        f"Señales detectadas: {detalles} "
        f"Se recomienda {'revisión especializada de campo' if nivel == 'ROJO' else 'revisión documental por Unidad Antifraude' if nivel == 'AMARILLO' else 'continuar flujo normal'}."
    )


# ──────────────────────────────────────────────
# PROCESAMIENTO EN LOTE
# ──────────────────────────────────────────────

def procesar_todos(db_path: str) -> pd.DataFrame:
    """Calcula scores de reglas para todos los siniestros y retorna DataFrame."""
    conn = sqlite3.connect(db_path)
    siniestros_df = pd.read_sql("SELECT * FROM siniestros", conn)
    polizas_df = pd.read_sql("SELECT * FROM polizas", conn)
    proveedores_df = pd.read_sql("SELECT * FROM proveedores", conn)
    docs_df = pd.read_sql("SELECT * FROM documentos", conn)
    conn.close()

    resultados = []
    for _, row in siniestros_df.iterrows():
        res = calcular_score_reglas(row, siniestros_df, polizas_df, proveedores_df, docs_df)
        resultados.append({
            "id_siniestro": res.id_siniestro,
            "score_reglas": res.score_reglas,
            "nivel_reglas": res.nivel,
            "reglas_activadas": json.dumps([r.codigo for r in res.reglas_activadas]),
            "explicacion_reglas": res.explicacion,
        })

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    import os
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "fraudia.db")
    db_path = os.path.normpath(db_path)
    print("Ejecutando motor de reglas...")
    df = procesar_todos(db_path)
    print(f"Procesados: {len(df)} siniestros")
    print(df["nivel_reglas"].value_counts())
