# hackIAthon - Reto Aseguradora del Sur

> Documento convertido desde `hackIAthon - reto Aseguradora del Sur.pdf` para lectura y analisis de implementacion.

- Paginas del PDF: 14

---

## Pagina 1

hackIAthon Reto Aseguradora del Sur Detector de Posibles Fraudes en Siniestros

usando

Inteligencia

Artificial

Documento de levantamiento funcional, alcance técnico, entregables y criterios de evaluación Elemento Definición Sector Asegurador Tipo de solución Prototipo funcional basado en Inteligencia Artificial Datos permitidos Datos públicos reales o datos sintéticos Entregables Prototipo funcional, código fuente, dataset, documentación y demo Herramientas esperadas Claude, ChatGPT, GitHub, Python, Oracle y R Principio clave La solución genera alertas de revisión, no acusaciones automáticas de fraude

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 2

Contenido ● 1. Resumen ejecutivo ● 2. Planteamiento del problema ● 3. Objetivos ● 4. Alcance del reto ● 5. Usuarios beneficiarios ● 6. Datos mínimos requeridos ● 7. Señales de posible fraude ● 8. Reglas de negocio sugeridas ● 9. Uso esperado de Inteligencia Artificial ● 10. Funcionalidades del prototipo ● 11. Casos de uso ● 12. Preguntas que el agente de IA debe responder ● 13. Score de riesgo sugerido ● 14. Entregables obligatorios ● 15. Estructura del repositorio ● 16. Requisitos técnicos y estándares ● 17. Seguridad, privacidad y ética ● 18. Criterios de evaluación ● 19. Métricas sugeridas ● 20. Riesgos y mitigaciones ● 21. Formato de presentación

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 3

1. Resumen ejecutivo El sector asegurador enfrenta el reto de identificar oportunamente posibles patrones irregulares en los

siniestros

reportados.

La

detección

manual

depende

de

la

experiencia

del

analista,

reglas

dispersas,

revisión

documental

y

cruces

de

información

que

pueden

tomar

tiempo.

El reto consiste en desarrollar un prototipo funcional basado en Inteligencia Artificial que analice información

de

siniestros

y

genere

un

score

de

riesgo

de

posible

fraude,

acompañado

de

alertas

explicables,

patrones

detectados

y

recomendaciones

para

revisión

humana.

La solución no debe emitir una acusación de fraude ni rechazar automáticamente un siniestro. Su propósito

es

identificar

casos

sospechosos,

anómalos

o

de

mayor

riesgo

para

que

sean

revisados

por

un

analista

especializado.

2. Planteamiento del problema En una aseguradora, los siniestros pueden presentar señales de riesgo que no siempre son evidentes en

una

revisión

individual.

Algunas

alertas

aparecen

al

cruzar

variables

de

pólizas,

asegurados,

proveedores,

documentos,

fechas,

montos

e

historial

de

reclamos.

● Frecuencia inusual de reclamos por asegurado o póliza. ● Montos reclamados superiores al promedio del ramo o del tipo de siniestro. ● Repetición de beneficiarios, proveedores, talleres, intermediarios asociados a casos observados. ● Reclamos ocurridos muy cerca de la fecha de inicio y fin de vigencia de la póliza. ● Documentos incompletos, ilegibles o inconsistentes. ● Narrativas similares entre diferentes reclamos. ● Cambios recientes en datos del asegurado antes del siniestro. ● Reporte tardío del evento frente a la fecha de ocurrencia.

3. Objetivos

3.1 Objetivo general Desarrollar un prototipo funcional de Inteligencia Artificial que permita analizar siniestros de seguros,

detectar

patrones

anómalos

o

señales

de

posible

fraude,

asignar

un

score

de

riesgo

y

generar

explicaciones

para

apoyar

la

revisión

del

analista.

