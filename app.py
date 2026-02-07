from flask import Flask, jsonify

app = Flask(__name__)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "Hilorama backend activo"}

# =========================
# NOTAS PAGADAS (EMPACADOR)
# =========================
@app.route("/notas-pagadas", methods=["GET"])
def notas_pagadas():
    notas = [
        {
            "id": "VTA-0001",
            "cliente": "Brenda",
            "telefono": "5578412147",
            "prioridad": "ALTA",
            "estado": "PENDIENTE"
        },
        {
            "id": "VTA-0002",
            "cliente": "Carlos",
            "telefono": "5587459632",
            "prioridad": "MEDIA",
            "estado": "EN_PROCESO"
        },
        {
            "id": "VTA-0003",
            "cliente": "María",
            "telefono": "5512349876",
            "prioridad": "BAJA",
            "estado": "COMPLETA"
        }
    ]

    return jsonify(notas)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run()
