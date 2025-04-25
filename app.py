from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.integrate import solve_ivp
import numpy as np
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    print("Received parameters:", data)

    a = float(data["a"])
    b = float(data["b"])
    c = float(data["c"])

    def rossler(t, state):
        x, y, z = state
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        return [dx, dy, dz]

    print("Sending dummy data...")
    points = [{"x": i / 10, "y": np.sin(i / 10)} for i in range(100)]
    return jsonify(points)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
