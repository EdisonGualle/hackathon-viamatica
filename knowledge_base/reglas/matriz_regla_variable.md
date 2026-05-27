# Matriz Regla Variable

| ID | Variables mínimas | Evidencia | Gap actual |
|---|---|---|---|
| RF-01 | ramo, cobertura | cobertura, denuncia | ninguno |
| RF-02 | id_siniestro, documentos | inconsistencia_detectada, fecha_emision | ninguno |
| RF-03 | id_proveedor, id_asegurado, id_beneficiario, actor_en_lista_restrictiva_tipo | actor restringido | faltan campos de actor adicional |
| RF-04 | descripcion, sin_tercero_identificado | relato, severidad, tercero | falta campo explícito de tercero |
| RF-05 | dias_inicio_poliza, dias_fin_poliza | fechas | ninguno |
| RF-06 | cobertura, dias_ocurr_reporte | fecha_reporte | ninguno |
| RF-07 | descripcion | similitud, reclamos comparables | requiere mejor NLP |
| S04 | historial_vehiculo_18m | conteo vehículo | falta campo |
| S05 | historial_conductor_18m | conteo conductor | falta campo |
| S06 | solo_rc_recurrente | historial RC | falta campo |
| S10 | sin_tercero_identificado | narrativa y bandera | falta campo |
| S15 | cambio_reciente_datos_asegurado | bandera cambio reciente | falta campo |
