Markdown
# 🛡️ Sistema Experto para Ciberseguridad en PYMES

Este proyecto es un sistema experto basado en reglas, diseñado para diagnosticar el nivel de madurez en ciberseguridad de una Pequeña y Mediana Empresa (PYME). Basado en las respuestas a un formulario web, el sistema infiere y recomienda estrategias de ciberseguridad prioritarias.

## 🏛️ Contexto del Proyecto

Este repositorio corresponde al **Trabajo Práctico 3**  de la asignatura **Inteligencia Artificial (2025-2)**, impartida por la Dra. Carola Figueroa-Flores.

El objetivo es aplicar la metodología **CommonKADS** para el modelado del conocimiento [cite: 10, 6] y desarrollar un motor de inferencia propio para el tema asignado: **"Sistema experto para selección de estrategias de ciberseguridad en PYMES"**.

## ✨ Características Principales

* **Diagnóstico Interactivo:** Un formulario web simple (UI) para recolectar el estado actual de la PYME.
* **Motor de Inferencia Propio:** Lógica de reglas en Python (`app.py`) que analiza las respuestas y activa recomendaciones.
* **Base de Conocimiento Flexible:** Las estrategias, justificaciones y metadatos se almacenan en `base_conocimiento.json`, permitiendo fácil actualización.
* **Historial de Diagnósticos:** Cada resultado se almacena en una base de datos **SQLite** (`historial_diagnosticos.db`) para consulta futura.


## 💻 Stack Tecnológico

* **Backend:** Python 3, Flask
* **Base de Conocimiento:** JSON
* **Frontend:** HTML5, Bootstrap 5
* **Entorno:** `venv` (para reproducibilidad) 

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para ejecutar el proyecto en tu máquina.

**1. Clonar el Repositorio:**

```bash
git clone https://github.com/benja0320/Sistema-experto-para-selecci-n-de-estrategias-de-ciberseguridad-en-PYMES.git
cd tu-repositorio
2. Crear y Activar un Entorno Virtual:

Esto es fundamental para cumplir con el requisito de reproducibilidad.

Bash
# Crear el entorno
python -m venv venv

# Activar el entorno
# En Windows (cmd):
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate

3. Instalar las Dependencias:

El archivo requirements.md contiene las bibliotecas necesarias (Flask).

Bash
pip install -r requirements.md


4. Ejecutar la Aplicación:

El siguinte comando iniciará la base de datos (si no existe) y arrancará el servidor web de Flask.

Bash
python app.py
5. Acceder al Sistema:

Abre tu navegador y visita la siguiente dirección: http://127.0.0.1:5000

 Manual de Usuario
1. Realizar un Diagnóstico

En la página principal, completa el formulario con la información de la PYME (Tamaño, Sector, etc.).

Responde el cuestionario. Los interruptores funcionan así:

ON (azul): Significa que la medida YA ESTÁ IMPLEMENTADA (Ej: "Sí, tengo MFA").

OFF (gris): Significa que la medida FALTA o se desconoce (Ej: "No, no tengo backups").

Haz clic en el botón verde "Obtener recomendaciones".

2. Revisar Resultados

Serás redirigido a la página de resultados.

A la izquierda, verás la lista de estrategias que el sistema experto ha inferido para ti (Ej: "Política de Backups 3-2-1").

A la derecha, podrás ver el detalle de cada recomendación (Área, Costo, Impacto y Justificación).


👥 Autores
[Benjamin Jimenez]

[Cristobal Morales ]


---
---