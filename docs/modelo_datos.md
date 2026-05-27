# Modelo de Datos

## Tablas Principales

| Tabla | Proposito |
|-------|-----------|
| `siniestros` | Reclamos reportados, montos, fechas, ramo, cobertura, descripcion y etiqueta simulada. |
| `polizas` | Vigencia, suma asegurada, deducible, canal, ciudad y estado de poliza. |
| `asegurados` | Segmento, antiguedad, ciudad, polizas, reclamos recientes, mora y score cliente. |
| `vehiculos` | Placa sintetica, chasis, motor, marca, modelo y anio. |
| `proveedores` | Talleres, clinicas o peritos con ciudad, tipo, recurrencia y lista restrictiva. |
| `documentos` | Evidencias entregadas, legibilidad e inconsistencias. |
| `scores_riesgo` | Score final, desglose reglas/ML/NLP, nivel, reglas activadas y explicacion. |
| `scores_nlp` | Similitud textual por siniestro. |
| `pares_narrativas_similares` | Pares de reclamos con narrativas similares. |

## Relaciones

- `siniestros.id_poliza -> polizas.id_poliza`
- `siniestros.id_asegurado -> asegurados.id_asegurado`
- `siniestros.id_proveedor -> proveedores.id_proveedor`
- `documentos.id_siniestro -> siniestros.id_siniestro`
- `scores_riesgo.id_siniestro -> siniestros.id_siniestro`

Los identificadores son sinteticos y no contienen informacion personal real.
