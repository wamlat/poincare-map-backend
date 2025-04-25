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

    y0 = [1.0, 1.0, 1.0]
    t_span = (0, 100)
    t_eval = np.linspace(*t_span, 5000)

    print("Starting integration...")
    sol = solve_ivp(rossler, t_span, y0, t_eval=t_eval, rtol=1e-9)
    x, y, z = sol.y
    print("Integration complete.")

    points = []
    for i in range(1, len(z)):
        if z[i - 1] < 0 and z[i] >= 0:
            alpha = -z[i - 1] / (z[i] - z[i - 1])
            px = x[i - 1] + alpha * (x[i] - x[i - 1])
            py = y[i - 1] + alpha * (y[i] - y[i - 1])
            points.append({"x": px, "y": py})

    print(f"Returning {len(points)} points")
    return jsonify(points)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
