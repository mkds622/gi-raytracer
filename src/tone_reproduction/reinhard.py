from src.math.vec3 import Vec3
import math


def _luminance(c: Vec3) -> float:
    return 0.27 * c.x + 0.67 * c.y + 0.06 * c.z


def _log_average_luminance(buffer, delta=1e-6):
    h = len(buffer)
    w = len(buffer[0])
    N = h * w

    s = 0.0
    for j in range(h):
        for i in range(w):
            L = _luminance(buffer[j][i])
            s += math.log(delta + L)

    return math.exp(s / N)


def apply(buffer, Ldmax: float):
    h = len(buffer)
    w = len(buffer[0])

    Lavg = _log_average_luminance(buffer)
    a = 0.18

    out = [[Vec3(0.0, 0.0, 0.0) for _ in range(w)] for _ in range(h)]

    for j in range(h):
        for i in range(w):
            c = buffer[j][i]

            # Step 1: scale
            Rs = (a / Lavg) * c.x
            Gs = (a / Lavg) * c.y
            Bs = (a / Lavg) * c.z

            # Step 2: compress
            Rr = Rs / (1.0 + Rs)
            Gr = Gs / (1.0 + Gs)
            Br = Bs / (1.0 + Bs)

            # Step 3: scale to display + normalize
            out[j][i] = Vec3(
                (Rr * Ldmax) / Ldmax,
                (Gr * Ldmax) / Ldmax,
                (Br * Ldmax) / Ldmax,
            )

    return out
    