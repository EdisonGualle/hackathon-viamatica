# Validación Integral con 20 Casos Nuevos

## Resumen

Se agregaron 20 casos nuevos `TC-X01` a `TC-X20` al banco dirigido y a la base operativa `fraudia.db`.

Objetivo:
- validar dashboard
- validar bandeja de casos
- validar red de relaciones
- validar simulador demo
- validar cumplimiento
- validar agente IA

Total actual del banco dirigido: `63 casos`

## Casos nuevos y propósito

| Caso | Objetivo principal | Página principal | Resultado esperado |
|---|---|---|---|
| `TC-X01` | concentración de rojos en `PRV-003` | Dashboard / Red | `ROJO` |
| `TC-X02` | dinámica imposible con `PRV-003` | Red / Bandeja | `ROJO` |
| `TC-X03` | concentración de rojos en `PRV-009` | Dashboard / Red | `ROJO` |
| `TC-X04` | proveedor recurrente + docs faltantes | Dashboard / Bandeja | `AMARILLO` |
| `TC-X05` | ciudad Quito con inconsistencia documental | Dashboard | `ROJO` |
| `TC-X06` | ciudad Guayaquil con robo tardío crítico | Dashboard / Bandeja | `ROJO` |
| `TC-X07` | monto extremo | Bandeja | `AMARILLO` |
| `TC-X08` | caso limpio de control | Dashboard / Bandeja | `VERDE` |
| `TC-X09` | asegurado en lista restrictiva | Bandeja / Chat | `ROJO` |
| `TC-X10` | beneficiario en lista restrictiva | Bandeja / Chat | `ROJO` |
| `TC-X11` | recurrencia solo RC | Bandeja | `AMARILLO` |
| `TC-X12` | recurrencia vehículo + conductor | Bandeja | `AMARILLO` |
| `TC-X13` | narrativa clonada 1 | Red / Chat | `AMARILLO` |
| `TC-X14` | narrativa clonada 2 | Red / Chat | `AMARILLO` |
| `TC-X15` | sin tercero identificado | Bandeja | `AMARILLO` |
| `TC-X16` | PTxRB + cambio reciente del asegurado | Chat / Bandeja | `ROJO` |
| `TC-X17` | borde exacto de vigencia | Simulador / Bandeja | `AMARILLO` |
| `TC-X18` | reporte tardío no crítico | Simulador / Bandeja | `AMARILLO` |
| `TC-X19` | proveedor observado + monto alto | Simulador / Red | `ROJO` |
| `TC-X20` | caso integral para agente y cumplimiento | Chat / Cumplimiento | `ROJO` |

## Flujo de validación por página

### 1. Dashboard

Validar:
- que existan los tres niveles
- que `PRV-003` y `PRV-009` aparezcan reforzados en alertas
- que Quito y Guayaquil aumenten concentración relativa

Casos a revisar:
- `TC-X01`
- `TC-X03`
- `TC-X05`
- `TC-X06`
- `TC-X08`

### 2. Bandeja de casos

Filtrar y revisar:
- `ROJO`: `TC-X01`, `TC-X02`, `TC-X03`, `TC-X09`, `TC-X10`, `TC-X16`, `TC-X19`, `TC-X20`
- `AMARILLO`: `TC-X04`, `TC-X06`, `TC-X07`, `TC-X11`, `TC-X12`, `TC-X13`, `TC-X14`, `TC-X15`, `TC-X17`, `TC-X18`
- `VERDE`: `TC-X08`

### 3. Red de relaciones

Esperar:
- nodos más densos alrededor de `PRV-003` y `PRV-009`
- relación visible entre `TC-X13` y `TC-X14` por narrativa repetida
- mayor concentración de rojos en proveedores observados

### 4. Simulador demo

Probar presets:
- `Robo total` -> debe tender a `ROJO`
- `Proveedor observado` -> debe tender a `ROJO`
- `Borde de poliza` -> debe tender a `AMARILLO`
- `Reporte tardio` -> debe tender a `AMARILLO`
- `Normal` -> debe tender a `VERDE`

Casos espejo de referencia:
- `TC-X17`
- `TC-X18`
- `TC-X19`

### 5. Cumplimiento

Cruzar con:
- `docs/reto_checklist.md`
- `docs/fuente_verdad_negocio.md`
- `docs/scoring_canonico.md`
- `knowledge_base/reglas/reglas_canonicas.md`

Caso recomendado:
- `TC-X20`

### 6. Agente IA

Preguntas sugeridas:
- `por que este siniestro fue marcado TC-X20`
- `por que este siniestro fue marcado TC-X09`
- `que significa RF-03`
- `que evidencia revisar en RF-02`
- `proveedores con mas alertas`
- `patrones repetidos`
- `que revisar primero y por que`

Esperar:
- fuente en consultas normativas
- estructura completa en consultas de caso
- nota ética visible

## Resultado mínimo esperado

El sistema se considera validado con estos 20 casos si:
- los 8 casos esperados en `ROJO` quedan `ROJO`
- los 10 casos esperados en `AMARILLO` quedan `AMARILLO`
- `TC-X08` queda `VERDE`
- `PRV-003` y `PRV-009` aparecen reforzados en dashboard o red
- `TC-X13` y `TC-X14` aparecen como patrón repetido
- el agente responde `TC-X20` con explicación y fuente
