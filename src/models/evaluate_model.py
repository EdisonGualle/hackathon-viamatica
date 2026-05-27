"""
Evaluacion expandida del sistema FRAUDIA CLAIMS contra etiqueta simulada.
Genera comparativas entre variantes del scoring y documenta limites del set sintetico.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
DB_PATH = os.path.join(ROOT_DIR, "fraudia.db")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from scoring.thresholds import CRITICAL_RULES, ROJO_MIN, VERDE_MAX
from models.fraud_model import build_labels


def _normalize_bool_level(score_series: pd.Series, critical_flags: pd.Series) -> pd.Series:
    base = pd.Series(["VERDE"] * len(score_series), index=score_series.index)
    base.loc[score_series > VERDE_MAX] = "AMARILLO"
    base.loc[score_series >= ROJO_MIN] = "ROJO"
    base.loc[critical_flags.astype(bool)] = "ROJO"
    return base


def _collect_frame(db_path: str = DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(
            """
            SELECT s.id_siniestro,
                   s.ramo,
                   s.ciudad,
                   s.descripcion,
                   s.cobertura,
                   s.dias_ocurr_reporte,
                   s.historial_siniestros,
                   s.historial_vehiculo_18m,
                   s.historial_conductor_18m,
                   s.monto_reclamado,
                   sr.score_final,
                   sr.score_ml,
                   sr.score_reglas,
                   sr.score_nlp,
                   sr.nivel,
                   sr.reglas_activadas,
                   COALESCE(d.document_score_total, 0) AS document_score_total
            FROM siniestros s
            JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
            LEFT JOIN (
                SELECT id_siniestro, ROUND(SUM(document_score), 2) AS document_score_total
                FROM document_ai_results
                GROUP BY id_siniestro
            ) d ON d.id_siniestro = s.id_siniestro
            """,
            conn,
        )
    df["etiqueta_fraude"] = build_labels(df).astype(int)
    df["critical_trigger"] = df["reglas_activadas"].fillna("[]").apply(
        lambda raw: any(code in CRITICAL_RULES for code in json.loads(raw or "[]"))
    )
    return df


def _variant_score(df: pd.DataFrame, variant: str) -> tuple[pd.Series, pd.Series]:
    if variant == "reglas":
        score = df["score_reglas"].clip(0, 100)
    elif variant == "reglas_ml":
        score = (0.55 * df["score_reglas"] + 0.45 * df["score_ml"]).clip(0, 100)
    elif variant == "reglas_ml_nlp":
        score = (0.45 * df["score_reglas"] + 0.40 * df["score_ml"] + 0.15 * df["score_nlp"]).clip(0, 100)
    elif variant == "reglas_ml_nlp_documentos":
        # Variante exploratoria: no reemplaza el score canónico. Se usa para medir aporte potencial del análisis documental.
        score = (0.45 * df["score_reglas"] + 0.40 * df["score_ml"] + 0.15 * df["score_nlp"] + 0.25 * df["document_score_total"]).clip(0, 100)
    else:
        raise ValueError(f"Variante no soportada: {variant}")
    level = _normalize_bool_level(score, df["critical_trigger"])
    return score.round(2), level


def _metrics_for_variant(df: pd.DataFrame, score: pd.Series, level: pd.Series) -> dict:
    y_true = df["etiqueta_fraude"].astype(int)
    y_pred = (level == "ROJO").astype(int)
    y_score = score.astype(float) / 100.0
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "total_casos": int(len(df)),
        "positivos_simulados": int(y_true.sum()),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "auc_roc": round(float(roc_auc_score(y_true, y_score)), 4),
        "matriz_confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "distribucion_nivel": level.value_counts().to_dict(),
    }


def _collect_fp_fn_examples(df: pd.DataFrame, score: pd.Series, level: pd.Series, limit: int = 5) -> dict:
    y_true = df["etiqueta_fraude"].astype(int)
    y_pred = (level == "ROJO").astype(int)
    working = df.copy()
    working["variant_score"] = score
    working["variant_level"] = level
    false_positives = working[(y_true == 0) & (y_pred == 1)].head(limit)
    false_negatives = working[(y_true == 1) & (y_pred == 0)].head(limit)
    cols = ["id_siniestro", "variant_score", "variant_level", "score_reglas", "score_ml", "score_nlp", "document_score_total"]
    return {
        "false_positives": false_positives[cols].to_dict("records"),
        "false_negatives": false_negatives[cols].to_dict("records"),
    }


def _segment_summary(df: pd.DataFrame, level: pd.Series, segment_col: str) -> list[dict]:
    working = df.copy()
    working["variant_level"] = level
    grouped = (
        working.groupby(segment_col, dropna=False)
        .agg(
            total_casos=("id_siniestro", "count"),
            score_promedio=("score_final", "mean"),
            document_score_promedio=("document_score_total", "mean"),
            positivos_simulados=("etiqueta_fraude", "sum"),
            rojos_predichos=("variant_level", lambda values: int((values == "ROJO").sum())),
            amarillos_predichos=("variant_level", lambda values: int((values == "AMARILLO").sum())),
        )
        .reset_index()
        .sort_values(["rojos_predichos", "score_promedio"], ascending=[False, False])
    )
    grouped["score_promedio"] = grouped["score_promedio"].round(2)
    grouped["document_score_promedio"] = grouped["document_score_promedio"].round(2)
    return grouped.to_dict("records")


def evaluate(db_path: str = DB_PATH) -> dict:
    df = _collect_frame(db_path)
    variants = ["reglas", "reglas_ml", "reglas_ml_nlp", "reglas_ml_nlp_documentos"]
    results = {}
    for variant in variants:
        score, level = _variant_score(df, variant)
        results[variant] = _metrics_for_variant(df, score, level)
        if variant == "reglas_ml_nlp_documentos":
            results[variant]["error_examples"] = _collect_fp_fn_examples(df, score, level)
        if variant == "reglas_ml_nlp":
            results[variant]["segmentacion"] = {
                "por_ramo": _segment_summary(df, level, "ramo"),
                "por_ciudad": _segment_summary(df, level, "ciudad"),
            }
    results["metadata"] = {
        "score_canonico_en_produccion": "reglas_ml_nlp",
        "score_documental_exploratorio": "reglas_ml_nlp_documentos",
        "nota": "La variante documental es comparativa y no sustituye el score canónico vigente.",
    }
    return results


def write_report(metrics: dict, path: str = os.path.join(DOCS_DIR, "evaluacion_modelo_expandida.md")) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    for name in ["reglas", "reglas_ml", "reglas_ml_nlp", "reglas_ml_nlp_documentos"]:
        item = metrics[name]
        rows.append(
            f"| {name} | {item['precision']} | {item['recall']} | {item['f1_score']} | {item['accuracy']} | {item['auc_roc']} |"
        )
    ramo_segment = metrics["reglas_ml_nlp"]["segmentacion"]["por_ramo"]
    ciudad_segment = metrics["reglas_ml_nlp"]["segmentacion"]["por_ciudad"]
    ramo_lines = [
        f"| {item['ramo']} | {item['total_casos']} | {item['rojos_predichos']} | {item['amarillos_predichos']} | {item['score_promedio']} |"
        for item in ramo_segment[:10]
    ]
    ciudad_lines = [
        f"| {item['ciudad']} | {item['total_casos']} | {item['rojos_predichos']} | {item['amarillos_predichos']} | {item['score_promedio']} |"
        for item in ciudad_segment[:10]
    ]
    content = f"""# Evaluación Expandida del Modelo

