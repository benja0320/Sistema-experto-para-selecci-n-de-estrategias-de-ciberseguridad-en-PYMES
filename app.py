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


def guardar_diagnostico(respuestas, recomendaciones, reglas_activadas):
    with sqlite3.connect(RUTA_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diagnosticos (fecha, respuestas_json, recomendaciones_json, reglas_activadas_json)
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            json.dumps(respuestas, ensure_ascii=False),
            json.dumps(recomendaciones, ensure_ascii=False),
            json.dumps(reglas_activadas, ensure_ascii=False)
        ))
        conn.commit()
    print("Diagnóstico guardado correctamente en la base de datos.")


def obtener_historial(limit=20):
    with sqlite3.connect(RUTA_BD) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fecha FROM diagnosticos ORDER BY id DESC LIMIT ?", (limit,))
        filas = cursor.fetchall()
    return filas


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

def inferir(respuestas):
    recomendaciones = []
    reglas_activadas = []

    if respuestas.get("mfa") != "on": 
        reglas_activadas.append("E101")

        if respuestas.get("usa_cloud") == "on":
            reglas_activadas.append("E101")

        if respuestas.get("exposicion_remota") == "on":
            reglas_activadas.append("E201")

    if respuestas.get("capacitacion") != "on":
        reglas_activadas.append("E102")

        if respuestas.get("mfa") != "on":
            reglas_activadas.append("E104")

    if respuestas.get("parches") != "on":
        reglas_activadas.append("E103")

        if respuestas.get("logging") != "on":
            reglas_activadas.append("E302")

    if respuestas.get("antimalware") != "on":
        reglas_activadas.append("E302")

    if respuestas.get("backups") != "on":
        reglas_activadas.append("E202")

        if respuestas.get("exposicion_remota") == "on":
            reglas_activadas.append("E202")

    if respuestas.get("exposicion_remota") == "on":
        reglas_activadas.append("E201")

        if respuestas.get("usa_cloud") == "on":
            reglas_activadas.append("E201")

    if respuestas.get("usa_cloud") == "on":
        reglas_activadas.append("E101")

        if respuestas.get("sector") == "comercio":
            reglas_activadas.append("E301")

    if respuestas.get("logging") != "on":
        reglas_activadas.append("E302")

    if respuestas.get("activos_criticos") == "on":
        reglas_activadas.append("E202")

        if respuestas.get("sector") == "salud":
            reglas_activadas.append("E302")

    if respuestas.get("sector") == "comercio":
        reglas_activadas.append("E301")
    elif respuestas.get("sector") == "salud":
        reglas_activadas.append("E302")

    if respuestas.get("tamano") == "mediana":
        reglas_activadas.append("E203")

    if respuestas.get("presupuesto") == "bajo":

        reglas_activadas.extend(["E101", "E102", "E103", "E202"])

    reglas_activadas = list(set(reglas_activadas))

    with open("base_conocimiento.json", "r", encoding="utf-8") as f:
        base = json.load(f)

    for e in base:
        if e["id"] in reglas_activadas:
            recomendaciones.append(e)

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

        recomendaciones = inferir(respuestas)

        return render_template("resultado.html",
                               recomendaciones=recomendaciones)

    return render_template("index.html")

@app.route("/historial")
def historial():
    registros = obtener_historial()
    return render_template("historial.html", registros=registros)

if __name__ == "__main__":
    catalogo = cargar_base_conocimiento()

    inicializar_bd()

    app.run(debug=True)
