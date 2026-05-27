"""
Generador de dataset sintético de siniestros con patrones de fraude embebidos.
Produce ~1000 siniestros con señales reales de fraude según el documento del reto.
"""
import random
import sqlite3
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "..", "fraudia.db")

CIUDADES = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Loja", "Portoviejo", "Riobamba"]
RAMOS = ["Vehiculos", "Salud", "Vida", "Hogar", "Generales"]
COBERTURAS = {
    "Vehiculos": ["Choque", "Robo", "Responsabilidad Civil", "Perdida Total"],
    "Salud": ["Atencion Medica", "Hospitalizacion", "Cirugia"],
    "Vida": ["Fallecimiento", "Invalidez"],
    "Hogar": ["Incendio", "Robo", "Inundacion"],
    "Generales": ["Dano", "Robo", "Responsabilidad Civil"],
}
ESTADOS = ["Reserva", "Pago Total", "Pago Parcial", "Anticipo", "Negativa", "Cierre Sin Consecuencia", "Liquidado"]
TIPOS_PROVEEDOR = ["Taller", "Clinica", "Perito", "Hospital", "Laboratorio"]
TIPOS_DOCUMENTO = ["Denuncia", "Factura", "Informe Pericial", "Foto Evidencia", "Certificado Medico"]
CANALES_VENTA = ["Agente", "Digital", "Corredor", "Directo"]
MARCAS = ["Toyota", "Chevrolet", "Hyundai", "Kia", "Nissan", "Ford", "Volkswagen"]
NARRATIVAS_NORMALES = [
    "El vehiculo fue impactado por detras mientras estaba detenido en semaforo.",
    "Se produjo choque lateral al cambiar de carril en autopista.",
    "El asegurado reporta robo del vehiculo en parqueadero publico.",
    "Accidente de transito en interseccion con semaforo en rojo.",
    "El vehiculo colisiono con un poste al perder el control.",
    "Choque frontal de baja velocidad en zona urbana.",
    "Se reporta incendio en el motor del vehiculo.",
    "El vehiculo fue danado por granizo durante tormenta.",
    "Colision con animal en carretera en horas de la madrugada.",
    "El asegurado sufrio resbalada y golpe contra otro vehiculo en estacionamiento.",
    "Accidente en rotonda por no ceder el paso.",
    "Colision multiple en carretera por neblina.",
    "El vehiculo fue rayado en el estacionamiento del supermercado.",
    "Se produjo volcamiento al tomar curva a alta velocidad.",
    "Choque con vehiculo que se paso la luz roja.",
]
NARRATIVAS_SOSPECHOSAS = [
    "El vehiculo fue impactado por un tercero que se dio a la fuga sin dejar datos.",
    "Accidente ocurrido en via solitaria de madrugada sin testigos ni camaras.",
    "El vehiculo colisiono frontalmente en circunstancias poco claras.",
    "Se produjo volcamiento en via recta sin causa aparente identificada.",
    "El asegurado indica que el tercero huyo antes de que llegara la policia.",
    "Accidente multiple en interseccion de madrugada, ninguno de los involucrados tiene seguro.",
    "El vehiculo presento danos severos sin rastro del tercero ni registro de camaras.",
    "Colision posterior en via solitaria, el tercero abandono el lugar sin identificarse.",
]