3.2 Objetivos específicos 1. Cargar y procesar información sintética o pública de siniestros. 2. Identificar patrones atípicos en reclamos. 3. Calcular un score de riesgo por siniestro. 4. Clasificar casos en niveles de riesgo: verde, amarillo, rojo. 5. Generar alertas explicables para el analista. 6. Permitir consultas en lenguaje natural sobre los casos detectados.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 4

7. Presentar un dashboard o interfaz funcional. 8. Documentar el modelo, reglas, datos y limitaciones. 9. Entregar código fuente ejecutable y reproducible. 10. Proponer una arquitectura escalable para una implementación futura.

4. Alcance del reto

4.1 Incluye ● Carga de un dataset de siniestros, pólizas, asegurados, vehículos (placa,chasis, motor, marca,

modelo,año),

beneficiarios,

proveedores

y

documentos. ● Análisis de variables del reclamo, pólizas, asegurados, vehículos (placa,chasis, motor, marca, modelo,año),

beneficiarios,

proveedores

y

documentos. ● Detección de anomalías o señales de riesgo. ● Generación de score de posible fraude. ● Priorización de casos para revisión, semáforo: verde, amarillo, rojo. ● Explicación del motivo de cada alerta. ● Interfaz, dashboard, aplicación o notebook funcional para la demo. ● Exportación, o visualización de un resumen o bandeja de casos sospechosos.

4.2 No incluye ● Acusar formalmente a un asegurado de fraude. ● Rechazar automáticamente un siniestro. ● Sustituir el análisis humano. ● Usar datos personales reales o información confidencial. ● Tomar decisiones automáticas de pago o rechazo. ● Presentar conclusiones legales definitivas.

5. Usuarios beneficiarios Usuario Beneficio esperado Analista de siniestros Priorización de casos y explicación de alertas. Analista antifraude Identificación temprana de patrones sospechosos. Jefatura de siniestros Visión consolidada de riesgos operativos. Riesgos Monitoreo de exposición y comportamiento anómalo. Auditoría interna Evidencia y trazabilidad para revisión. Tecnología Base para prototipo escalable e integrable. Gerencia Reducción potencial de pérdidas y mejora del control.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 5

6. Datos mínimos requeridos Para el reto se recomienda trabajar con datos sintéticos o públicos. Si se representa información interna

de

una

aseguradora,

los

datos

deberán

ser

sintéticos

y

no

contener

información

personal

identificable.

6.1 Tabla: Siniestros Campo Descripción id_siniestro Identificador único del siniestro. id_poliza Identificador de la póliza. id_asegurado Identificador anónimo del asegurado. ramo Vehículos, salud, vida, generales, hogar u otro. cobertura Choque, robo, atención médica, incendio, daño u otro. fecha_ocurrencia Fecha del evento. fecha_reporte Fecha de notificación. monto_reclamado Valor solicitado por el asegurado o proveedor. monto_estimado Valor estimado por la aseguradora. monto_pagado Valor pagado, si aplica. estado

Reserva, Pago Total, Pago Parcial, Anticipo, Negativa, Cierre Sin Consecuencia, Liquidado sucursal Sucursal del siniestro. descripcion Texto libre del reclamo. documentos_completos Indicador Sí/No. beneficiario Taller, clínica, perito u otro. dias_desde_inicio_poliza Días entre inicio de póliza y siniestro. dias_desde_fin_poliza Días entre fin de póliza y siniestro. dias_entre_ocurrencia_reporte Diferencia entre ocurrencia y reporte. historial_siniestros_asegurado Número de siniestros previos del asegurado. etiqueta_fraude_simulada 0/1, solo para entrenamiento o evaluación si aplica.

6.2 Tablas complementarias sugeridas Tabla Campos mínimos Pólizas

