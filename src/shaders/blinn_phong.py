from __future__ import annotations
from src.math.vec3 import Vec3
from src.shaders.phong import PhongMaterial


def shade_blinn_phong(
    *,
    ambient_light_rgb: Vec3,
    light_pos: Vec3,
    light_rgb: Vec3,
    hit_point: Vec3,
    normal: Vec3,
    view_dir: Vec3,
    mat_cfg: dict,
) -> Vec3:
    mat = PhongMaterial(
        ka=float(mat_cfg["ka"]),
        kd=float(mat_cfg["kd"]),
        ks=float(mat_cfg["ks"]),
        ke=float(mat_cfg["ke"]),
        ambient_color=Vec3(*mat_cfg["ambient_color"]),
        diffuse_color=Vec3(*mat_cfg["diffuse_color"]),
        specular_color=Vec3(*mat_cfg["specular_color"]),
    )

    n = normal.normalized()
    s = (light_pos - hit_point).normalized()
    v = view_dir.normalized()
    h = (s + v).normalized()

    ambient = mat.ambient_color * mat.ka
    ambient = Vec3(
        ambient.x * ambient_light_rgb.x,
        ambient.y * ambient_light_rgb.y,
        ambient.z * ambient_light_rgb.z,
    )

    ndotl = max(0.0, n.dot(s))
    diffuse = mat.diffuse_color * (mat.kd * ndotl)
    diffuse = Vec3(
        diffuse.x * light_rgb.x,
        diffuse.y * light_rgb.y,
        diffuse.z * light_rgb.z,
    )

    ndoth = max(0.0, n.dot(h))
    spec_strength = (ndoth ** mat.ke) if ndoth > 0.0 else 0.0
    specular = mat.specular_color * (mat.ks * spec_strength)
    specular = Vec3(
        specular.x * light_rgb.x,
        specular.y * light_rgb.y,
        specular.z * light_rgb.z,
    )

    return ambient + diffuse + specular