# ──────────────────────────────────────────────
# 1. ASEGURADOS
# ──────────────────────────────────────────────
def generate_asegurados(n=200):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "id_asegurado": f"ASE-{i:04d}",
            "segmento": random.choice(["Individual", "Empresa", "VIP"]),
            "antiguedad_anos": random.randint(1, 20),
            "ciudad": random.choice(CIUDADES),
            "num_polizas": random.randint(1, 4),
            "reclamos_12m": random.choices([0, 1, 2, 3, 4], weights=[50, 25, 15, 7, 3])[0],
            "mora_actual": random.choices([0, 1], weights=[85, 15])[0],
            "score_cliente": round(random.uniform(300, 900), 1),
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 2. PROVEEDORES
# ──────────────────────────────────────────────
def generate_proveedores(n=40):
    rows = []
    # 3 proveedores en lista restrictiva
    for i in range(1, n + 1):
        en_lista = 1 if i <= 3 else 0
        pct_obs = round(random.uniform(0.3, 0.9), 2) if en_lista else round(random.uniform(0.0, 0.2), 2)
        rows.append({
            "id_proveedor": f"PRV-{i:03d}",
            "nombre": f"Proveedor {i} {random.choice(TIPOS_PROVEEDOR)}",
            "tipo": random.choice(TIPOS_PROVEEDOR),
            "ciudad": random.choice(CIUDADES),
            "reclamos_asociados": random.randint(5, 120),
            "monto_promedio": round(random.uniform(500, 8000), 2),
            "pct_casos_observados": pct_obs,
            "en_lista_restrictiva": en_lista,
            "antiguedad_anos": random.randint(1, 15),
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 3. PÓLIZAS
# ──────────────────────────────────────────────
def generate_polizas(asegurados_df, n=300):
    rows = []
    ids_asegurados = asegurados_df["id_asegurado"].tolist()
    for i in range(1, n + 1):
        inicio = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900))
        fin = inicio + timedelta(days=365)
        ramo = random.choice(RAMOS)
        rows.append({
            "id_poliza": f"POL-{i:05d}",
            "id_asegurado": random.choice(ids_asegurados),
            "ramo": ramo,
            "fecha_inicio": inicio.strftime("%Y-%m-%d"),
            "fecha_fin": fin.strftime("%Y-%m-%d"),
            "prima": round(random.uniform(200, 3000), 2),
            "suma_asegurada": round(random.uniform(5000, 80000), 2),
            "deducible": round(random.uniform(100, 1000), 2),
            "canal_venta": random.choice(CANALES_VENTA),
            "ciudad": random.choice(CIUDADES),
            "estado_poliza": random.choices(["Activa", "Vencida", "Cancelada"], weights=[70, 20, 10])[0],
        })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 4. VEHÍCULOS