id_poliza, id_asegurado, ramo, fecha_inicio, fecha_fin, prima, suma_asegurada, deducible, canal_venta, ciudad, estado_poliza. Asegurados sintéticos id_asegurado, segmento, antigüedad, ciudad, número de pólizas, reclamos últimos 12 meses, mora actual, score cliente simulado. Beneficiarios / Proveedores id_proveedor, tipo, ciudad, reclamos asociados, monto promedio reclamado, porcentaje de casos observados, antigüedad. Documentos id_documento, id_siniestro, tipo_documento, entregado, legible, fecha_emision, inconsistencia_detectada, observacion.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 6

7. Señales de posible fraude Señal Ejemplo

Puntuación Reclamo cercano al borde de vigencia Siniestro ocurrido pocos días después de contratar la póliza o antes del fin de vigencia (menor o igual a 30 días). Hasta 8 pts• ≤ 10 días: 8 pts• 11 a 30 días: 4 pts• > 30 días: 0 pts Demora denuncia por robo Tiempos prolongados entre la ocurrencia del evento y la denuncia formal en casos de Robo. Hasta 8 pts• > 48 horas: 8 pts• 24 a 48 horas: 4 pts• < 24 horas: 0 pts Alta frecuencia de reclamos Asegurado Asegurado con múltiples siniestros en un periodo menor o igual a 18 meses Hasta 8 pts• ≥ 3 siniestros: 8 pts• 2 siniestros: 4 pts• 01 siniestros: 0 pts Alta frecuencia de reclamos Vehículo Vehículo con múltiples siniestros en un periodo menor o igual a 18 meses Hasta 6 pts• ≥ 3 siniestros: 6 pts• 2 siniestros: 3 pts• 01 siniestros: 0 pts Alta frecuencia de conductor Vehículo Conductor presente en múltiples siniestros en un periodo menor o igual a 18 meses Hasta 8 pts• ≥ 3 siniestros: 8 pts• 2 siniestros: 4 pts• 01 siniestros: 0 pts Alta frecuencia reclamos solo RC Frecuencia atípica de siniestros donde solo se afecta la cobertura de Responsabilidad Civil RC. Hasta 6 pts• > 2 eventos previos de solo RC 6 pts• 1 evento previo: 3 pts Beneficiario / Proveedor recurrente Proveedor asociado a varios casos observados. Hasta 10 pts• En Lista Restrictiva: 10 pts• En 2 casos observados este año: 5 pts Documentos incompletos Falta denuncia, factura, informe o evidencia requerida. Hasta 4 pts• Falta documento legal obligatorio: 4 pts Dinámica sospechosa Tipos de accidentes que requieren revisión minuciosa cruzada Frontal, Posterior, Volcadura, Múltiple). Hasta 6 pts• Relato ilógico vs tipo de impacto: 6 pts• Accidente múltiple de madrugada: 3 pts Eventos Sin tercero identificado Siniestros donde el vehículo asegurado resulta afectado, pero no existe o huye el tercer involucrado. Hasta 6 pts• Daño severo sin rastro del tercero ni cámaras: 5 pts Documentos inconsistentes Fechas no coinciden, valores diferentes o documentos ilegibles. Hasta 10 pts• Alteración confirmada o fechas de factura previas al evento: 10 pts Reporte tardío El siniestro se reporta muchos días después del evento. Hasta 5 pts• > 7 días: 5 pts• 4 a 7 días: 3 pts• ≤ 3 días: 0 pts

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 7

Narrativas similares Descripciones parecidas entre varios reclamos. Hasta 8 pts• > 85% de similitud textual con otro reclamo: 8 pts• 70% - 84% 4 pts Monto cercano o superior a suma asegurada Valor reclamado representa una proporción muy alta de la cobertura. Hasta 5 pts• Reclamo 95% de la suma asegurada o 50% del promedio de reparación: 4 pts

8. Reglas de negocio sugeridas Críticas

