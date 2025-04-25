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
    t_span = (0, 300)
    t_eval = np.linspace(*t_span, 12000)

    print("Starting integration...", flush=True)
    sol = solve_ivp(rossler, t_span, y0, t_eval=t_eval, rtol=1e-6)  # loosen rtol for speed
    x, y, z = sol.y
    print("Integration complete.", flush=True)

    print("First few z values:", z[:10], flush=True)

    points = []
    crossings = 0
    for i in range(1, len(z)):
        if z[i - 1] < 0 and z[i] >= 0:
            alpha = -z[i - 1] / (z[i] - z[i - 1])
            px = x[i - 1] + alpha * (x[i] - x[i - 1])
            py = y[i - 1] + alpha * (y[i] - y[i - 1])
            points.append({"x": px, "y": py})
            crossings += 1

    print(f"Total crossings detected: {crossings}", flush=True)
    return jsonify(points)