# ──────────────────────────────────────────────
def generate_vehiculos(asegurados_df):
    rows = []
    for _, ase in asegurados_df.iterrows():
        num_vehi = random.choices([1, 2], weights=[80, 20])[0]
        for j in range(num_vehi):
            rows.append({
                "id_vehiculo": f"VEH-{ase['id_asegurado']}-{j+1}",
                "id_asegurado": ase["id_asegurado"],
                "placa": f"{random.choice('ABCDEFGHIJKLMNOP')}{random.choice('ABCDEFGHIJKLMNOP')}{random.choice('ABCDEFGHIJKLMNOP')}-{random.randint(100,999)}",
                "chasis": f"CH{random.randint(100000, 999999)}",
                "motor": f"MT{random.randint(100000, 999999)}",
                "marca": random.choice(MARCAS),
                "modelo": f"Modelo-{random.randint(1, 10)}",
                "anio": random.randint(2010, 2024),
                "siniestros_18m": random.choices([0, 1, 2, 3, 4], weights=[55, 25, 12, 5, 3])[0],
            })
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 5. SINIESTROS (núcleo con fraudes embebidos)
# ──────────────────────────────────────────────
def generate_siniestros(polizas_df, asegurados_df, proveedores_df, n=1000):
    rows = []
    polizas = polizas_df.to_dict("records")
    proveedores_lista_rest = proveedores_df[proveedores_df["en_lista_restrictiva"] == 1]["id_proveedor"].tolist()
    proveedores_all = proveedores_df["id_proveedor"].tolist()

    # Asegurados con alta frecuencia (fraude simulado)
    asegurados_alta_frec = asegurados_df[asegurados_df["reclamos_12m"] >= 3]["id_asegurado"].tolist()

    for i in range(1, n + 1):
        poliza = random.choice(polizas)
        fecha_inicio_poliza = datetime.strptime(poliza["fecha_inicio"], "%Y-%m-%d")
        fecha_fin_poliza = datetime.strptime(poliza["fecha_fin"], "%Y-%m-%d")
        ramo = poliza["ramo"]
        coberturas_ramo = COBERTURAS.get(ramo, ["Dano"])
        cobertura = random.choice(coberturas_ramo)

        # Decidir si es caso sospechoso (~20%)
        es_fraude = random.random() < 0.20

        if es_fraude:
            # Señales de fraude embebidas
            tipo_fraude = random.choice([
                "borde_vigencia_inicio", "borde_vigencia_fin",
                "reporte_tardio", "proveedor_restrictivo",
                "monto_alto", "documentos_incompletos",
                "narrativa_sospechosa", "alta_frecuencia"
            ])

            if tipo_fraude == "borde_vigencia_inicio":
                dias_desde_inicio = random.randint(1, 10)
                fecha_ocurrencia = fecha_inicio_poliza + timedelta(days=dias_desde_inicio)
            elif tipo_fraude == "borde_vigencia_fin":
                dias_antes_fin = random.randint(1, 10)
                fecha_ocurrencia = fecha_fin_poliza - timedelta(days=dias_antes_fin)
            else:
                fecha_ocurrencia = fecha_inicio_poliza + timedelta(days=random.randint(30, 300))

            dias_reporte = random.randint(8, 30) if tipo_fraude == "reporte_tardio" else random.randint(1, 3)
            fecha_reporte = fecha_ocurrencia + timedelta(days=dias_reporte)

            proveedor = random.choice(proveedores_lista_rest) if tipo_fraude == "proveedor_restrictivo" else random.choice(proveedores_all)
            monto_rec = round(poliza["suma_asegurada"] * random.uniform(0.85, 1.0), 2) if tipo_fraude == "monto_alto" else round(random.uniform(500, 8000), 2)
            docs_completos = 0 if tipo_fraude == "documentos_incompletos" else random.choices([0, 1], weights=[20, 80])[0]
            descripcion = random.choice(NARRATIVAS_SOSPECHOSAS)
            etiqueta = 1
        else:
            fecha_ocurrencia = fecha_inicio_poliza + timedelta(days=random.randint(30, 330))
            dias_reporte = random.choices([1, 2, 3, 4, 7], weights=[40, 25, 20, 10, 5])[0]
            fecha_reporte = fecha_ocurrencia + timedelta(days=dias_reporte)
            proveedor = random.choice(proveedores_all)
            suma = poliza["suma_asegurada"]
            monto_rec = round(random.uniform(500, suma * 0.6), 2)
            docs_completos = random.choices([0, 1], weights=[10, 90])[0]
            descripcion = random.choice(NARRATIVAS_NORMALES)
            etiqueta = 0

        monto_estimado = round(monto_rec * random.uniform(0.7, 1.1), 2)
        monto_pagado = round(monto_estimado * random.uniform(0.0, 1.0), 2) if random.random() > 0.3 else 0.0

        dias_inicio = (fecha_ocurrencia - fecha_inicio_poliza).days
        dias_fin = (fecha_fin_poliza - fecha_ocurrencia).days
        dias_reporte_calc = (fecha_reporte - fecha_ocurrencia).days

        # Historial del asegurado
        hist = asegurados_df[asegurados_df["id_asegurado"] == poliza["id_asegurado"]]["reclamos_12m"]
        historial = int(hist.values[0]) if len(hist) > 0 else 0

        rows.append({
            "id_siniestro": f"SIN-{i:05d}",
            "id_poliza": poliza["id_poliza"],
            "id_asegurado": poliza["id_asegurado"],
            "id_proveedor": proveedor,
            "ramo": ramo,
            "cobertura": cobertura,
            "fecha_ocurrencia": fecha_ocurrencia.strftime("%Y-%m-%d"),
            "fecha_reporte": fecha_reporte.strftime("%Y-%m-%d"),
            "monto_reclamado": monto_rec,
            "monto_estimado": monto_estimado,
            "monto_pagado": monto_pagado,
            "estado": random.choice(ESTADOS),
            "sucursal": random.choice(CIUDADES),
            "descripcion": descripcion,
            "documentos_completos": docs_completos,
            "beneficiario": random.choice(["Taller", "Clinica", "Perito", "Directo"]),
            "dias_inicio_poliza": max(0, dias_inicio),
            "dias_fin_poliza": max(0, dias_fin),
            "dias_ocurr_reporte": max(0, dias_reporte_calc),
            "historial_siniestros": historial,
            "etiqueta_fraude": etiqueta,
        })

    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 6. DOCUMENTOS