Código Regla Clasificación RF01 Cobertura Pérdida Total por Robo PTxRB Rojo RF02 Evidencia de Falsificación o Adulteración Documental Evidente Rojo RF03 Asegurado, Beneficiario o APS Coincidencia Exacta con "Lista Restrictiva" Rojo RF04 Dinámica del Accidente Físicamente Imposible Rojo RF05 Siniestro Extremo al Borde de Vigencia (< 48 hrs) Amarillo RF06 Demora Atípica en Denuncia de Robo (> 4 días) Amarillo RF07 Narrativa Idêntica Clonada) Amarillo

9. Uso esperado de Inteligencia Artificial Enfoque Aplicación esperada

Machine Learning supervisado Predicción de probabilidad de posible fraude usando etiqueta simulada. Detección de anomalías Identificación de casos fuera del comportamiento esperado. Procesamiento de lenguaje natural Análisis de descripciones, similitud textual, extracción de entidades y resúmenes. Agente de IA explicativo Consultas en lenguaje natural sobre casos, alertas, proveedores y patrones. Enfoque híbrido Combinación de reglas de negocio, modelo de anomalías, análisis textual, dashboard y explicación. La mejor solución combinaría reglas de negocio, modelo de anomalías o clasificación, análisis de texto, dashboard

y

agente

de

explicación.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 8

10. Funcionalidades del prototipo

10.1 Funcionalidades mínimas 11. Carga de datos de siniestros. 12. Cálculo de variables de riesgo. 13. Detección de alertas por reglas. 14. Modelo de IA para score de posible fraude. 15. Clasificación de riesgo: bajo, medio, alto o crítico. 16. Dashboard o interfaz para revisar casos. 17. Explicación automática del motivo de la alerta.

10.2 Funcionalidades deseables ● Chat con los casos y consultas en lenguaje natural. ● Análisis del texto del reclamo. ● Red de relaciones entre asegurados, proveedores y casos. ● Ranking de proveedores con mayor concentración de alertas. ● Simulación de ahorro potencial. ● Exportación de reporte para auditoría. ● API funcional para integración futura.

11. Casos de uso Código Caso de uso Resultado esperado CU01 Cargar siniestros

El sistema valida estructura y procesa la información. CU02 Calcular score de riesgo Cada siniestro recibe un puntaje de riesgo. CU03 Priorizar casos El analista visualiza los casos ordenados por riesgo. CU04 Explicar alerta El sistema muestra factores como monto atípico, proveedor recurrente o documentos incompletos. CU05 Consultar mediante IA El usuario obtiene respuestas basadas en los datos. CU06 Generar reporte El sistema genera un resumen ejecutivo de casos de mayor riesgo.

12. Preguntas que el agente de IA debe responder 18. ¿Cuáles son los 10 siniestros con mayor riesgo de posible fraude? 19. ¿Por qué este siniestro fue marcado como alto riesgo? 20. ¿Qué proveedores concentran más alertas? 21. ¿Qué ramos tienen mayor porcentaje de casos sospechosos?

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 9

22. ¿Qué ciudades presentan mayor concentración de alertas? 23. ¿Qué asegurados tienen mayor frecuencia de reclamos? 24. ¿Qué documentos faltan en los casos críticos? 25. ¿Qué casos tienen montos atípicos? 26. ¿Qué siniestros ocurrieron cerca del inicio de la póliza? 27. ¿Qué patrones se repiten en los reclamos sospechosos? 28. Genera un resumen ejecutivo de los casos críticos. 29. Recomienda qué casos debería revisar primero el analista.

13. Score de riesgo sugerido Rango Nivel Acción sugerida 0 - 40

🟢 Verde

Bajo

Continuar flujo normal. 41 - 75 🟡 Amarillo

Medio

Escala a Unidad Antifraude para Revisión documental. 76 - 100 🔴 Rojo

Alto

Escala Unidad Antifraude para Revisión especializada de campo. Los pesos son referenciales. Los equipos pueden proponer otro esquema si explican la lógica, validación y

trazabilidad

del

score.

