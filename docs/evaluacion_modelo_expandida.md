# Evaluación Expandida del Modelo

Evaluación contra `etiqueta_fraude` simulada. Esta validación sirve para defensa técnica del prototipo y no sustituye una evaluación con históricos reales.

## Variantes comparadas

| Variante | Precision | Recall | F1 | Accuracy | AUC |
|---|---:|---:|---:|---:|---:|
| reglas | 0.8718 | 0.5763 | 0.6939 | 0.6226 | 0.8103 |
| reglas_ml | 0.8718 | 0.5763 | 0.6939 | 0.6226 | 0.9175 |
| reglas_ml_nlp | 0.8718 | 0.5763 | 0.6939 | 0.6226 | 0.9315 |
| reglas_ml_nlp_documentos | 0.8718 | 0.5763 | 0.6939 | 0.6226 | 0.9288 |

## Lectura técnica

- `reglas_ml_nlp` es el score canónico actualmente desplegado.
- `reglas_ml_nlp_documentos` es una variante exploratoria para medir el aporte potencial de `Document AI`.
- La comparación muestra el impacto incremental de sumar ML, NLP y evidencia documental.

## Corte por ramo sobre score canónico

| Ramo | Casos | Rojos | Amarillos | Score promedio |
|---|---:|---:|---:|---:|
| Vehiculos | 136 | 64 | 39 | 62.28 |
| Patrimoniales | 23 | 14 | 8 | 71.21 |

## Corte por ciudad sobre score canónico

| Ciudad | Casos | Rojos | Amarillos | Score promedio |
|---|---:|---:|---:|---:|
| Quito | 72 | 27 | 15 | 53.96 |
| Cuenca | 27 | 19 | 7 | 74.85 |
| Guayaquil | 29 | 16 | 12 | 71.33 |
| Ambato | 18 | 10 | 8 | 71.96 |
| Manta | 13 | 6 | 5 | 64.48 |

## Metadatos

```json
{
  "score_canonico_en_produccion": "reglas_ml_nlp",
  "score_documental_exploratorio": "reglas_ml_nlp_documentos",
  "nota": "La variante documental es comparativa y no sustituye el score canónico vigente."
}
```

## Resultado completo

