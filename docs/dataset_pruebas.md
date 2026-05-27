# Dataset de Pruebas

## Objetivo

Separar dos universos:

- `portfolio dataset`: portafolio sintético para dashboard, scoring y demo general.
- `test cases dataset`: catálogo determinista para validar reglas, señales, score y respuestas del agente.

## Cobertura mínima

- 7 casos positivos para RF-01..RF-07
- 7 casos negativos espejo para RF-01..RF-07
- 14 casos de señales de score
- 6 casos combinados
- 4 casos limpios
- 5 casos orientados a preguntas del jurado
- 20 casos adicionales para validación integral de dashboard, bandeja, red, simulador, cumplimiento y chat

Total actual esperado en el banco dirigido: `63 casos`

## Nuevos campos sintéticos esperados

- `id_conductor`
- `historial_vehiculo_18m`
- `historial_conductor_18m`
- `solo_rc_recurrente`
- `sin_tercero_identificado`
- `cambio_reciente_datos_asegurado`
- `actor_en_lista_restrictiva_tipo`
- `id_beneficiario`

## Regla de diseño

El dataset dirigido no es aleatorio. Cada caso debe activar exactamente la regla o combinación esperada salvo que el propio caso esté marcado como combinado.

Los casos `TC-*` deben existir tanto en `data/synthetic/test_cases_rules.csv` como en la base operativa `fraudia.db`.
