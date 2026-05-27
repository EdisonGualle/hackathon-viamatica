# Reglas de Negocio

## Reglas Criticas

| Codigo | Regla | Nivel |
|--------|-------|-------|
| RF-01 | Cobertura Perdida Total por Robo | ROJO |
| RF-02 | Evidencia de falsificacion o adulteracion documental | ROJO |
| RF-03 | Asegurado, beneficiario o proveedor en lista restrictiva | ROJO |
| RF-04 | Dinamica del accidente fisicamente imposible | ROJO |
| RF-05 | Siniestro extremo al borde de vigencia menor a 48 horas | AMARILLO |
| RF-06 | Demora atipica en denuncia de robo mayor a 4 dias | AMARILLO |
| RF-07 | Narrativa identica o clonada | AMARILLO |

## Rangos de Score

| Rango | Nivel | Accion |
|-------|-------|--------|
| 0-40 | VERDE | Continuar flujo normal |
| 41-75 | AMARILLO | Revision documental por Unidad Antifraude |
| 76-100 | ROJO | Revision especializada de campo |

## Score Final

`Score Final = 45% Reglas + 40% Machine Learning + 15% NLP`

Las reglas criticas RF-01 a RF-04 fuerzan nivel ROJO aunque el score ponderado sea menor.
