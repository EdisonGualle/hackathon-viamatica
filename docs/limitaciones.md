# Limitaciones, Riesgos y Mitigaciones

## Limitaciones

- Dataset sintetico: no representa distribucion real de una aseguradora.
- Etiqueta de fraude simulada: util para demo, no para decisiones productivas.
- Las reglas y pesos son configurables y deben calibrarse con expertos.
- El modelo puede generar falsos positivos.
- La API externa de IA puede tener limites de cuota.

## Riesgos

| Riesgo | Mitigacion |
|--------|------------|
| Confundir alerta con acusacion | Lenguaje de posible fraude y nota etica en la app. |
| Sesgo en datos sinteticos | Documentar origen y validar con datos reales anonimizados. |
| Falsos positivos | Revision humana obligatoria. |
| Modelo caja negra | Mostrar reglas activadas y desglose del score. |
| Dependencia de API externa | Modo local SQL para demo y consultas criticas. |
| Exposicion de datos sensibles | Solo datos sinteticos e identificadores anonimos. |

## Alcance No Decisorio

FRAUDIA no rechaza siniestros, no acusa asegurados y no toma decisiones automaticas de pago. Su funcion es priorizar revision.
