# Reto Aseguradora del Sur

Versión de trabajo en Markdown basada en el PDF del reto.

## Resumen ejecutivo

Se debe construir un prototipo de IA para analizar siniestros, detectar patrones anómalos o señales de posible fraude, calcular un score de riesgo, clasificar casos y generar alertas explicables para revisión humana.

## Objetivos específicos

1. Cargar y procesar información sintética o pública de siniestros.
2. Identificar patrones atípicos en reclamos.
3. Calcular un score de riesgo por siniestro.
4. Clasificar casos en verde, amarillo y rojo.
5. Generar alertas explicables.
6. Permitir consultas en lenguaje natural.
7. Presentar un dashboard funcional.
8. Documentar modelo, reglas, datos y limitaciones.
9. Entregar código reproducible.
10. Proponer una arquitectura escalable.

## Reglas críticas sugeridas

- RF-01 Pérdida Total por Robo en Vehículos.
- RF-02 Falsificación o adulteración documental.
- RF-03 Coincidencia con lista restrictiva.
- RF-04 Dinámica físicamente imposible.
- RF-05 Borde extremo de vigencia.
- RF-06 Demora atípica en denuncia de robo.
- RF-07 Narrativa idéntica o clonada.

## Señales sugeridas

- Borde de vigencia.
- Demora por robo.
- Frecuencia asegurado.
- Frecuencia vehículo.
- Frecuencia conductor.
- Recurrencia solo RC.
- Proveedor recurrente.
- Documentos incompletos.
- Dinámica sospechosa.
- Evento sin tercero.
- Documentos inconsistentes.
- Reporte tardío.
- Narrativas similares.
- Monto cercano a suma asegurada.

## Preguntas del agente

- Top 10 de mayor riesgo.
- Por qué este siniestro fue marcado.
- Proveedores con más alertas.
- Ramos con mayor sospecha.
- Ciudades con más alertas.
- Asegurados con mayor frecuencia.
- Documentos faltantes en críticos.
- Casos con montos atípicos.
- Casos cerca del inicio de póliza.
- Patrones que se repiten.
- Resumen ejecutivo.
- Qué revisar primero y por qué.

## Restricciones éticas

- Datos sintéticos o públicos.
- No acusar fraude confirmado.
- No rechazar automáticamente.
- Mantener revisión humana.
