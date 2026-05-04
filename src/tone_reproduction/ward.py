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

    # Step 1: log-average luminance
    Lwa = _log_average_luminance(buffer)

    # Step 2: scale factor (Ward)
    numerator = 1.219 + (Ldmax / 2.0) ** 0.4
    denominator = 1.219 + (Lwa) ** 0.4
    sf = (numerator / denominator) ** 2.5

    # Step 3: apply scaling + device normalization
    out = [[Vec3(0.0, 0.0, 0.0) for _ in range(w)] for _ in range(h)]

    for j in range(h):
        for i in range(w):
            mapped = buffer[j][i] * sf

            # Step 4: device scaling
            out[j][i] = mapped * (1.0 / Ldmax)

    return out