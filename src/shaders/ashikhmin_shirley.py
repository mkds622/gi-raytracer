from __future__ import annotations
from src.math.vec3 import Vec3
import math


def shade_ashikhmin_shirley(
    *,
    ambient_light_rgb: Vec3,
    light_pos: Vec3,
    light_rgb: Vec3,
    hit_point: Vec3,
    normal: Vec3,
    view_dir: Vec3,
    mat_cfg: dict,
) -> Vec3:

    n = normal.normalized()
    v = view_dir.normalized()
    l = (light_pos - hit_point).normalized()
    h = (v + l).normalized()

    # --- Build tangent frame (u, v, n) ---
    up = Vec3(0.0, 1.0, 0.0)
    if abs(n.dot(up)) > 0.99:
        up = Vec3(1.0, 0.0, 0.0)

    u = up.cross(n).normalized()
    v_tangent = n.cross(u).normalized()

    # Dot products
    ndotl = max(n.dot(l), 0.0)
    ndotv = max(n.dot(v), 0.0)
    ndoth = max(0.0, min(1.0, n.dot(h)))

    hu = h.dot(u)
    hv = h.dot(v_tangent)

    # Parameters
    Rs = float(mat_cfg["Rs"])
    Rd = float(mat_cfg["Rd"])
    nu = float(mat_cfg["nu"])
    nv = float(mat_cfg["nv"])

    # --- Specular term (anisotropic) ---
    if ndotl > 0 and ndotv > 0:
        denom = max(1e-6, (1.0 - ndoth * ndoth))
        exponent = (nu * hu * hu + nv * hv * hv) / denom
        spec = math.sqrt((nu + 1) * (nv + 1)) / (8 * math.pi)
        spec *= math.exp(exponent * math.log(max(ndoth, 1e-6))) / max(1e-6, (h.dot(v)) * max(ndotl, ndotv))
    else:
        spec = 0.0

    # --- Diffuse term ---
    diffuse = Rd * (28.0 / (23.0 * math.pi))
    diffuse *= (1 - Rs)
    diffuse *= (1 - (1 - ndotl / 2) ** 5)
    diffuse *= (1 - (1 - ndotv / 2) ** 5)

    # Final color
    color = Vec3(0.0, 0.0, 0.0)

    # ambient (reuse simple model)
    ambient = ambient_light_rgb * Rd
    color += ambient

    # light contribution
    color += light_rgb * ((diffuse + Rs * spec) * ndotl)

    return color