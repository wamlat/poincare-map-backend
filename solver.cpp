// solver.cpp
#include <vector>
#include <utility>

std::vector<std::pair<double, double>> compute_poincare(double a, double b, double c) {
    std::vector<std::pair<double, double>> points;
    double x = 1.0, y = 1.0, z = 1.0;
    double dt = 0.01;

    for (int i = 1; i < 12000; ++i) {
        double dx = -y - z;
        double dy = x + a * y;
        double dz = b + z * (x - c);

        double x1 = x + dt * dx;
        double y1 = y + dt * dy;
        double z1 = z + dt * dz;

        if (y < 0 && y1 >= 0) {
            double alpha = -y / (y1 - y);
            double px = x + alpha * (x1 - x);
            double pz = z + alpha * (z1 - z);
            points.emplace_back(px, pz);
        }

        x = x1; y = y1; z = z1;
    }

    return points;
}
