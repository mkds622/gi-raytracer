import math

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

    if u_mod < mt or v_mod < mt:
        return mortar_color
    return brick_color