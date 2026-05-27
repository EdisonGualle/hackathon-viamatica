# Falsos Positivos y Falsos Negativos

Análisis exploratorio sobre la variante con soporte documental. La lectura es útil para calibración del prototipo y para explicar límites del dataset sintético.

## Falsos positivos

```json
[
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
]
```

## Falsos negativos

```json
[
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
```

## Interpretación

- Un falso positivo es aceptable si la evidencia justifica revisión humana y el sistema no acusa automáticamente.
- Un falso negativo es el riesgo más delicado; estos casos deben usarse para reforzar reglas, NLP y evidencia documental.
- La etiqueta sigue siendo simulada, por lo que estas observaciones sirven para calibración, no para inferencia de performance productiva real.
