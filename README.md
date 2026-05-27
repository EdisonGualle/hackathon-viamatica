# FRAUDIA CLAIMS
### Detector de Posibles Fraudes en Siniestros — hackIAthon 2026

> **Principio ético:** Este sistema genera **alertas de revisión**, no acusaciones formales de fraude.
> Toda decisión final debe ser tomada por un analista humano especializado.

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-equipo/fraudia-claims.git
cd fraudia-claims

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env y agregar tu GROQ_API_KEY (gratuita en console.groq.com)
```

## Ejecución

```bash
# Paso 1: Generar datos y ejecutar pipeline de IA (solo la primera vez)
python src/ingestion/load_data.py

# Paso 2: Iniciar el dashboard
python src/app/main.py

# Abrir en el navegador: http://localhost:8050
```

## Validacion y Calidad

```bash
# Ejecutar pruebas de reglas criticas
python -m unittest discover -s tests

# Generar metricas del modelo en docs/metricas_modelo.md
python src/models/evaluate_model.py

# API minima de integracion futura
uvicorn src.api.main:app --reload
```

Metricas actuales contra etiqueta simulada:

| Metrica | Valor |
|---------|-------|
| Precision | 0.7029 |
| Recall | 0.9151 |
| F1-score | 0.7951 |
| Accuracy | 0.9000 |
| AUC-ROC | 0.9916 |

## Demo en Vivo

La pestana **Simulador Demo** permite crear un siniestro temporal sin modificar la base principal. El sistema calcula score, nivel, reglas activadas, explicacion y permite descargar un reporte de auditoria.

---

## Arquitectura

```
FRAUDIA CLAIMS
├── Capa de Datos        → SQLite (fraudia.db) con dataset sintético
├── Motor de Reglas      → RF-01..RF-07 + 7 señales de puntuación (sec. 7 del reto)
├── Modelo ML            → Isolation Forest (anomalías) + XGBoost (clasificación)
├── Módulo NLP           → TF-IDF + cosine similarity (narrativas similares)
├── Agente IA            → Groq API / Llama 3.3 70B + Tool Use (costo $0)
└── Dashboard            → Dash + Plotly (Dashboard, Bandeja, Red, Simulador, Chat)
```

Documentacion ampliada:

- `docs/arquitectura.md`
- `docs/modelo_datos.md`
- `docs/reglas_negocio.md`
- `docs/uso_ia.md`
- `docs/limitaciones.md`
- `docs/metricas_modelo.md`
- `presentation/demo_script.md`

## Objetivos Específicos del Reto

1. Cargar y procesar información sintética o pública de siniestros.
2. Identificar patrones atípicos en reclamos mediante reglas, ML y NLP.
3. Calcular un score de riesgo por siniestro con trazabilidad por componente.
4. Clasificar casos en niveles de riesgo: VERDE, AMARILLO y ROJO.
5. Generar alertas explicables para el analista antifraude.
6. Permitir consultas en lenguaje natural sobre los casos detectados, con respaldo local si la API de IA alcanza límite de cuota.
7. Presentar un dashboard funcional para KPIs, bandeja de casos, red de relaciones y Copilot.
8. Documentar el modelo, reglas, datos, limitaciones y principio ético.
9. Entregar código fuente ejecutable y reproducible.
10. Proponer una arquitectura escalable para una implementación futura.

## Cobertura Funcional

| Objetivo | Implementación en FRAUDIA CLAIMS |
|----------|----------------------------------|
| Datos | Dataset sintético de 1,000 siniestros y base SQLite portable. |
| Patrones atípicos | Reglas RF-01 a RF-07, señales S01-S07, anomalías y similitud textual. |
| Score | Score final 0-100 con desglose reglas, ML y NLP. |
| Clasificación | Niveles VERDE, AMARILLO y ROJO para priorización operativa. |
| Explicabilidad | Reglas activadas, descripción de alertas y recomendación de acción. |
| Lenguaje natural | Copilot con Groq y modo local SQL ante rate limit o falta de API key. |
| Dashboard | KPIs, gráficos, bandeja, detalle de caso, red y agente IA. |
| Documentación | README, reglas, flujo de ejecución y limitaciones éticas. |
| Reproducibilidad | Scripts de generación, carga y ejecución local. |
| Escalabilidad futura | Separación por capas: datos, reglas, modelos, NLP, agente y UI. |

## Score de Riesgo Final

| Componente    | Peso | Descripción |
|---------------|------|-------------|
| Motor Reglas  | 50%  | Puntos por señales de fraude (máx 100) |
| Modelo ML     | 35%  | Isolation Forest + XGBoost combinados |
| NLP Similitud | 15%  | Similitud textual entre narrativas |

| Rango     | Nivel   | Acción |
|-----------|---------|--------|
| 0 – 40    | 🟢 VERDE   | Flujo normal |
| 41 – 75   | 🟡 AMARILLO | Revisión documental — Unidad Antifraude |
| 76 – 100  | 🔴 ROJO    | Revisión especializada de campo |

## Dataset Sintético

- **1,000 siniestros** con ~20% de fraudes simulados
- **Tablas:** siniestros, pólizas, asegurados, vehículos, proveedores, documentos
- Patrones de fraude embebidos: borde de vigencia, reporte tardío, documentos inconsistentes, narrativas clonadas, proveedores en lista restrictiva, montos atípicos

## Tecnologías

- **Python 3.11+**, Dash, Plotly, pandas, scikit-learn, XGBoost
- **Groq API** (Llama 3.3 70B) — gratuita, sin costo
- **SQLite** — sin servidor, portátil
- **Dash Cytoscape** — red de relaciones asegurado-proveedor-siniestro

## Equipo

hackIAthon 2026 — Reto Aseguradora del Sur
