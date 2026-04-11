import math
from src.noise.perlin import perlin

def brick_texture(mat_cfg, **kwargs):
    P = kwargs["hit_point"]
    obj = kwargs["obj"]

    u, v = obj.get_uv(P)

    # u *= 10.0
    # v *= 10.0

    bw = mat_cfg.get("brick_width", 1.0)
    bh = mat_cfg.get("brick_height", 0.5)
    mt = mat_cfg.get("mortar_thickness", 0.05)

    brick_color = mat_cfg.get("brick_color", [0.6, 0.15, 0.1])
    mortar_color = mat_cfg.get("mortar_color", [0.85, 0.85, 0.85])

    row = int(math.floor(v / bh))
    if row % 2 == 1:
        u += 0.5 * bw

    u_mod = u % bw
    v_mod = v % bh

    final_result = [0, 0, 0]

    if u_mod < mt or v_mod < mt:
        final_result = mortar_color
    else:
        final_result = brick_color

    # Add Noise
    # NOTE:
    # Noise is applied per-point (object space) to create intra-surface variation.
    if mat_cfg.get("noise", False):
        scale = mat_cfg.get("noise_scale", 5.0)
        amp = mat_cfg.get("noise_amp", 0.1)

        n = perlin(P.x * scale, P.y * scale, P.z * scale)

        final_result = [
            max(0.0, min(1.0, c + amp * (n - 0.5)))
            for c in final_result
        ]

    return final_result