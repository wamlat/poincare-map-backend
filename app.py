from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.integrate import solve_ivp
import numpy as np
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/")
def home():
    return "Backend is running!"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    print("Received parameters:", data, flush=True)

    a = float(data["a"])
    b = float(data["b"])
    c = float(data["c"])

    def rossler(t, state):
        x, y, z = state
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        return [dx, dy, dz]

    y0 = [1.0, 1.0, 1.0]
    t_span = (0, 300)  # Extended to allow more crossings
    t_eval = np.linspace(*t_span, 12000)
    print("Starting integration...", flush=True)

    sol = solve_ivp(rossler, t_span, y0, t_eval=t_eval, rtol=1e-6)
    x, y, z = sol.y
    print("Integration complete.", flush=True)
    print("First few z values:", z[:10], flush=True)

    points = []
    crossings = 0
    for i in range(1, len(y)):
        if y[i - 1] < 0 and y[i] >= 0:  # crossing y = 0 from below
            alpha = -y[i - 1] / (y[i] - y[i - 1])
            px = x[i - 1] + alpha * (x[i] - x[i - 1])
            pz = z[i - 1] + alpha * (z[i] - z[i - 1])
            points.append({"x": px, "z": pz})
            crossings += 1

    print(f"Total crossings detected: {crossings}", flush=True)
    return jsonify(points)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

