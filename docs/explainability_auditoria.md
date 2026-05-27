# Explainability y Auditoría

## Objetivo
Dar trazabilidad formal a cada alerta de riesgo sin cambiar el frontend actual.

## Artefactos persistidos
### `case_explainability`
Una fila por siniestro con:
- `reason_codes_json`
- `evidence_bundle_json`
- `counterfactual_json`
- `audit_trail_json`
- `explicacion_auditable`

### `case_reviews`
Estado actual de revisión humana por caso.

### `case_status_history`
Bitácora cronológica de cambios de estado y comentarios.

### `audit_reports`
Reportes de auditoría persistidos en Markdown.

## Reason codes
Se consolidan desde:
- reglas `RF-*`
- señales `S*`
- códigos documentales `DOC-*`

## Evidence bundle
Cada evidencia registra:
- origen (`rules`, `document_ai`, `ml`, `nlp`)
- código
- severidad
- detalle
- variable o documento asociado

## Contrafactual
Se genera una explicación simple de qué evidencia, al desaparecer, bajaría la prioridad del caso.

## Auditoría humana
El backend soporta estos estados:
- `pendiente_revision`
- `revision_documental`
- `requiere_campo`
- `escalado_antifraude`
- `descartado`
- `caso_observado`
- `cerrado`

## Integración actual
El pipeline ahora ejecuta, en orden:
1. dataset sintético
2. document AI
3. reglas
4. ML
5. NLP
6. explainability
7. review bootstrap

## Uso esperado en fases siguientes
- El agente debe consultar `case_explainability` para justificar respuestas.
- Los reportes descargables deben salir de `audit_reports`.
- La UI puede consumir estos artefactos sin reimplementar lógica.
