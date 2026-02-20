
#include <vector>
#include <utility>
#include <cstdlib>
#include <cmath>

extern "C" {
    struct Result {
        double x;
        double z;
    };

    // status: 0 = success, 1 = diverged
    Result* compute_poincare_map(double a, double b, double c, int* size, int* status) {
        std::vector<std::pair<double, double>> points;
        double x = 1.0, y = 1.0, z = 1.0;
        double dt = 0.01;
        int max_iter = 200000;
        *status = 0;

        for (int i = 1; i < max_iter; ++i) {
            // RK4 integration
            double k1x = -y - z;
            double k1y = x + a * y;
            double k1z = b + z * (x - c);

            double k2x = -(y + 0.5 * dt * k1y) - (z + 0.5 * dt * k1z);
            double k2y = (x + 0.5 * dt * k1x) + a * (y + 0.5 * dt * k1y);
            double k2z = b + (z + 0.5 * dt * k1z) * ((x + 0.5 * dt * k1x) - c);

            double k3x = -(y + 0.5 * dt * k2y) - (z + 0.5 * dt * k2z);
            double k3y = (x + 0.5 * dt * k2x) + a * (y + 0.5 * dt * k2y);
            double k3z = b + (z + 0.5 * dt * k2z) * ((x + 0.5 * dt * k2x) - c);

            double k4x = -(y + dt * k3y) - (z + dt * k3z);
            double k4y = (x + dt * k3x) + a * (y + dt * k3y);
            double k4z = b + (z + dt * k3z) * ((x + dt * k3x) - c);

            double x1 = x + dt * (k1x + 2 * k2x + 2 * k3x + k4x) / 6;
            double y1 = y + dt * (k1y + 2 * k2y + 2 * k3y + k4y) / 6;
            double z1 = z + dt * (k1z + 2 * k2z + 2 * k3z + k4z) / 6;

            // Divergence guard
            if (std::abs(x1) > 1e10 || std::abs(y1) > 1e10 || std::abs(z1) > 1e10 ||
                std::isnan(x1) || std::isnan(y1) || std::isnan(z1)) {
                *status = 1;
                break;
            }

            // Poincaré section: y crosses zero upward
            if (y < 0 && y1 >= 0) {
                double alpha = -y / (y1 - y);
                double px = x + alpha * (x1 - x);
                double pz = z + alpha * (z1 - z);
                points.emplace_back(px, pz);
            }

            x = x1; y = y1; z = z1;
        }

        *size = points.size();
        Result* result = (Result*)malloc(points.size() * sizeof(Result));

        for (size_t i = 0; i < points.size(); ++i) {
            result[i].x = points[i].first;
            result[i].z = points[i].second;
        }

        return result;
    }

    void free_points(Result* points) {
        free(points);
    }
}
