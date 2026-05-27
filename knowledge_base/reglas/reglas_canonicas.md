# Reglas Canónicas

Versión: 2026-05-27

## RF-01
- Nombre: Pérdida Total por Robo en Vehículos.
- Nivel: ROJO.
- Disparador: ramo vehículos y cobertura PTxRB o equivalente explícito de robo total.
- Evidencia esperada: cobertura, ramo, denuncia y narrativa consistente.
- Acción: revisión especializada de campo.
- Limitación: no activar por pérdida total genérica sin referencia de robo.

## RF-02
- Nombre: Falsificación o adulteración documental.
- Nivel: ROJO.
- Disparador: documentos con inconsistencia detectada, fechas imposibles o adulteración explícita.
- Evidencia esperada: tipo de documento, observación, fecha de emisión y fecha de ocurrencia.
- Acción: validación documental reforzada y revisión especializada.

## RF-03
- Nombre: Coincidencia exacta con lista restrictiva.
- Nivel: ROJO.
- Disparador: proveedor, asegurado, beneficiario o actor observado marcado en lista restrictiva.
- Evidencia esperada: identificador del actor y tipo de actor restringido.
- Acción: escalamiento inmediato a la Unidad Antifraude.

## RF-04
- Nombre: Dinámica físicamente imposible.
- Nivel: ROJO.
- Disparador: relato incompatible con la mecánica del evento o evento severo sin sustento básico.
- Evidencia esperada: narrativa, tipo de impacto, presencia de tercero, consistencia temporal.
- Acción: revisión especializada.

## RF-05
- Nombre: Siniestro extremo al borde de vigencia.
- Nivel: AMARILLO.
- Disparador: siniestro ocurrido a menos de 48 horas del inicio o fin de vigencia.
- Acción: revisión documental prioritaria.

## RF-06
- Nombre: Demora atípica en denuncia de robo.
- Nivel: AMARILLO.
- Disparador: cobertura de robo y reporte posterior a 4 días.
- Acción: revisión documental prioritaria.

## RF-07
- Nombre: Narrativa idéntica o clonada.
- Nivel: AMARILLO.
- Disparador: similitud textual alta o texto exacto respecto a otros reclamos.
- Acción: revisión documental y búsqueda de patrón repetido.