```json
{
  "reglas": {
    "total_casos": 159,
    "positivos_simulados": 118,
    "precision": 0.8718,
    "recall": 0.5763,
    "f1_score": 0.6939,
    "accuracy": 0.6226,
    "auc_roc": 0.8103,
    "matriz_confusion": {
      "tn": 31,
      "fp": 10,
      "fn": 50,
      "tp": 68
    },
    "distribucion_nivel": {
      "ROJO": 78,
      "VERDE": 75,
      "AMARILLO": 6
    }
  },
  "reglas_ml": {
    "total_casos": 159,
    "positivos_simulados": 118,
    "precision": 0.8718,
    "recall": 0.5763,
    "f1_score": 0.6939,
    "accuracy": 0.6226,
    "auc_roc": 0.9175,
    "matriz_confusion": {
      "tn": 31,
      "fp": 10,
      "fn": 50,
      "tp": 68
    },
    "distribucion_nivel": {
      "ROJO": 78,
      "VERDE": 50,
      "AMARILLO": 31
    }
  },
  "reglas_ml_nlp": {
    "total_casos": 159,
    "positivos_simulados": 118,
    "precision": 0.8718,
    "recall": 0.5763,
    "f1_score": 0.6939,
    "accuracy": 0.6226,
    "auc_roc": 0.9315,
    "matriz_confusion": {
      "tn": 31,
      "fp": 10,
      "fn": 50,
      "tp": 68
    },
    "distribucion_nivel": {
      "ROJO": 78,
      "AMARILLO": 47,
      "VERDE": 34
    },
    "segmentacion": {
      "por_ramo": [
        {
          "ramo": "Vehiculos",
          "total_casos": 136,
          "score_promedio": 62.28,
          "document_score_promedio": 4.84,
          "positivos_simulados": 99,
          "rojos_predichos": 64,
          "amarillos_predichos": 39
        },
        {
          "ramo": "Patrimoniales",
          "total_casos": 23,
          "score_promedio": 71.21,
          "document_score_promedio": 9.04,
          "positivos_simulados": 19,
          "rojos_predichos": 14,
          "amarillos_predichos": 8
        }
      ],
      "por_ciudad": [
        {
          "ciudad": "Quito",
          "total_casos": 72,
          "score_promedio": 53.96,
          "document_score_promedio": 3.11,
          "positivos_simulados": 40,
          "rojos_predichos": 27,
          "amarillos_predichos": 15
        },
        {
          "ciudad": "Cuenca",
          "total_casos": 27,
          "score_promedio": 74.85,
          "document_score_promedio": 8.37,
          "positivos_simulados": 26,
          "rojos_predichos": 19,
          "amarillos_predichos": 7
        },
        {
          "ciudad": "Guayaquil",
          "total_casos": 29,
          "score_promedio": 71.33,
          "document_score_promedio": 8.28,
          "positivos_simulados": 25,
          "rojos_predichos": 16,
          "amarillos_predichos": 12
        },
        {
          "ciudad": "Ambato",
          "total_casos": 18,
          "score_promedio": 71.96,
          "document_score_promedio": 5.22,
          "positivos_simulados": 17,
          "rojos_predichos": 10,
          "amarillos_predichos": 8
        },
        {
          "ciudad": "Manta",
          "total_casos": 13,
          "score_promedio": 64.48,
          "document_score_promedio": 6.31,
          "positivos_simulados": 10,
          "rojos_predichos": 6,
          "amarillos_predichos": 5
        }
      ]
    }
  },
  "reglas_ml_nlp_documentos": {
    "total_casos": 159,
    "positivos_simulados": 118,
    "precision": 0.8718,
    "recall": 0.5763,
    "f1_score": 0.6939,
    "accuracy": 0.6226,
    "auc_roc": 0.9288,
    "matriz_confusion": {
      "tn": 31,
      "fp": 10,
      "fn": 50,
      "tp": 68
    },
    "distribucion_nivel": {
      "ROJO": 78,
      "AMARILLO": 47,
      "VERDE": 34
    },
    "error_examples": {
      "false_positives": [
        {
          "id_siniestro": "SIN-0029",
          "variant_score": 66.42,
          "variant_level": "ROJO",
          "score_reglas": 76.0,
          "score_ml": 35.54,
          "score_nlp": 100.0,
          "document_score_total": 12.0
        },
        {
          "id_siniestro": "SIN-0077",
          "variant_score": 67.88,
          "variant_level": "ROJO",
          "score_reglas": 76.0,
          "score_ml": 39.2,
          "score_nlp": 100.0,
          "document_score_total": 12.0
        },
        {
          "id_siniestro": "TC-RF03-P",
          "variant_score": 49.73,
          "variant_level": "ROJO",
          "score_reglas": 76.0,
          "score_ml": 6.76,
          "score_nlp": 85.51,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "TC-C01",
          "variant_score": 53.26,
          "variant_level": "ROJO",
          "score_reglas": 76.0,
          "score_ml": 16.4,
          "score_nlp": 83.33,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "TC-A01",
          "variant_score": 49.4,
          "variant_level": "ROJO",
          "score_reglas": 76.0,
          "score_ml": 6.76,
          "score_nlp": 83.33,
          "document_score_total": 0.0
        }
      ],
      "false_negatives": [
        {
          "id_siniestro": "SIN-0001",
          "variant_score": 54.22,
          "variant_level": "AMARILLO",
          "score_reglas": 24.0,
          "score_ml": 71.06,
          "score_nlp": 100.0,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "SIN-0002",
          "variant_score": 51.85,
          "variant_level": "AMARILLO",
          "score_reglas": 18.0,
          "score_ml": 71.87,
          "score_nlp": 100.0,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "SIN-0003",
          "variant_score": 67.19,
          "variant_level": "AMARILLO",
          "score_reglas": 47.0,
          "score_ml": 77.61,
          "score_nlp": 100.0,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "SIN-0005",
          "variant_score": 50.2,
          "variant_level": "AMARILLO",
          "score_reglas": 18.0,
          "score_ml": 67.75,
          "score_nlp": 100.0,
          "document_score_total": 0.0
        },
        {
          "id_siniestro": "SIN-0008",
          "variant_score": 75.51,
          "variant_level": "AMARILLO",
          "score_reglas": 38.0,
          "score_ml": 87.28,
          "score_nlp": 100.0,
          "document_score_total": 34.0
        }
      ]
    }
  },
  "metadata": {
    "score_canonico_en_produccion": "reglas_ml_nlp",
    "score_documental_exploratorio": "reglas_ml_nlp_documentos",
    "nota": "La variante documental es comparativa y no sustituye el score canónico vigente."
  }
}
```
