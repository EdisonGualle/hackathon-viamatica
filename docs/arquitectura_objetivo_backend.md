# Arquitectura Objetivo Backend

## Objetivo
Mantener el frontend actual y mover la complejidad del producto a un backend modular, auditable y reutilizable.

## Capas backend
1. `data.synthetic`
   - Genera siniestros, casos dirigidos y, en la siguiente fase, documentos sintéticos.
2. `rules`
   - Evalúa reglas y señales del reto.
   - Produce evidencia estructurada por caso.
3. `models`
   - Entrena y calcula `score_ml`.
4. `nlp`
   - Calcula `score_nlp` y similitud de narrativas.
5. `scoring`
   - Fuente única de verdad para fórmula, umbrales, override crítico, confianza y acción sugerida.
6. `document_ai`
   - Fase siguiente. Analiza documentos, extrae campos y produce inconsistencias reutilizables.
7. `explainability`
   - Fase siguiente. Consolida reason codes, evidencia y trail auditable.
8. `rag`
   - Recupera conocimiento normativo y, en fase siguiente, evidencia documental del caso.
9. `agent`
   - Fase siguiente. Orquesta herramientas especializadas.
10. `review`
   - Fase siguiente. Registra revisión humana y auditoría operativa.
11. `ingestion`
   - Ejecuta el pipeline y persiste `scores_riesgo`.
12. `app`
   - Consume resultados ya calculados sin reimplementar lógica de negocio.

## Dueño por responsabilidad
- Dataset sintético: `data.synthetic`
- Reglas y señales: `rules`
- Score ML: `models`
- Score NLP: `nlp`
- Score final, nivel, confianza, acción: `scoring`
- Evidencia documental: `document_ai`
- Explicación auditable: `explainability`
- Respuestas híbridas del asistente: `agent` + `rag`
- Revisión humana: `review`
- Persistencia operativa: `ingestion`

## Flujo backend actual
1. `data.synthetic.generate_dataset` genera base y casos dirigidos.
2. `rules.fraud_rules.procesar_todos` produce `score_reglas`, `reglas_activadas`, `detalle_reglas_json`, `explicacion_reglas`.
3. `models.fraud_model` produce `score_ml`.
4. `nlp.narrative_similarity` produce `score_nlp` y pares similares.
5. `scoring.scoring_service.compute_assessment` calcula:
   - `score_final`
   - `nivel_final`
   - `confianza_ia`
   - `critical_override`
   - `action`
6. `ingestion.load_data` persiste `scores_riesgo`.
7. `app.main` y `ai_agent.claims_agent` consumen esos resultados ya cerrados.

## Principios obligatorios
- No duplicar fórmula de score fuera de `src/scoring`.
- No duplicar umbrales fuera de `src/scoring`.
- No recalcular nivel final en frontend.
- El agente no inventa score ni recomendación; los consulta desde backend.
- El frontend puede presentar resultados, pero no ser dueño de la lógica.

## Duplicaciones identificadas y decisión
### Duplicación cerrada en esta fase
- Fórmula `45/40/15`: movida a `src/scoring`.
- Umbrales `0-40 / 41-75 / 76-100`: movidos a `src/scoring`.
- Recomendación por nivel del agente: movida a `src/scoring`.
- Simulador demo: ahora consume `score_simulated_claim`.
- Pipeline: ahora consume `compute_assessment`.

### Duplicación que queda aceptada temporalmente
- Heurísticas del simulador para construir señales demo.
  - Se mantienen locales en `src/app/main.py` porque pertenecen a la interacción demo.
  - El cierre de score, nivel y confianza ya sale de `src/scoring`.
- Score interno de `rules` para `score_reglas`.
  - Se mantiene como componente especializado del motor de reglas.
  - No sustituye el score final unificado.

## Siguiente fase técnica
- Agregar `document_ai` como nuevo productor de evidencia y `score_documental`.
- Agregar `explainability` para bundle auditable.
- Agregar `review` para estados humanos.
- Mantener frontend congelado y conectar sólo outputs backend.
