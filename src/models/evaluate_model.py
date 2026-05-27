"""
Evaluacion del modelo FRAUDIA CLAIMS contra etiqueta simulada.
Genera metricas para documentacion y pitch del hackIAthon.
"""
import json
import os
import sqlite3

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(ROOT_DIR, "fraudia.db")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")


def evaluate(db_path: str = DB_PATH) -> dict:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("""
        SELECT s.id_siniestro, s.etiqueta_fraude,
               sr.score_final, sr.score_ml, sr.score_reglas, sr.score_nlp, sr.nivel
        FROM siniestros s
        JOIN scores_riesgo sr ON sr.id_siniestro = s.id_siniestro
    """, conn)
    conn.close()

    y_true = df["etiqueta_fraude"].astype(int)
    y_pred = (df["nivel"] == "ROJO").astype(int)
    y_score = df["score_final"].astype(float) / 100.0
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    metrics = {
        "total_casos": int(len(df)),
        "positivos_simulados": int(y_true.sum()),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "auc_roc": round(float(roc_auc_score(y_true, y_score)), 4),
        "matriz_confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "distribucion_nivel": df["nivel"].value_counts().to_dict(),
    }
    return metrics


def write_report(metrics: dict, path: str = os.path.join(DOCS_DIR, "metricas_modelo.md")):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cm = metrics["matriz_confusion"]
    content = f"""# Metricas del Modelo

Evaluacion contra `etiqueta_fraude` simulada del dataset sintetico. Estas metricas validan el comportamiento del prototipo, no reemplazan una validacion con datos historicos reales.

| Metrica | Valor |
|---------|-------|
| Casos evaluados | {metrics['total_casos']} |
| Positivos simulados | {metrics['positivos_simulados']} |
| Precision | {metrics['precision']} |
| Recall | {metrics['recall']} |
| F1-score | {metrics['f1_score']} |
| Accuracy | {metrics['accuracy']} |
| AUC-ROC | {metrics['auc_roc']} |

## Matriz de Confusion

|  | Predicho no rojo | Predicho rojo |
|---|---:|---:|
| Real no fraude simulado | {cm['tn']} | {cm['fp']} |
| Real fraude simulado | {cm['fn']} | {cm['tp']} |

## Interpretacion

- El objetivo operativo prioriza `recall`: capturar casos de alto riesgo para revision humana.
- Los falsos positivos son aceptables dentro del prototipo porque el sistema no acusa ni rechaza automaticamente.
- La decision final permanece en manos del analista antifraude.

```json
{json.dumps(metrics, indent=2, ensure_ascii=False)}
```
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    result = evaluate()
    write_report(result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
