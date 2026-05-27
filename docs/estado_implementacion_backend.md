# Estado de Implementación Backend

Fecha de corte: `2026-05-27`

## Alcance de esta fase

Esta fase se ejecutó bajo la restricción de no rediseñar frontend ni cambiar navegación. El trabajo se concentró en backend, scoring, Document AI, explainability, agente, RAG de caso, auditoría, validación y datos sintéticos.

## Estado por agente

### A1 Architecture / Source of Truth
Estado: `completado`

Artefactos:
- `docs/arquitectura_objetivo_backend.md`
- `docs/contratos_backend.md`

Resultado:
- arquitectura backend objetivo documentada
- contratos de score, evidencia y respuesta definidos

### A2 Scoring Core
Estado: `completado`

Artefactos:
- `src/scoring/__init__.py`
- `src/scoring/scoring_service.py`
- `src/scoring/scoring_config.py`
- `src/scoring/thresholds.py`
- `src/scoring/score_schema.py`

Resultado:
- fórmula única de scoring
- umbrales centralizados
- simulador, pipeline y agente alineados a la fuente de verdad

### A3 Document AI
Estado: `completado`

Artefactos:
- `src/document_ai/ocr.py`
- `src/document_ai/document_classifier.py`
- `src/document_ai/invoice_analyzer.py`
- `src/document_ai/police_report_analyzer.py`
- `src/document_ai/consistency_checker.py`
- `src/document_ai/schemas.py`
- `src/document_ai/service.py`

Resultado:
- OCR simulado
- clasificación documental
- extracción de campos
- inconsistencias documentales persistidas en `document_ai_results`

### A4 Data Expansion
Estado: `completado`

Artefactos:
- `data/synthetic/generate_dataset.py`
- `data/synthetic/generate_documents.py`
- `data/synthetic/document_samples/`
- `docs/modelo_datos_expandido.md`

Resultado:
- dataset expandido con documentos
- soporte de `vehiculos`, `beneficiarios` y evidencia documental sintética
- casos `TC-*` cubiertos con soporte documental

### A5 Explainability / Audit
Estado: `completado`

Artefactos:
- `src/explainability/explain_score.py`
- `src/explainability/evidence_builder.py`
- `src/explainability/reason_codes.py`
- `src/explainability/counterfactuals.py`
- `src/explainability/audit_trail.py`
- `docs/explainability_auditoria.md`

Resultado:
- `reason_codes`
- `evidence_bundle`
- `counterfactual`
- `audit_trail`
- persistencia en `case_explainability`

### A6 Agent Tools
Estado: `completado`

Artefactos:
- `src/agent/fraudia_agent.py`
- `src/agent/tools/claim_tools.py`
- `src/agent/tools/document_tools.py`
- `src/agent/tools/provider_tools.py`
- `src/agent/tools/graph_tools.py`
- `src/agent/tools/scoring_tools.py`
- `src/agent/tools/report_tools.py`

Resultado:
- agente especializado por herramientas
- chat actual integrado con agente V2
- respuestas de caso con evidencia, documentos y auditoría

### A7 RAG Expansion
Estado: `completado`

Artefactos:
- `src/rag/indexer.py`
- `src/rag/chunking.py`
- `src/rag/vector_store.py`
- `src/rag/knowledge_service.py`

Resultado:
- RAG normativo
- RAG de caso
- fuentes diferenciadas entre criterio normativo y evidencia específica del caso

### A8 Validation / Evaluation
Estado: `completado`

Artefactos:
- `tests/test_scoring_service.py`
- `tests/test_document_ai.py`
- `tests/test_explainability.py`
- `tests/test_agent_tools.py`
- `tests/test_audit_report.py`
- `tests/test_case_level_validation.py`
- `docs/evaluacion_modelo_expandida.md`
- `docs/falsos_positivos_negativos.md`

Resultado:
- comparación entre variantes del sistema
- análisis de errores
- segmentación por ramo y ciudad
- cobertura de wrapper conversacional y herramientas

### A9 Human-in-the-loop / Review Workflow
Estado: `completado`

Artefactos:
- `src/review/review_service.py`
- `src/review/review_schema.py`
- `src/review/audit_repository.py`

Resultado:
- estados de revisión humana
- historial de caso
- reportes auditables
- tablas `case_reviews`, `case_status_history`, `audit_reports`

## Estado de validación

Validaciones ejecutadas:
- `venv\Scripts\python.exe -m unittest discover -s tests`
- `venv\Scripts\python.exe -m compileall src`
- `venv\Scripts\python.exe src\models\evaluate_model.py`

Resultado actual:
- `28 tests OK`
- evaluación expandida generada
- frontend sigue operativo sin rediseño

## Deuda técnica residual

### 1. ResourceWarning de SQLite
Estado: `pendiente`

Observación:
- la suite sigue mostrando `ResourceWarning` de conexiones SQLite
- se corrigieron varios puntos evidentes con `with sqlite3.connect(...)`
- los warnings remanentes parecen asociados a interacción de `pandas` / `sklearn` / pipeline repetido en tests

Impacto:
- no rompe funcionalidad
- no bloquea demo
- sí conviene limpiarlo si se busca una base más pulida

### 2. Score documental en producción
Estado: `parcial`

Observación:
- `Document AI` ya existe y se evalúa
- la variante documental está medida en evaluación expandida
- el score canónico vigente sigue siendo `45/40/15`

Impacto:
- es correcto para esta fase
- la integración de `document_score` al score productivo requiere aprobación de cambio canónico

## Juicio técnico

El backend ya dejó de ser solo un MVP tabular simple. El sistema actual soporta:
- scoring centralizado
- documentos sintéticos analizados
- evidencia formal auditable
- agente con herramientas
- RAG de conocimiento y de caso
- revisión humana persistida
- evaluación técnica defendible

El principal pendiente real ya no es funcional. Es limpieza técnica fina de warnings y, si se quisiera una siguiente fase, expansión del score multimodal más allá del esquema canónico vigente.
