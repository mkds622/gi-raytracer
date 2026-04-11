import math
from src.math.vec3 import Vec3
from src.noise.perlin import perlin

def checkerboard_texture(mat_cfg, **kwargs):
    P = kwargs["hit_point"]
    obj = kwargs["obj"]


    check_size = mat_cfg.get("check_size", 1.0)
    color1 = mat_cfg.get("color1", [1, 0, 0])
    color2 = mat_cfg.get("color2", [1, 1, 0])

    u, v = obj.get_uv(P)

    u /= check_size
    v /= check_size

    final_result = [0, 0, 0]

    if (int(math.floor(u)) + int(math.floor(v))) % 2 == 0:
        final_result = color1
    else:
        final_result = color2

    # Add Noise
    if mat_cfg.get("noise", False):
        scale = mat_cfg.get("noise_scale", 5.0)
        amp = mat_cfg.get("noise_amp", 0.1)

        n = perlin(P.x * scale, P.y * scale, P.z * scale)

        final_result = [
            max(0.0, min(1.0, c + amp * (n - 0.5)))
            for c in final_result
        ]

    return final_result