Evaluación contra `etiqueta_fraude` simulada. Esta validación sirve para defensa técnica del prototipo y no sustituye una evaluación con históricos reales.

## Variantes comparadas

| Variante | Precision | Recall | F1 | Accuracy | AUC |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Lectura técnica

- `reglas_ml_nlp` es el score canónico actualmente desplegado.
- `reglas_ml_nlp_documentos` es una variante exploratoria para medir el aporte potencial de `Document AI`.
- La comparación muestra el impacto incremental de sumar ML, NLP y evidencia documental.

## Corte por ramo sobre score canónico

| Ramo | Casos | Rojos | Amarillos | Score promedio |
|---|---:|---:|---:|---:|
{chr(10).join(ramo_lines)}

## Corte por ciudad sobre score canónico

| Ciudad | Casos | Rojos | Amarillos | Score promedio |
|---|---:|---:|---:|---:|
{chr(10).join(ciudad_lines)}

## Metadatos

```json
{json.dumps(metrics["metadata"], indent=2, ensure_ascii=False)}
```

## Resultado completo

```json
{json.dumps(metrics, indent=2, ensure_ascii=False)}
```
"""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def write_error_analysis(metrics: dict, path: str = os.path.join(DOCS_DIR, "falsos_positivos_negativos.md")) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    examples = metrics["reglas_ml_nlp_documentos"]["error_examples"]
    content = f"""# Falsos Positivos y Falsos Negativos

Análisis exploratorio sobre la variante con soporte documental. La lectura es útil para calibración del prototipo y para explicar límites del dataset sintético.

## Falsos positivos

```json
{json.dumps(examples["false_positives"], indent=2, ensure_ascii=False)}
```

## Falsos negativos

```json
{json.dumps(examples["false_negatives"], indent=2, ensure_ascii=False)}
```

## Interpretación

- Un falso positivo es aceptable si la evidencia justifica revisión humana y el sistema no acusa automáticamente.
- Un falso negativo es el riesgo más delicado; estos casos deben usarse para reforzar reglas, NLP y evidencia documental.
- La etiqueta sigue siendo simulada, por lo que estas observaciones sirven para calibración, no para inferencia de performance productiva real.
"""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


if __name__ == "__main__":
    result = evaluate()
    write_report(result)
    write_error_analysis(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
