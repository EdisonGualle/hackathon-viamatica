# Uso de Inteligencia Artificial

## Enfoque Hibrido

FRAUDIA combina:

- Reglas de negocio explicables.
- Isolation Forest para anomalias.
- Clasificador supervisado con etiqueta simulada.
- NLP con TF-IDF y similitud coseno para narrativas repetidas.
- Agente IA para consultas en lenguaje natural.

## Agente IA

El agente usa Groq cuando hay cuota disponible. Si la API llega a limite o no existe llave, activa modo local con consultas SQL deterministicas para responder preguntas criticas del jurado.

Preguntas cubiertas:

- Top 10 siniestros de mayor riesgo.
- Proveedores con mayor concentracion de alertas.
- Ramos y ciudades con mayor riesgo.
- Asegurados con mayor frecuencia.
- Documentos faltantes.
- Montos atipicos.
- Siniestros cerca del inicio de poliza.
- Resumen ejecutivo.

## Simulador Demo

El simulador evalua un siniestro temporal sin modificar la base principal. Calcula reglas, score, nivel, explicacion y reporte descargable.
