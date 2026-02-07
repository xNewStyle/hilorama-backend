from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# USUARIOS (TEMPORAL)
# =========================
USUARIOS = {
    "empacador1": {
        "password": "1234",
        "nombre": "Juan Empacador"
    },
    "admin": {
        "password": "admin123",
        "nombre": "Administrador"
    }
}

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return {"status": "Hilorama backend activo"}

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    usuario = data.get("usuario")
    password = data.get("password")

    if usuario not in USUARIOS:
        return jsonify({"ok": False, "mensaje": "Usuario no existe"}), 401

    if USUARIOS[usuario]["password"] != password:
        return jsonify({"ok": False, "mensaje": "Contraseña incorrecta"}), 401

    # 🔑 token simple (luego lo mejoramos)
    token = f"token-{usuario}"

    return jsonify({
        "ok": True,
        "token": token,
        "nombre": USUARIOS[usuario]["nombre"]
    })


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
