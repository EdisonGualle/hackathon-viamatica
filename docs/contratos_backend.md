# Contratos Backend

## Contrato único de score
Módulo dueño: `src/scoring/`

### Entrada mínima
```json
{
  "score_reglas": 0,
  "score_ml": 0,
  "score_nlp": 0,
  "active_rules": ["RF-03", "S08"]
}
```

### Salida mínima
```json
{
  "score_final": 82.0,
  "nivel_final": "ROJO",
  "confianza_ia": 78.4,
  "critical_override": true,
  "action": "Revisión especializada reforzada.",
  "breakdown": {
    "weights": {
      "score_reglas": 0.45,
      "score_ml": 0.40,
      "score_nlp": 0.15
    },
    "weighted_components": {
      "score_reglas": 18.0,
      "score_ml": 40.0,
      "score_nlp": 12.0
    },
    "raw_components": {
      "score_reglas": 40.0,
      "score_ml": 100.0,
      "score_nlp": 80.0
    },
    "critical_rules_triggered": ["RF-03"]
  },
  "reason_codes": ["RF-03", "S08"]
}
```

## Contrato único de evidencia por caso
Dueño actual: `src/rules/`
Dueño futuro consolidado: `src/explainability/`

### Forma mínima actual
```json
{
  "codigo": "RF-03",
  "nombre": "Coincidencia con lista restrictiva",
  "tipo": "regla_critica",
  "activada": true,
  "nivel": "ROJO",
  "puntos": 35,
  "variable_principal": "id_proveedor",
  "evidencia": "Proveedor PRV-003 en lista restrictiva",
  "explicacion": "El actor coincide con una lista de observación.",
  "accion_sugerida": "Escalar a revisión especializada",
  "fuente_negocio": "reglas_canonicas/RF-03"
}
```

### Forma objetivo consolidada
```json
{
  "id_siniestro": "TC-RF03-P",
  "reason_codes": ["RF-03", "S07"],
  "evidence_bundle": [
    {
      "source": "rules",
      "code": "RF-03",
      "severity": "ALTA",
      "detail": "Proveedor PRV-003 en lista restrictiva"
    }
  ],
  "counterfactual": [
    "Sin RF-03 el caso baja a AMARILLO"
  ]
}
```

## Contrato del agente
Dueño actual: `src/ai_agent/claims_agent.py`
Dueño objetivo: `src/agent/`

### Consulta factual
- Fuente primaria: `SQL`
- No debe inventar reglas ni política.

### Consulta normativa
- Fuente primaria: `RAG`
- Debe citar fuente.

### Consulta mixta
- Hechos: `SQL`
- Regla/política: `RAG`
- Recomendación: `scoring` y, en fases siguientes, `explainability`.

### Respuesta mínima de caso
```json
{
  "nivel": "ROJO",
  "score": 84.0,
  "senales_detectadas": ["RF-03", "S08"],
  "hechos_del_caso": "Ramo Vehiculos, cobertura PTxRB, proveedor PRV-003",
  "explicacion_de_negocio": "El caso combina proveedor observado y soporte documental incompleto.",
  "recomendacion": "Revisión especializada reforzada.",
  "fuente": ["SQL transaccional", "reglas_canonicas/RF-03"],
  "nota_etica": "El sistema identifica posible fraude y no sustituye la decisión humana."
}
```

## Contrato de `scores_riesgo`
Tabla dueña: `scores_riesgo`

### Columnas obligatorias actuales
- `id_siniestro`
- `score_reglas`
- `score_ml`
- `score_nlp`
- `score_final`
- `nivel`
- `reglas_activadas`
- `detalle_reglas_json`
- `explicacion`
- `confianza_ia`
- `scoring_breakdown_json`
- `fecha_calculo`

## Punto de integración por módulo
- `rules` produce componentes y evidencia base.
- `models` produce `score_ml`.
- `nlp` produce `score_nlp`.
- `scoring` consolida score final.
- `ingestion` persiste salida operativa.
- `app` sólo presenta.
- `agent` sólo consulta y formatea.

## Reglas de ownership
- Ningún módulo fuera de `src/scoring` decide fórmula final.
- Ningún módulo fuera de `src/scoring` decide umbral canónico.
- Ningún módulo fuera de `src/scoring` decide acción por nivel.
- Ningún módulo fuera de `src/document_ai` implementará lógica documental de próxima fase.
- Ningún módulo fuera de `src/explainability` será dueño del bundle auditable final.
