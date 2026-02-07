from flask import Flask, request, jsonify

app = Flask(__name__)

# =========================
# USUARIOS (TEMPORAL)
# =========================
USUARIOS = {
    "empacador1": {
        "password": "1234",
        "nombre": "Juan Empacador",
        "rol": "EMPACADOR"
    },
    "admin": {
        "password": "admin123",
        "nombre": "Administrador",
        "rol": "ADMIN"
    }
}

# =========================
# NOTAS (ÚNICA FUENTE)
# =========================
NOTAS = [
    {
        "id": "VTA-0001",
        "cliente": "Brenda",
        "estado": "EN_PROCESO",
        "empacador": "empacador1",
        "productos": [
            {
                "codigo": "HIL-ROJO-123",
                "color": "ROJO",
                "pz_requeridas": 3,
                "pz_empacadas": 0
            },
            {
                "codigo": "HIL-AZUL-456",
                "color": "AZUL",
                "pz_requeridas": 1,
                "pz_empacadas": 0
            }
        ]
    }
]

# =========================
# VALIDAR TOKEN
# =========================
def validar_token(req):
    auth = req.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return None

    token = auth.replace("Bearer ", "")

    tokens_validos = {
        "token-empacador1": "empacador1",
        "token-admin": "admin"
    }

    usuario = tokens_validos.get(token)
    if not usuario:
        return None

    return {
        "usuario": usuario,
        "rol": USUARIOS[usuario]["rol"]
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
    auth = validar_token(request)

    if not auth:
        return jsonify({"error": "No autorizado"}), 401

    if auth["rol"] != "EMPACADOR":
        return jsonify({"error": "Acceso denegado"}), 403

    usuario = auth["usuario"]

    notas_empacador = [
        n for n in NOTAS if n["empacador"] == usuario
    ]

    return jsonify(notas_empacador)




@app.route("/notas/<nota_id>/asignar", methods=["POST"])
def asignar_nota(nota_id):
    auth = validar_token(request)

    if not auth:
        return jsonify({"error": "No autorizado"}), 401

    if auth["rol"] != "ADMIN":
        return jsonify({"error": "Solo admin puede asignar"}), 403

    empacador = request.json.get("empacador")

    if empacador not in USUARIOS:
        return jsonify({"error": "Empacador no existe"}), 400

    for nota in NOTAS:
        if nota["id"] == nota_id:
            nota["empacador"] = empacador
            nota["estado"] = "EN_PROCESO"
            return jsonify(nota)

    return jsonify({"error": "Nota no encontrada"}), 404

# =========================
# CAMBIAR ESTADO DE NOTA
# =========================
@app.route("/notas/<nota_id>/estado", methods=["POST"])
def cambiar_estado(nota_id):
    auth = validar_token(request)

    if not auth:
        return jsonify({"error": "No autorizado"}), 401

    nuevo_estado = request.json.get("estado")

    ESTADOS_VALIDOS = ["PENDIENTE", "EN_PROCESO", "COMPLETA", "INCOMPLETA"]

    if nuevo_estado not in ESTADOS_VALIDOS:
        return jsonify({"error": "Estado inválido"}), 400

    for nota in NOTAS:
        if nota["id"] == nota_id:
            estado_actual = nota["estado"]

            # 🔒 reglas de transición
            if estado_actual == "PENDIENTE" and nuevo_estado == "EN_PROCESO":
                nota["estado"] = nuevo_estado
                return jsonify(nota)

            if estado_actual == "EN_PROCESO" and nuevo_estado in ["COMPLETA", "INCOMPLETA"]:
                nota["estado"] = nuevo_estado
                return jsonify(nota)

            if estado_actual == "INCOMPLETA" and nuevo_estado == "EN_PROCESO":
                nota["estado"] = nuevo_estado
                return jsonify(nota)

            return jsonify({"error": "Transición no permitida"}), 400

    return jsonify({"error": "Nota no encontrada"}), 404

@app.route("/notas/<nota_id>/reset", methods=["POST"])
def resetear_nota(nota_id):
    auth = validar_token(request)

    if not auth or auth["rol"] != "ADMIN":
        return jsonify({"error": "No autorizado"}), 401

    for nota in NOTAS:
        if nota["id"] == nota_id:
            nota["empacador"] = None
            nota["estado"] = "PENDIENTE"
            return jsonify(nota)

    return jsonify({"error": "Nota no encontrada"}), 404

@app.route("/notas/<nota_id>/scan", methods=["POST"])
def escanear_producto(nota_id):
    auth = validar_token(request)

    if not auth:
        return jsonify({"error": "No autorizado"}), 401

    codigo_escaneado = request.json.get("codigo")

    if not codigo_escaneado:
        return jsonify({"error": "Código vacío"}), 400

    for nota in NOTAS:
        if nota["id"] == nota_id:

            for prod in nota["productos"]:
                if prod["codigo"] == codigo_escaneado:

                    if prod["pz_empacadas"] >= prod["pz_requeridas"]:
                        return jsonify({
                            "error": "Piezas ya completas",
                            "codigo": codigo_escaneado
                        }), 409

                    prod["pz_empacadas"] += 1

                    return jsonify({
                        "ok": True,
                        "producto": prod
                    })

            return jsonify({
                "error": "Código no pertenece a la nota",
                "codigo": codigo_escaneado
            }), 404

    return jsonify({"error": "Nota no encontrada"}), 404

@app.route("/notas/<nota_id>/producto/ajustar", methods=["POST"])
def ajustar_producto(nota_id):
    auth = validar_token(request)

    if not auth:
        return jsonify({"error": "No autorizado"}), 401

    data = request.json
    codigo = data.get("codigo")
    cantidad = data.get("cantidad")

    if not codigo or cantidad is None:
        return jsonify({"error": "Datos incompletos"}), 400

    if not isinstance(cantidad, int):
        return jsonify({"error": "Cantidad debe ser entera"}), 400

    for nota in NOTAS:
        if nota["id"] == nota_id:

            for prod in nota["productos"]:
                if prod["codigo"] == codigo:

                    nuevo_total = prod["pz_empacadas"] + cantidad

                    if nuevo_total < 0:
                        return jsonify({
                            "error": "No puede ser menor a 0",
                            "actual": prod["pz_empacadas"]
                        }), 409

                    if nuevo_total > prod["pz_requeridas"]:
                        return jsonify({
                            "error": "Excede piezas requeridas",
                            "requeridas": prod["pz_requeridas"],
                            "actual": prod["pz_empacadas"]
                        }), 409

                    prod["pz_empacadas"] = nuevo_total

                    return jsonify({
                        "ok": True,
                        "producto": prod
                    })

            return jsonify({
                "error": "Producto no pertenece a la nota",
                "codigo": codigo
            }), 404

    return jsonify({"error": "Nota no encontrada"}), 404

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run()
