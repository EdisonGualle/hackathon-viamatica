# Scoring Canónico

## Componentes

- `score_reglas`: suma normalizada de reglas y señales en escala `0-100`.
- `score_ml`: score combinado de anomalía y clasificación en escala `0-100`.
- `score_nlp`: score de similitud narrativa en escala `0-100`.

## Fórmula

`score_final = 0.45 * score_reglas + 0.40 * score_ml + 0.15 * score_nlp`

## Overrides

- Si se activa cualquier regla crítica `RF-01..RF-04`, el nivel final es `ROJO`.
- Si no hay crítica, el nivel depende del semáforo canónico.

## Semáforo

- `0-40`: VERDE
- `41-75`: AMARILLO
- `76-100`: ROJO

## Reglas de trazabilidad

Cada caso debe dejar:
- score por componente
- reglas activadas
- evidencia por regla
- explicación resumida
- recomendación operativa
