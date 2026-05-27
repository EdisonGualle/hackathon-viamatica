# Modelo de Datos Expandido

## Objetivo
Extender el modelo sintético para soportar análisis documental, trazabilidad de evidencia y siguientes fases de auditoría.

## Tablas activas en esta fase
- `asegurados`
- `proveedores`
- `polizas`
- `conductores`
- `vehiculos`
- `beneficiarios`
- `siniestros`
- `documentos`
- `document_ai_results`
- `scores_riesgo`
- `scores_nlp`
- `pares_similares`

## Nuevos activos incorporados
### `vehiculos`
Campos principales:
- `id_vehiculo`
- `placa`
- `chasis`
- `marca`
- `modelo`
- `anio`

### `beneficiarios`
Campos principales:
- `id_beneficiario`
- `nombre`
- `en_lista_restrictiva`

### Nuevos campos en `siniestros`
- `id_vehiculo`
- `placa_vehiculo`
- `chasis_vehiculo`

### `documentos`
La tabla deja de ser un flag mínimo y pasa a representar evidencia sintética estructurada.

Campos principales:
- `id_documento`
- `id_siniestro`
- `tipo_documento`
- `nombre_archivo`
- `file_path`
- `presente`
- `texto_documento`
- `texto_ocr`
- `legibilidad_hint`
- `fecha_emision`
- `fecha_evento_doc`
- `monto_doc`
- `proveedor_doc`
- `placa_doc`
- `inconsistencia_detectada`

### `document_ai_results`
Persistencia del análisis documental backend.

Campos principales:
- `id_documento`
- `id_siniestro`
- `tipo_detectado`
- `legibilidad_score`
- `presente`
- `campos_extraidos_json`
- `inconsistencias_json`
- `document_score`
- `recomendacion`

## Relaciones nuevas
- `siniestros.id_vehiculo -> vehiculos.id_vehiculo`
- `siniestros.id_beneficiario -> beneficiarios.id_beneficiario`
- `documentos.id_siniestro -> siniestros.id_siniestro`
- `document_ai_results.id_documento -> documentos.id_documento`

## Tipos documentales sintéticos
- `aviso_siniestro`
- `factura_taller`
- `parte_policial`
- `informe_pericial`
- `cedula`

## Casos documentales cubiertos
- factura con fecha previa al evento
- proveedor documental inconsistente
- monto documental incoherente
- placa documental inconsistente
- denuncia ausente en robo
- documento ilegible

## Criterio de uso
- `documentos` es la fuente de evidencia sintética base.
- `document_ai_results` es la fuente de análisis documental estructurado.
- `rules` puede seguir consumiendo `inconsistencia_detectada` sin romper compatibilidad.
- `agent` y `explainability` deben consumir `document_ai_results` en fases siguientes.