14. Entregables obligatorios Entregable Descripción Prototipo funcional Aplicación, dashboard, notebook o sistema ejecutable. Código fuente Repositorio GitHub disponible para revisión del jurado. Dataset Sintético o público, con explicación de origen y estructura. README Instrucciones de instalación, ejecución y demo. Arquitectura Diagrama o explicación técnica. Modelo de datos Tablas, campos y relaciones. Explicación del modelo IA Algoritmo, variables, lógica, métricas y limitaciones. Rúbrica de alertas Reglas o criterios usados para generar alertas. Demo funcional Presentación en vivo durante el evento. Presentación ejecutiva Problema, solución, impacto y próximos pasos.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 10

15. Estructura sugerida del repositorio GitHub fraudia-claims/ ├── README.md ├── requirements.txt ├── .env.example ├── data/ │ ├── raw/ │ ├── processed/ │ └── synthetic/ ├── notebooks/ │ ├── 01_exploracion_datos.ipynb │ ├── 02_modelo_fraude.ipynb │ └── 03_evaluacion_modelo.ipynb ├── src/ │ ├── ingestion/load_data.py │ ├── features/build_features.py │ ├── rules/fraud_rules.py │ ├── models/fraud_model.py │ ├── explainability/explain_score.py │ ├── ai_agent/claims_agent.py │ └── app/main.py ├── docs/ │ ├── arquitectura.md │ ├── modelo_datos.md │ ├── reglas_negocio.md │ ├── uso_ia.md │ └── limitaciones.md ├── tests/ │ └── test_rules.py └── presentation/ └── pitch.pdf

16. Requisitos técnicos y estándares Categoría Estándar mínimo Lenguajes Python, R y SQL. Base de datos Oracle, PostgreSQL, MySQL o archivos planos. Repositorio GitHub público o privado con acceso al jurado. Documentación

README, arquitectura, modelo de datos, reglas y uso de IA. Código Modular, comentado, ejecutable y reproducible.

Interfaz Aplicación web, dashboard, notebook o consola funcional con demo clara. Dependencias requirements.txt, renv.lock u otro mecanismo equivalente. Configuración Uso de .env.example; no credenciales reales.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 11

17. Seguridad, privacidad y ética ● No usar datos personales reales. ● No usar información confidencial de aseguradoras. ● Usar datos sintéticos o públicos. ● Anonimizar cualquier identificador. ● No subir credenciales a GitHub. ● No exponer llaves de API. ● Documentar fuentes de datos. ● Aclarar que el resultado es una alerta, no una acusación. ● Mantener revisión humana antes de cualquier decisión. ● Explicar limitaciones del modelo y posibles falsos positivos.

18. Criterios de evaluación Criterio Peso Entendimiento del problema de fraude en seguros 15% Calidad del prototipo funcional 20% Uso efectivo de IA 20% Explicabilidad y trazabilidad del score 15% Calidad técnica del código y arquitectura 10% Seguridad, privacidad y ética 10% Impacto de negocio y escalabilidad 10%

19. Métricas sugeridas Tipo de enfoque Métricas sugeridas Modelo supervisado Precision, recall, F1-score, matriz de confusión y AUCROC. Modelo de anomalías

Porcentaje de casos marcados, ranking de anomalías, score de rareza y validación con reglas. NLP Calidad de extracción, similitud textual, coherencia de resúmenes y explicación de narrativas repetidas.

20. Riesgos y mitigaciones Riesgo Mitigación Confundir alerta con acusación Usar lenguaje de posible fraude o requiere revisión. Sesgo en datos Usar variables explicables y análisis de sesgo. Falsos positivos Mantener revisión humana y explicar factores. Datos sensibles Usar datos sintéticos o públicos. Modelo caja negra Exigir explicación del score y reglas activadas. Sobreajuste Validar con datos separados o explicar la validación. Mal uso legal Declarar limitaciones y alcance no decisorio. Dependencia de APIs externas Documentar dependencias y tener una alternativa de demo.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 12