# ──────────────────────────────────────────────
def generate_documentos(siniestros_df):
    rows = []
    doc_id = 1
    for _, sin in siniestros_df.iterrows():
        num_docs = random.randint(2, 5)
        tipos = random.sample(TIPOS_DOCUMENTO, min(num_docs, len(TIPOS_DOCUMENTO)))
        for tipo in tipos:
            inconsistencia = 1 if (sin["etiqueta_fraude"] == 1 and random.random() < 0.4) else 0
            fecha_emision = datetime.strptime(sin["fecha_ocurrencia"], "%Y-%m-%d") - timedelta(days=random.randint(-5, 10))
            # Fraude: fecha factura anterior al evento
            if inconsistencia:
                fecha_emision = datetime.strptime(sin["fecha_ocurrencia"], "%Y-%m-%d") - timedelta(days=random.randint(5, 30))
            rows.append({
                "id_documento": f"DOC-{doc_id:06d}",
                "id_siniestro": sin["id_siniestro"],
                "tipo_documento": tipo,
                "entregado": sin["documentos_completos"],
                "legible": random.choices([0, 1], weights=[15, 85])[0],
                "fecha_emision": fecha_emision.strftime("%Y-%m-%d"),
                "inconsistencia_detectada": inconsistencia,
                "observacion": "Fecha previa al evento" if inconsistencia else "",
            })
            doc_id += 1
    return pd.DataFrame(rows)


# ──────────────────────────────────────────────
# 7. GUARDAR EN SQLite
# ──────────────────────────────────────────────
def save_to_sqlite(dfs: dict, db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    for table_name, df in dfs.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  Tabla '{table_name}': {len(df)} registros guardados.")
    conn.close()


def main():
    print("Generando dataset sintético...")
    asegurados = generate_asegurados(200)
    proveedores = generate_proveedores(40)
    polizas = generate_polizas(asegurados, 300)
    vehiculos = generate_vehiculos(asegurados)
    siniestros = generate_siniestros(polizas, asegurados, proveedores, 1000)
    documentos = generate_documentos(siniestros)

    # Tabla scores vacía (la llena el pipeline de ML)
    scores = pd.DataFrame(columns=[
        "id_siniestro", "score_reglas", "score_ml", "score_nlp",
        "score_final", "nivel", "reglas_activadas", "explicacion", "fecha_calculo"
    ])

    db_path = os.path.normpath(DB_PATH)
    print(f"\nGuardando en SQLite: {db_path}")
    save_to_sqlite({
        "asegurados": asegurados,
        "proveedores": proveedores,
        "polizas": polizas,
        "vehiculos": vehiculos,
        "siniestros": siniestros,
        "documentos": documentos,
        "scores_riesgo": scores,
    }, db_path)

    # También exportar CSVs para revisión
    csv_dir = os.path.join(BASE_DIR)
    for name, df in [("siniestros", siniestros), ("polizas", polizas), ("proveedores", proveedores)]:
        df.to_csv(os.path.join(csv_dir, f"{name}.csv"), index=False)

    print(f"\nDataset generado exitosamente.")
    print(f"  Siniestros totales : {len(siniestros)}")
    print(f"  Fraudes simulados  : {siniestros['etiqueta_fraude'].sum()} ({siniestros['etiqueta_fraude'].mean()*100:.1f}%)")
    print(f"  Base de datos      : {db_path}")


if __name__ == "__main__":
    main()
