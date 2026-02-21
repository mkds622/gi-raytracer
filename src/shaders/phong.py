from __future__ import annotations
from dataclasses import dataclass
from src.math.vec3 import Vec3


@dataclass(frozen=True)
class PhongMaterial:
    ka: float
    kd: float
    ks: float
    ke: float
    ambient_color: Vec3
    diffuse_color: Vec3
    specular_color: Vec3


def reflect(i: Vec3, n: Vec3) -> Vec3:
    # i: incident direction (pointing *into* surface), n: normal
    return i - n * (2.0 * i.dot(n))


def shade_phong(
    *,
    ambient_light_rgb: Vec3,
    light_pos: Vec3,
    light_rgb: Vec3,
    hit_point: Vec3,
    normal: Vec3,
    view_dir: Vec3,  # direction from hit -> camera (normalized)
    mat: PhongMaterial,
) -> Vec3:
    """
    Returns linear RGB (0..inf). No clamping/tone-map here.
    Shadowing is handled outside this function.
    """
    n = normal.normalized()
    s = (light_pos - hit_point).normalized()

    # Ambient
    ambient = mat.ambient_color * mat.ka
    ambient = Vec3(
        ambient.x * ambient_light_rgb.x,
        ambient.y * ambient_light_rgb.y,
        ambient.z * ambient_light_rgb.z,
    )

    # Diffuse
    ndotl = max(0.0, n.dot(s))
    diffuse = mat.diffuse_color * (mat.kd * ndotl)
    diffuse = Vec3(
        diffuse.x * light_rgb.x,
        diffuse.y * light_rgb.y,
        diffuse.z * light_rgb.z,
    )

    # Specular (Phong using reflection vector)
    r = reflect(-s, n).normalized()
    rdotv = max(0.0, r.dot(view_dir))
    spec_strength = (rdotv ** mat.ke) if rdotv > 0.0 else 0.0
    specular = mat.specular_color * (mat.ks * spec_strength)
    specular = Vec3(
        specular.x * light_rgb.x,
        specular.y * light_rgb.y,
        specular.z * light_rgb.z,
    )

    return ambient + diffuse + specular