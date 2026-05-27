# Metricas del Modelo

Evaluacion contra `etiqueta_fraude` simulada del dataset sintetico. Estas metricas validan el comportamiento del prototipo, no reemplazan una validacion con datos historicos reales.

| Metrica | Valor |
|---------|-------|
| Casos evaluados | 1000 |
| Positivos simulados | 212 |
| Precision | 0.7029 |
| Recall | 0.9151 |
| F1-score | 0.7951 |
| Accuracy | 0.9 |
| AUC-ROC | 0.9916 |

## Matriz de Confusion

|  | Predicho no rojo | Predicho rojo |
|---|---:|---:|
| Real no fraude simulado | 706 | 82 |
| Real fraude simulado | 18 | 194 |

## Interpretacion

- El objetivo operativo prioriza `recall`: capturar casos de alto riesgo para revision humana.
- Los falsos positivos son aceptables dentro del prototipo porque el sistema no acusa ni rechaza automaticamente.
- La decision final permanece en manos del analista antifraude.

```json
{
  "total_casos": 1000,
  "positivos_simulados": 212,
  "precision": 0.7029,
  "recall": 0.9151,
  "f1_score": 0.7951,
  "accuracy": 0.9,
  "auc_roc": 0.9916,
  "matriz_confusion": {
    "tn": 706,
    "fp": 82,
    "fn": 18,
    "tp": 194
  },
  "distribucion_nivel": {
    "VERDE": 696,
    "ROJO": 276,
    "AMARILLO": 28
  }
}
```
