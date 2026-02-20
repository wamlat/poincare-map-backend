from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_compress import Compress
import os
import ctypes
import subprocess
import platform
import time
import math

app = Flask(__name__)
CORS(app, supports_credentials=True)
Compress(app)

# Compile the C++ code
def compile_solver():
    system = platform.system()
    if system == "Windows":
        subprocess.run(["g++", "-shared", "-o", "solver.dll", "-O2", "solver_wrapper.cpp"])
        return ctypes.CDLL("./solver.dll")
    else:  # Linux or Mac
        subprocess.run(["g++", "-shared", "-o", "libsolver.so", "-fPIC", "-O2", "solver_wrapper.cpp"])
        return ctypes.CDLL("./libsolver.so")

try:
    solver_lib = compile_solver()

    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("z", ctypes.c_double)]

    solver_lib.compute_poincare_map.argtypes = [
        ctypes.c_double, ctypes.c_double, ctypes.c_double,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)
    ]
    solver_lib.compute_poincare_map.restype = ctypes.POINTER(Point)
    solver_lib.free_points.argtypes = [ctypes.POINTER(Point)]

    USE_CPP = True
except Exception as e:
    print(f"Failed to compile C++ code: {e}")
    print("Falling back to Python implementation")
    USE_CPP = False

result_cache = {}

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

    cache_key = f"{a}_{b}_{c}"

    if cache_key in result_cache:
        print(f"Using cached result for {cache_key}", flush=True)
        return jsonify(result_cache[cache_key])

    start_time = time.time()

    if USE_CPP:
        print("Starting C++ computation...", flush=True)
        size = ctypes.c_int()
        status = ctypes.c_int()
        points_array = solver_lib.compute_poincare_map(
            a, b, c, ctypes.byref(size), ctypes.byref(status)
        )

        points = []
        for i in range(size.value):
            points.append({"x": points_array[i].x, "z": points_array[i].z})

        solver_lib.free_points(points_array)
        diverged = status.value == 1
        elapsed = time.time() - start_time
        print(f"C++ done. {len(points)} crossings, {elapsed:.2f}s, diverged={diverged}", flush=True)
    else:
        points = []
        x, y, z = 1.0, 1.0, 1.0
        dt = 0.01
        max_iter = 200000
        diverged = False

        print("Starting Python computation...", flush=True)
        for i in range(1, max_iter):
            k1x = -y - z
            k1y = x + a * y
            k1z = b + z * (x - c)

            k2x = -(y + 0.5 * dt * k1y) - (z + 0.5 * dt * k1z)
            k2y = (x + 0.5 * dt * k1x) + a * (y + 0.5 * dt * k1y)
            k2z = b + (z + 0.5 * dt * k1z) * ((x + 0.5 * dt * k1x) - c)

            k3x = -(y + 0.5 * dt * k2y) - (z + 0.5 * dt * k2z)
            k3y = (x + 0.5 * dt * k2x) + a * (y + 0.5 * dt * k2y)
            k3z = b + (z + 0.5 * dt * k2z) * ((x + 0.5 * dt * k2x) - c)

            k4x = -(y + dt * k3y) - (z + dt * k3z)
            k4y = (x + dt * k3x) + a * (y + dt * k3y)
            k4z = b + (z + dt * k3z) * ((x + dt * k3x) - c)

            x1 = x + dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6
            y1 = y + dt * (k1y + 2 * k2y + 2 * k3y + k4y) / 6
            z1 = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6

            if abs(x1) > 1e10 or abs(y1) > 1e10 or abs(z1) > 1e10 or math.isnan(x1) or math.isnan(y1) or math.isnan(z1):
                diverged = True
                break

            if y < 0 and y1 >= 0:
                alpha = -y / (y1 - y)
                px = x + alpha * (x1 - x)
                pz = z + alpha * (z1 - z)
                points.append({"x": px, "z": pz})

            x, y, z = x1, y1, z1

        elapsed = time.time() - start_time
        print(f"Python done. {len(points)} crossings, {elapsed:.2f}s, diverged={diverged}", flush=True)

    result = {"points": points, "diverged": diverged, "count": len(points)}
    result_cache[cache_key] = result

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