21. Formato de presentación del día del evento Tiempo Contenido 1 min Problema y oportunidad. 1 min Solución propuesta. 4 min Demo funcional. 2 min Arquitectura y uso de IA. 1 min Impacto de negocio. 1 min Limitaciones y próximos pasos. 5 min Preguntas del jurado.

22. Matriz de evaluación para el hackIAthon 2026 Reto

Aseguradora

del

Sur.

Esta tabla ha sido diseñada para que los equipos participantes comprendan exactamente qué se espera de

su

solución

y

cómo

alcanzar

la

máxima

puntuación

en

cada

dimensión. Dimensión Peso 1 Limitado 2 Básico 3 Funcional 4 Avanzado 5 Excepcional Tecnología y Arquitectura 10% Código desordenado, sin requirements.txt o falla al ejecutar. Scripts aislados sin arquitectura clara; sin uso de. env. Repositorio organizado según el estándar solicitado. Arquitectura robusta, escalable y manejo correcto de excepciones. Código de nivel producción, modular, con documentación técnica profunda. Análisis del Caso y Lógica 15% No identifica señales de riesgo mínimas (fechas/montos). Reglas simples (ej. solo vigencia) sin un score ponderado. Implementa el semáforo de riesgo Verde/Amarillo/Rojo) solicitado. Cruza múltiples variables (asegurado, proveedor, narrativa). Detecta patrones complejos como redes de relación o anomalías no evidentes. Uso de IA y Prototipo 40% Solo utiliza lógica de reglas rígidas IF/ELSE. Implementa un modelo de ML básico sobre datos sintéticos. Prototipo funcional que integra modelos de IA ML o NLP. Uso eficiente de APIs de IA Claude/ChatGPT) para análisis de texto. Enfoque híbrido: ML + NLP + Agente de IA para consultas en lenguaje natural. Explicabilidad y Ética 25% El modelo es una "caja negra"; no explica el porqué del score. Indica qué regla se activó pero de forma técnica o poco clara. Genera una explicación textual simple del motivo de la alerta. El Agente de IA redacta un resumen justificando el nivel de riesgo. Documenta riesgos, sesgos y garantiza que la IA sea solo una alerta.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 13

Pitch, Impacto y Negocio 10% No explica la solución en tiempo o no realiza demo en vivo. Presentación técnica que olvida el impacto de negocio. Estructura clara: Problema, Solución, Demo y Arquitectura. Comunicación fluida con visión clara de impacto operativo. Pitch persuasivo que demuestra valor real y escalabilidad futura.

23. Guía de Preparación para el Pitch 10 minutos)

Para que los equipos se preparen para la presentación, deben considerar que el jurado realizará las siguientes evaluaciones

dinámicas:

1. Cuestionario Crítico Los equipos deben estar listos para responder preguntas como:

●

Técnica: ¿Cómo detectan específicamente la similitud entre dos narrativas de reclamo? ●

Negocio: ¿Cómo ayuda su solución a que un analista humano tome una decisión más rápida? ●

Ética: ¿Qué medidas tomaron para evitar que la IA acuse a un cliente de fraude injustamente? 2. Pruebas de Fuego Live Demo) Durante el pitch, el jurado podrá solicitar: ●

Consulta Agentica: "Pregúntele a su sistema: ¿Qué proveedores concentran el 80% de las alertas rojas? "

●

Prueba de Score: "Cargue este siniestro ocurrido 24 horas después de la póliza y explíquenos el riesgo

asignado".

●

Verificación de Repositorio: "Muestre la estructura de su GitHub para verificar la modularidad del código".

3. Entregables Obligatorios para Calificar

●

Prototipo funcional: Aplicación, Dashboard o notebook ejecutable. ●

Código fuente: Repositorio en GitHub con README.md detallado. ●

Data set: Datos sintéticos o públicos utilizados para la prueba. ●

Presentación Ejecutiva: PDF con el pitch del equipo.

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---

## Pagina 14

ORGANIZA

COORGANIZA

INNOVATION

LEADER

---
