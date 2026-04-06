import math
from src.math.vec3 import Vec3

def checkerboard_texture(mat_cfg, **kwargs):
    P = kwargs["hit_point"]
    obj = kwargs["obj"]


    check_size = mat_cfg.get("check_size", 1.0)
    color1 = mat_cfg.get("color1", [1, 0, 0])
    color2 = mat_cfg.get("color2", [1, 1, 0])

    u, v = obj.get_uv(P)

    u /= check_size
    v /= check_size

    if (int(math.floor(u)) + int(math.floor(v))) % 2 == 0:
        return color1
    else:
        return color2