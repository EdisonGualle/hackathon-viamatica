# Fuente de Verdad de Negocio

Fecha de vigencia: 2026-05-27
Este documento prevalece sobre README, docs previos, agente y UI cuando exista contradicción.

## Objetivo del sistema

El sistema genera alertas de revisión de posible fraude. No acusa, no rechaza siniestros y no sustituye la decisión humana.

## Semáforo canónico

- VERDE: `0` a `40`
- AMARILLO: `41` a `75`
- ROJO: `76` a `100`

## Score final canónico

`score_final = 0.45 * score_reglas + 0.40 * score_ml + 0.15 * score_nlp`

Reglas:
- `score_reglas` en escala `0-100`
- `score_ml` en escala `0-100`
- `score_nlp` en escala `0-100`

## Reglas críticas que fuerzan ROJO

- `RF-01`
- `RF-02`
- `RF-03`
- `RF-04`

## Lenguaje permitido

Se permite usar:
- `posible fraude`
- `alerta de revisión`
- `requiere revisión especializada`
- `señales de alerta identificadas`

No se permite usar:
- `fraude confirmado`
- `cliente fraudulento`
- `rechazo automático`
- `acusación`

## Modelo operativo del agente

- SQL para hechos transaccionales.
- RAG para reglas, criterios, tipologías, playbooks y ética.
- SQL + RAG para explicaciones mixtas.

## Acciones por nivel

- VERDE: continuar flujo normal con monitoreo operativo.
- AMARILLO: revisión documental prioritaria por Unidad Antifraude.
- ROJO: revisión especializada de campo o validación reforzada.

## Reglas críticas canónicas

- `RF-01`: Cobertura Pérdida Total por Robo en Vehículos (PTxRB).
- `RF-02`: Evidencia de falsificación o adulteración documental.
- `RF-03`: Coincidencia exacta con lista restrictiva de actor observado.
- `RF-04`: Dinámica del accidente físicamente imposible.

## Contradicciones a corregir obligatoriamente

- README usa pesos `50/35/15`; debe migrar a `45/40/15`.
- El prompt del agente usa umbrales `70/35`; debe migrar a `76/41`.
- RF-04 debe tratarse como regla crítica ROJO en todas las capas.
- NLP no puede persistirse como `0/4/8` bajo el nombre `score_nlp`.
