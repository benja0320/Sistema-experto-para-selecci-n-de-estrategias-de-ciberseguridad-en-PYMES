from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

RUTA_BD = "historial_diagnosticos.db"
RUTA_JSON = "base_conocimiento.json"

def cargar_base_conocimiento(ruta_json=RUTA_JSON):
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            estrategias = json.load(f)
        base = {e["id"]: e for e in estrategias}
        print(f"Base de conocimiento cargada correctamente ({len(base)} estrategias).")
        return base
    except FileNotFoundError:
        print("Archivo base_conocimiento.json no encontrado.")
        return {}
    except json.JSONDecodeError:
        print("Error al leer el archivo JSON. Verifica su formato.")
        return {}

catalogo = cargar_base_conocimiento()

def inicializar_bd(ruta_bd=RUTA_BD):
    with sqlite3.connect(ruta_bd) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnosticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                respuestas_json TEXT,
                recomendaciones_json TEXT,
                reglas_activadas_json TEXT
            );
        """)
        conn.commit()
    print("Base de datos SQLite verificada / creada correctamente.")

def obtener_diagnostico(id_diagnostico):
    with sqlite3.connect(RUTA_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, respuestas_json, recomendaciones_json, reglas_activadas_json
            FROM diagnosticos
            WHERE id = ?
        """, (id_diagnostico,))
        fila = cursor.fetchone()
    return fila


import json

def inferir(respuestas, base_conocimiento):
    reglas_activadas = set()

    # E101: Implementar MFA
    if respuestas.get("mfa") != "on":
        reglas_activadas.add("E101")

    # E102: Capacitación
    if respuestas.get("capacitacion") != "on":
        reglas_activadas.add("E102")

    # E104: Gestor de Contraseñas
    if respuestas.get("mfa") != "on" and respuestas.get("capacitacion") != "on":
        reglas_activadas.add("E104")

    # E103: Gestión de Parches
    if respuestas.get("parches") != "on":
        reglas_activadas.add("E103")

    # E201: Acceso Remoto Seguro (VPN)
    if respuestas.get("exposicion_remota") != "on":
        reglas_activadas.add("E201")
        
    # E301: Protección de Aplicaciones Web (WAF)
    if respuestas.get("sector", "").lower() == "comercio" and respuestas.get("usa_cloud") == "on":
        reglas_activadas.add("E301")

    # E203: Control de acceso/Firewall (Contextual por tamaño)
    if respuestas.get("tamano", "").lower() == "mediana" and respuestas.get("antimalware") != "on":
        reglas_activadas.add("E203")

    # E202: Copias de Seguridad (Backups)
    if respuestas.get("backups") != "on":
        reglas_activadas.add("E202")

    # E302: Detección y Respuesta (EDR/Logging)
    
    cond_1_no_antimalware = respuestas.get("antimalware") != "on"
    cond_2_no_logging = respuestas.get("logging") != "on"
    
    # Condición de alto riesgo: Salud, datos críticos Y sin backups
    cond_3_riesgo_salud = (
        respuestas.get("sector", "").lower() == "salud" and
        respuestas.get("activos_criticos") == "on" and
        respuestas.get("backups") != "on" 
    )
    
    # Si cualquiera de estas condiciones es verdadera, se activa la E302.
    if cond_1_no_antimalware or cond_2_no_logging or cond_3_riesgo_salud:
        reglas_activadas.add("E302")
    
    recomendaciones = []
    for regla_id in sorted(list(reglas_activadas)): # Usamos sorted() para un orden consistente
        # Buscamos la regla en la base de conocimiento cargada
        if regla_id in base_conocimiento:
            recomendaciones.append(base_conocimiento[regla_id])
        else:
            print(f"Advertencia: Regla '{regla_id}' activada pero no encontrada en base_conocimiento.json")
    
    print(f"Opciones activadas: {respuestas}")
    print(f"Reglas activadas ({len(recomendaciones)}): {reglas_activadas}")

    return recomendaciones



@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        tamano = request.form.get("tamano")
        sector = request.form.get("sector")
        presupuesto = request.form.get("presupuesto")

        activos_criticos = request.form.get("activos_criticos")
        usa_cloud = request.form.get("usa_cloud")
        mfa = request.form.get("mfa")
        backups = request.form.get("backups")
        exposicion_remota = request.form.get("exposicion_remota")
        antimalware = request.form.get("antimalware")
        parches = request.form.get("parches")
        capacitacion = request.form.get("capacitacion")
        logging = request.form.get("logging")

        respuestas = {
            "tamano": tamano,
            "sector": sector,
            "presupuesto": presupuesto,
            "activos_criticos": activos_criticos,
            "usa_cloud": usa_cloud,
            "mfa": mfa,
            "backups": backups,
            "exposicion_remota": exposicion_remota,
            "antimalware": antimalware,
            "parches": parches,
            "capacitacion": capacitacion,
            "logging": logging
        }

        recomendaciones = inferir(respuestas, catalogo)

        return render_template("resultado.html",
                               recomendaciones=recomendaciones)

    return render_template("index.html")

if __name__ == "__main__":
    inicializar_bd()

    app.run(debug=True)
