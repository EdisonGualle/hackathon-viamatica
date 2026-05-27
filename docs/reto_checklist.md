# Checklist del Reto

Fecha de corte: 2026-05-27
Fuente principal: `hackIAthon - reto Aseguradora del Sur.pdf`

## Requisitos funcionales

| ID | Requisito | Estado inicial | Responsable | Evidencia actual | Prueba esperada |
|---|---|---|---|---|---|
| REQ-01 | Cargar datos sintéticos de siniestros | cumple | ingestion/data | `src/ingestion/load_data.py`, `data/synthetic/generate_dataset.py` | pipeline genera DB reproducible |
| REQ-02 | Analizar variables de póliza, asegurado, proveedor, documentos y fechas | parcial | rules/data | existen campos base pero faltan variables de vehículo/conductor/RC/cambio reciente | test de reglas con nuevos campos |
| REQ-03 | Detectar alertas por reglas | cumple | rules | `src/rules/fraud_rules.py` | tests unitarios por RF/S |
| REQ-04 | Calcular score híbrido | parcial | models/ingestion | score existe pero NLP mal escalado | test de fórmula 45/40/15 |
| REQ-05 | Clasificar en verde/amarillo/rojo | cumple | rules/ingestion | semáforo existe | test de thresholds 0-40/41-75/76-100 |
| REQ-06 | Explicar motivo de la alerta | parcial | rules/agent/app | explicación existe pero sin contrato uniforme ni fuente documental | test de estructura de respuesta |
| REQ-07 | Consultas en lenguaje natural | parcial | ai_agent | agente actual responde varias preguntas | test de cobertura total jurado |
| REQ-08 | Dashboard funcional | cumple | app | `src/app/main.py` | app carga KPIs, bandeja y chat |
| REQ-09 | Red de relaciones | cumple | app | tab red existente | smoke visual/manual |
| REQ-10 | Exportación o bandeja de casos sospechosos | cumple | app | bandeja y reporte demo | prueba manual |
| REQ-11 | API mínima futura | cumple | api | `src/api/main.py` | smoke `/health` y endpoints |
| REQ-12 | Documentar reglas, modelo, datos y limitaciones | parcial | docs | docs existen pero están inconsistentes | validación cruzada contra fuente de verdad |
| REQ-13 | Alternativa local a dependencias externas | cumple | ai_agent | fallback local SQL existente | test sin API key |
| REQ-14 | RAG interno documental | no cumple | rag | no existe actualmente | test de retrieval y citas |

## Preguntas del jurado

| ID | Pregunta | Estado inicial | Responsable | Prueba esperada |
|---|---|---|---|---|
| J-01 | Top 10 siniestros con mayor riesgo | cumple | ai_agent | respuesta factual con SQL |
| J-02 | Por qué este siniestro fue marcado | parcial | ai_agent/rag | respuesta mixta SQL + RAG |
| J-03 | Qué proveedores concentran más alertas | cumple | ai_agent | ranking y lectura operativa |
| J-04 | Qué ramos tienen mayor porcentaje sospechoso | cumple | ai_agent | agregado por ramo |
| J-05 | Qué ciudades concentran alertas | cumple | ai_agent | agregado por ciudad |
| J-06 | Qué asegurados tienen mayor frecuencia | cumple | ai_agent | ranking asegurados |
| J-07 | Qué documentos faltan en críticos | cumple | ai_agent | agregado documental |
| J-08 | Qué casos tienen montos atípicos | cumple | ai_agent | consulta SQL |
| J-09 | Qué siniestros ocurrieron cerca del inicio de la póliza | cumple | ai_agent | consulta SQL |
| J-10 | Qué patrones se repiten en reclamos sospechosos | parcial | ai_agent/rag | mezcla SQL + RAG |
| J-11 | Resumen ejecutivo de casos críticos | cumple | ai_agent | resumen ejecutivo |
| J-12 | Qué revisar primero y por qué | parcial | ai_agent/rag | priorización razonada |

## Requisitos éticos y técnicos

| ID | Requisito | Estado inicial | Responsable | Prueba esperada |
|---|---|---|---|---|
| GOV-01 | No acusar fraude confirmado | cumple | agent/app/docs | texto restringido |
| GOV-02 | Revisión humana obligatoria | cumple | agent/app/docs | nota ética visible |
| GOV-03 | Datos sintéticos/anonimizados | cumple | data | inspección de dataset |
| GOV-04 | Código reproducible | parcial | repo | pipeline + tests verdes |
| GOV-05 | Modularidad y trazabilidad | parcial | all | contratos uniformes y docs fuente |
