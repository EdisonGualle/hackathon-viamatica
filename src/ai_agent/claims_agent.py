"""
Agente IA con Groq API (Llama 3.3 70B) + Tool Use.
Responde preguntas en lenguaje natural sobre los siniestros cargados en la BD.
Costo: $0 (free tier Groq — 14,400 requests/día).
"""
import json
import os
import sqlite3
import unicodedata

import pandas as pd
from groq import Groq

DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "fraudia.db")
)

# ──────────────────────────────────────────────
# FUNCIONES DE CONSULTA (herramientas del agente)
# ──────────────────────────────────────────────

def _conn():
    return sqlite3.connect(DB_PATH)


def get_top_risk_claims(n: int = 10) -> str:
    """Retorna los N siniestros con mayor score de riesgo final."""
    conn = _conn()
    query = """
        SELECT s.id_siniestro, s.ramo, s.cobertura, s.id_asegurado,
               s.monto_reclamado, s.fecha_ocurrencia,
               sr.score_final, sr.nivel, sr.explicacion
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        ORDER BY sr.score_final DESC
        LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(n,))
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_claim_detail(id_siniestro: str) -> str:
    """Retorna el detalle completo de un siniestro incluyendo score y reglas activadas."""
    conn = _conn()
    sin = pd.read_sql(
        "SELECT * FROM siniestros WHERE id_siniestro = ?", conn, params=(id_siniestro,)
    )
    score = pd.read_sql(
        "SELECT * FROM scores_riesgo WHERE id_siniestro = ?", conn, params=(id_siniestro,)
    )
    docs = pd.read_sql(
        "SELECT * FROM documentos WHERE id_siniestro = ?", conn, params=(id_siniestro,)
    )
    conn.close()
    result = {
        "siniestro": sin.to_dict("records"),
        "score": score.to_dict("records"),
        "documentos": docs.to_dict("records"),
    }
    return json.dumps(result, ensure_ascii=False, default=str)


def get_provider_ranking(top_n: int = 10) -> str:
    """Ranking de proveedores con mayor concentración de alertas rojas."""
    conn = _conn()
    query = """
        SELECT s.id_proveedor, p.nombre, p.tipo, p.ciudad,
               p.en_lista_restrictiva,
               COUNT(*) as total_siniestros,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) as alertas_rojas,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) as alertas_amarillas,
               ROUND(AVG(sr.score_final), 1) as score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        LEFT JOIN proveedores p ON s.id_proveedor = p.id_proveedor
        GROUP BY s.id_proveedor
        ORDER BY alertas_rojas DESC, score_promedio DESC
        LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(top_n,))
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_suspicious_by_city() -> str:
    """Concentración de alertas por ciudad."""
    conn = _conn()
    query = """
        SELECT s.sucursal as ciudad,
               COUNT(*) as total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) as rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) as amarillos,
               ROUND(AVG(sr.score_final), 1) as score_promedio
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        GROUP BY s.sucursal
        ORDER BY rojos DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_suspicious_by_ramo() -> str:
    """Porcentaje de casos sospechosos por ramo."""
    conn = _conn()
    query = """
        SELECT s.ramo,
               COUNT(*) as total,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) as rojos,
               SUM(CASE WHEN sr.nivel = 'AMARILLO' THEN 1 ELSE 0 END) as amarillos,
               ROUND(100.0 * SUM(CASE WHEN sr.nivel != 'VERDE' THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_sospechosos
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        GROUP BY s.ramo
        ORDER BY pct_sospechosos DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_high_frequency_insureds(top_n: int = 10) -> str:
    """Asegurados con mayor frecuencia de reclamos."""
    conn = _conn()
    query = """
        SELECT s.id_asegurado,
               COUNT(*) as total_siniestros,
               ROUND(AVG(sr.score_final), 1) as score_promedio,
               SUM(CASE WHEN sr.nivel = 'ROJO' THEN 1 ELSE 0 END) as alertas_rojas,
               SUM(s.monto_reclamado) as monto_total_reclamado
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        GROUP BY s.id_asegurado
        HAVING total_siniestros >= 2
        ORDER BY total_siniestros DESC, score_promedio DESC
        LIMIT ?
    """
    df = pd.read_sql(query, conn, params=(top_n,))
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_missing_documents_critical() -> str:
    """Documentos faltantes en casos críticos (ROJO)."""
    conn = _conn()
    query = """
        SELECT d.tipo_documento,
               COUNT(*) as casos_faltantes
        FROM documentos d
        JOIN scores_riesgo sr ON d.id_siniestro = sr.id_siniestro
        WHERE d.entregado = 0 AND sr.nivel = 'ROJO'
        GROUP BY d.tipo_documento
        ORDER BY casos_faltantes DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_atypical_amounts() -> str:
    """Siniestros con montos atípicos (reclamado > 90% suma asegurada)."""
    conn = _conn()
    query = """
        SELECT s.id_siniestro, s.ramo, s.id_asegurado,
               s.monto_reclamado, p.suma_asegurada,
               ROUND(100.0 * s.monto_reclamado / p.suma_asegurada, 1) as pct_suma,
               sr.score_final, sr.nivel
        FROM siniestros s
        JOIN polizas p ON s.id_poliza = p.id_poliza
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        WHERE p.suma_asegurada > 0
          AND (s.monto_reclamado / p.suma_asegurada) > 0.9
        ORDER BY pct_suma DESC
        LIMIT 20
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def get_near_policy_border() -> str:
    """Siniestros ocurridos cerca del inicio o fin de póliza."""
    conn = _conn()
    query = """
        SELECT s.id_siniestro, s.ramo, s.id_asegurado,
               s.dias_inicio_poliza, s.dias_fin_poliza,
               s.fecha_ocurrencia, sr.score_final, sr.nivel
        FROM siniestros s
        JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
        WHERE s.dias_inicio_poliza <= 30 OR s.dias_fin_poliza <= 30
        ORDER BY MIN(s.dias_inicio_poliza, s.dias_fin_poliza) ASC
        LIMIT 20
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_json(orient="records", force_ascii=False)


def generate_executive_summary() -> str:
    """Genera un resumen ejecutivo con las estadísticas principales del portafolio."""
    conn = _conn()
    totales = pd.read_sql("""
        SELECT
            COUNT(*) as total_siniestros,
            SUM(CASE WHEN nivel = 'ROJO' THEN 1 ELSE 0 END) as casos_rojos,
            SUM(CASE WHEN nivel = 'AMARILLO' THEN 1 ELSE 0 END) as casos_amarillos,
            SUM(CASE WHEN nivel = 'VERDE' THEN 1 ELSE 0 END) as casos_verdes,
            ROUND(AVG(score_final), 1) as score_promedio,
            ROUND(100.0 * SUM(CASE WHEN nivel != 'VERDE' THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_sospechosos
        FROM scores_riesgo
    """, conn)
    montos = pd.read_sql("""
        SELECT
            ROUND(SUM(s.monto_reclamado), 2) as monto_total_reclamado,
            ROUND(SUM(CASE WHEN sr.nivel = 'ROJO' THEN s.monto_reclamado ELSE 0 END), 2) as monto_en_riesgo
        FROM siniestros s JOIN scores_riesgo sr ON s.id_siniestro = sr.id_siniestro
    """, conn)
    conn.close()
    summary = {**totales.to_dict("records")[0], **montos.to_dict("records")[0]}
    return json.dumps(summary, ensure_ascii=False, default=str)


# ──────────────────────────────────────────────
# DEFINICIÓN DE HERRAMIENTAS PARA GROQ
# ──────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_top_risk_claims",
            "description": "Obtiene los N siniestros con mayor score de riesgo de fraude.",
            "parameters": {
                "type": "object",
                "properties": {"n": {"type": "integer", "description": "Número de siniestros a retornar (default 10)"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_claim_detail",
            "description": "Obtiene el detalle completo de un siniestro específico, incluyendo su score, reglas activadas y documentos.",
            "parameters": {
                "type": "object",
                "properties": {"id_siniestro": {"type": "string", "description": "ID del siniestro"}},
                "required": ["id_siniestro"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_provider_ranking",
            "description": "Ranking de proveedores con mayor concentración de alertas de fraude.",
            "parameters": {
                "type": "object",
                "properties": {"top_n": {"type": "integer", "description": "Número de proveedores (default 10)"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_suspicious_by_city",
            "description": "Concentración de alertas de fraude por ciudad.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_suspicious_by_ramo",
            "description": "Porcentaje de casos sospechosos por ramo de seguro.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_high_frequency_insureds",
            "description": "Asegurados con mayor frecuencia de reclamos.",
            "parameters": {
                "type": "object",
                "properties": {"top_n": {"type": "integer"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_missing_documents_critical",
            "description": "Tipos de documentos faltantes en los casos críticos (nivel ROJO).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_atypical_amounts",
            "description": "Siniestros con montos reclamados atípicamente altos respecto a la suma asegurada.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_near_policy_border",
            "description": "Siniestros ocurridos cerca del inicio o fin de la póliza.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_executive_summary",
            "description": "Genera un resumen ejecutivo completo del portafolio de siniestros y alertas.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

TOOL_FUNCTIONS = {
    "get_top_risk_claims": get_top_risk_claims,
    "get_claim_detail": get_claim_detail,
    "get_provider_ranking": get_provider_ranking,
    "get_suspicious_by_city": get_suspicious_by_city,
    "get_suspicious_by_ramo": get_suspicious_by_ramo,
    "get_high_frequency_insureds": get_high_frequency_insureds,
    "get_missing_documents_critical": get_missing_documents_critical,
    "get_atypical_amounts": get_atypical_amounts,
    "get_near_policy_border": get_near_policy_border,
    "generate_executive_summary": generate_executive_summary,
}


def _rows(payload: str) -> list[dict]:
    return json.loads(payload or "[]")


def _money(value) -> str:
    return f"${float(value or 0):,.0f}"


def _plain(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(c for c in normalized if not unicodedata.combining(c)).lower()


def _format_table(rows: list[dict], columns: list[tuple[str, str]], limit: int = 10) -> str:
    lines = []
    for i, row in enumerate(rows[:limit], 1):
        parts = []
        for key, label in columns:
            value = row.get(key, "N/D")
            if "monto" in key:
                value = _money(value)
            parts.append(f"{label}: {value}")
        lines.append(f"{i}. " + " | ".join(parts))
    return "\n".join(lines) if lines else "No se encontraron registros para esta consulta."


def answer_with_local_tools(user_message: str) -> str:
    """Respuesta deterministica con SQLite cuando Groq no esta disponible."""
    q = _plain(user_message)

    if "asegurado" in q and ("frecuencia" in q or "reclamo" in q):
        data = _rows(get_high_frequency_insureds(10))
        body = _format_table(data, [
            ("id_asegurado", "Asegurado"),
            ("total_siniestros", "Siniestros"),
            ("alertas_rojas", "Rojas"),
            ("score_promedio", "Score prom."),
            ("monto_total_reclamado", "Monto total"),
        ])
        return (
            "Modo local activado: Groq no es necesario para esta consulta.\n\n"
            "Asegurados con mayor frecuencia de reclamos:\n"
            f"{body}\n\n"
            "Lectura antifraude: prioriza los asegurados con mayor volumen, score promedio alto "
            "y alertas rojas, porque combinan recurrencia operativa con severidad de riesgo."
        )

    if "proveedor" in q and ("80" in q or "roja" in q or "concentra" in q):
        data = _rows(get_provider_ranking(20))
        total_rojas = sum(int(r.get("alertas_rojas") or 0) for r in data)
        acumulado = 0
        corte_80 = 0
        for row in data:
            if total_rojas <= 0:
                break
            acumulado += int(row.get("alertas_rojas") or 0)
            corte_80 += 1
            if acumulado / total_rojas >= 0.8:
                break
        body = _format_table(data, [
            ("id_proveedor", "Proveedor"),
            ("nombre", "Nombre"),
            ("tipo", "Tipo"),
            ("alertas_rojas", "Rojas"),
            ("score_promedio", "Score prom."),
        ])
        return (
            "Modo local activado: respuesta generada desde la base SQLite.\n\n"
            f"{corte_80} proveedores concentran aproximadamente el 80% de {total_rojas} alertas rojas.\n\n"
            f"Ranking principal:\n{body}\n\n"
            "Accion recomendada: revisar primero proveedores con lista restrictiva, alto score promedio "
            "y concentracion de casos rojos."
        )

    if "riesgo" in q and ("top" in q or "mayor" in q or "10" in q):
        data = _rows(get_top_risk_claims(10))
        body = _format_table(data, [
            ("id_siniestro", "Siniestro"),
            ("ramo", "Ramo"),
            ("nivel", "Nivel"),
            ("score_final", "Score"),
            ("monto_reclamado", "Monto"),
        ])
        return f"Top 10 siniestros con mayor riesgo:\n{body}"

    if "ramo" in q:
        data = _rows(get_suspicious_by_ramo())
        body = _format_table(data, [
            ("ramo", "Ramo"),
            ("total", "Total"),
            ("rojos", "Rojos"),
            ("amarillos", "Amarillos"),
            ("pct_sospechosos", "% sospechosos"),
        ])
        return f"Ramos con mayor concentracion de casos sospechosos:\n{body}"

    if "ciudad" in q or "sucursal" in q:
        data = _rows(get_suspicious_by_city())
        body = _format_table(data, [
            ("ciudad", "Ciudad"),
            ("total", "Total"),
            ("rojos", "Rojos"),
            ("amarillos", "Amarillos"),
            ("score_promedio", "Score prom."),
        ])
        return f"Concentracion de alertas por ciudad:\n{body}"

    if "document" in q:
        data = _rows(get_missing_documents_critical())
        body = _format_table(data, [
            ("tipo_documento", "Documento"),
            ("casos_faltantes", "Casos faltantes"),
        ])
        return f"Documentos faltantes en casos criticos ROJO:\n{body}"

    if "monto" in q or "atipic" in q:
        data = _rows(get_atypical_amounts())
        body = _format_table(data, [
            ("id_siniestro", "Siniestro"),
            ("ramo", "Ramo"),
            ("nivel", "Nivel"),
            ("pct_suma", "% suma asegurada"),
            ("monto_reclamado", "Monto"),
        ])
        return f"Casos con montos atipicos:\n{body}"

    if "poliza" in q or "vigencia" in q or "inicio" in q:
        data = _rows(get_near_policy_border())
        body = _format_table(data, [
            ("id_siniestro", "Siniestro"),
            ("ramo", "Ramo"),
            ("dias_inicio_poliza", "Dias inicio"),
            ("dias_fin_poliza", "Dias fin"),
            ("nivel", "Nivel"),
            ("score_final", "Score"),
        ])
        return f"Siniestros cercanos al inicio o fin de poliza:\n{body}"

    if "resumen" in q or "ejecutivo" in q or "objetivo" in q:
        data = json.loads(generate_executive_summary())
        return (
            "Resumen ejecutivo FRAUDIA CLAIMS:\n"
            f"- Siniestros procesados: {data['total_siniestros']}\n"
            f"- Casos ROJO: {data['casos_rojos']}\n"
            f"- Casos AMARILLO: {data['casos_amarillos']}\n"
            f"- Casos VERDE: {data['casos_verdes']}\n"
            f"- Score promedio: {data['score_promedio']}/100\n"
            f"- Monto total reclamado: {_money(data['monto_total_reclamado'])}\n"
            f"- Monto en riesgo ROJO: {_money(data['monto_en_riesgo'])}\n\n"
            "Cobertura de objetivos: carga de datos, deteccion de patrones atipicos, score, "
            "clasificacion verde/amarillo/rojo, alertas explicables, consultas en lenguaje natural, "
            "dashboard funcional, documentacion y arquitectura futura."
        )

    return (
        "Modo local activado. Puedo responder sin Groq sobre: top de riesgo, proveedores, "
        "asegurados frecuentes, ramos, ciudades, documentos faltantes, montos atipicos, "
        "vigencia de poliza y resumen ejecutivo."
    )

SYSTEM_PROMPT = """Eres FRAUDIA Copilot, el asistente de inteligencia artificial de la plataforma FRAUDIA CLAIMS, desarrollada para la Aseguradora del Sur en el hackIAthon 2026.

Tu misión: apoyar a los analistas de la Unidad Antifraude con análisis de alto valor, trazabilidad total y recomendaciones accionables sobre siniestros sospechosos.

IDENTIDAD Y TONO:
- Eres un experto en detección de fraude en seguros con 15 años de experiencia simulada.
- Tu tono es ejecutivo, tecnológico y premium corporativo. Directo, sin rodeos.
- Nunca digas "fraude confirmado". Siempre usa: "posible fraude", "requiere revisión especializada", "señales de alerta identificadas".
- Responde SIEMPRE en español profesional.

METODOLOGÍA DE SCORING (explícala cuando sea relevante):
- Score Final = 45% Reglas de Negocio + 40% Machine Learning + 15% Similitud NLP
- Niveles: ROJO ≥ 70 pts (revisión de campo urgente) | AMARILLO 35-69 pts (revisión documental) | VERDE < 35 pts (flujo normal)
- Reglas críticas que fuerzan ROJO automático: RF-01 (PTxRB), RF-02 (Falsificación Documental), RF-03 (Lista Restrictiva)

REGLAS DE NEGOCIO DISPONIBLES:
- RF-01: Cobertura Pérdida Total por Robo en Vehículos → ROJO automático
- RF-02: Falsificación o Adulteración Documental → ROJO automático
- RF-03: Proveedor/Asegurado en Lista Restrictiva → ROJO automático
- RF-04: Dinámica del Accidente Sospechosa → AMARILLO
- RF-05: Siniestro al Borde de Vigencia <48h → AMARILLO
- RF-06: Demora Atípica en Denuncia de Robo >4 días → AMARILLO
- RF-07: Narrativa Idéntica (posible clonación) → AMARILLO
- S01-S07: Señales adicionales de puntuación (borde vigencia, reporte tardío, alta frecuencia, documentos incompletos, monto atípico, proveedor recurrente)

FORMATO DE RESPUESTA OBLIGATORIO para análisis de casos individuales:
🔴/🟡/🟢 **[NIVEL] — Score [X]/100 | Confianza IA: [Y]%**

**Señales detectadas:**
• [RF-XX] [Descripción de la regla activada]
• [RF-XX] [Descripción de la regla activada]

**Análisis del analista:**
[2-3 oraciones explicando el patrón detectado como lo haría un analista senior]

**Línea de tiempo del caso:**
• [Fecha evento] → [Fecha reporte] → [Días de demora]

**Recomendación:**
[Acción concreta: inspección de campo / revisión documental / cruce de bases de datos]

**Nota ética:** Este análisis es una alerta de revisión generada por IA. La decisión final corresponde exclusivamente al analista humano certificado.

INSTRUCCIONES OPERATIVAS:
- Siempre llama a las herramientas disponibles antes de responder sobre datos específicos.
- Si el usuario pide un resumen ejecutivo, usa generate_executive_summary() y presenta los datos con contexto de negocio.
- Para rankings de proveedores, destaca si alguno está en lista restrictiva.
- Si el usuario menciona un ID de siniestro, usa get_claim_detail() primero.
- Calcula la confianza IA como: min(97, score_final * 0.8 + num_reglas_activas * 3)%"""


class FraudiaAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.history: list[dict] = []

    def chat(self, user_message: str) -> str:
        if self.client is None:
            return answer_with_local_tools(user_message)

        self.history.append({"role": "user", "content": user_message})
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history

        # Primera llamada: el agente decide qué herramienta usar
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=900,
            temperature=0.1,
        )

        msg = response.choices[0].message

        # Ejecutar herramientas si las hay
        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments or "{}") or {}
                fn = TOOL_FUNCTIONS.get(fn_name)
                if fn:
                    result = fn(**fn_args)
                else:
                    result = json.dumps({"error": f"Herramienta {fn_name} no encontrada."})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Segunda llamada: el agente redacta la respuesta con los datos
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=900,
                temperature=0.2,
            )
            answer = final_response.choices[0].message.content
        else:
            answer = msg.content

        self.history.append({"role": "assistant", "content": answer})
        return answer

    def reset(self):
        self.history = []


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = FraudiaAgent()
    print("Agente FRAUDIA listo. Escribe tu pregunta (o 'salir'):")
    while True:
        q = input("\nTú: ").strip()
        if q.lower() == "salir":
            break
        resp = agent.chat(q)
        print(f"\nFRAUDIA: {resp}")
