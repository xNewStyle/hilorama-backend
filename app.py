from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "Hilorama backend activo"}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    return jsonify({
        "ok": True,
        "user": data.get("user")
    })

@app.route("/notas", methods=["GET"])
def notas():
    return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
