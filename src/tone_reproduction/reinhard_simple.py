from src.math.vec3 import Vec3


def apply(buffer, Ldmax: float):
    h = len(buffer)
    w = len(buffer[0])

    out = [[Vec3(0.0, 0.0, 0.0) for _ in range(w)] for _ in range(h)]

    for j in range(h):
        for i in range(w):
            c = buffer[j][i]

            # Reinhard simple
            mapped = Vec3(
                c.x / (1.0 + c.x),
                c.y / (1.0 + c.y),
                c.z / (1.0 + c.z),
            )

            # device scaling
            out[j][i] = mapped * (1.0 / Ldmax)

    return out