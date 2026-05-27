# Arquitectura

FRAUDIA CLAIMS usa una arquitectura por capas para separar datos, reglas, modelos, explicabilidad, agente y visualizacion.

## Flujo Actual

1. **Ingestion**: `src/ingestion/load_data.py` genera/carga dataset sintetico.
2. **Persistencia**: `fraudia.db` centraliza siniestros, polizas, asegurados, vehiculos, proveedores, documentos y scores.
3. **Reglas**: `src/rules/fraud_rules.py` aplica RF-01 a RF-07 y senales ponderadas.
4. **Modelo IA**: `src/models/fraud_model.py` combina Isolation Forest y clasificador supervisado.
5. **NLP**: `src/nlp/narrative_similarity.py` detecta narrativas similares.
6. **Score final**: reglas 45%, ML 40%, NLP 15%.
7. **App**: `src/app/main.py` presenta dashboard, bandeja, red, simulador y agente.
8. **API futura**: `src/api/main.py` expone endpoints de consulta.

## Arquitectura Escalable Futura

- Ingestion batch/API desde core asegurador.
- Base transaccional para siniestros y data lake para historicos.
- Motor de reglas versionado con auditoria.
- Feature store para variables reutilizables.
- Servicio de scoring en tiempo real.
- Monitoreo de drift, falsos positivos y performance.
- Registro de decisiones humanas para retroalimentar modelos.
- Seguridad por roles: analista, antifraude, auditoria, gerencia.

## Principio Operativo

La IA genera alertas de revision. No acusa, no rechaza y no reemplaza decision humana.
