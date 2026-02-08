from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from src.math.vec3 import Vec3
from src.core.ray import Ray


@dataclass(frozen=True)
class Hit:
    t: float
    point: Vec3
    normal: Vec3
    material_name: str


def intersect_sphere(ray: Ray, center: Vec3, radius: float, material_name: str, t_min: float, t_max: float) -> Optional[Hit]:
    oc = ray.origin - center
    a = ray.direction.dot(ray.direction)
    b = 2.0 * oc.dot(ray.direction)
    c = oc.dot(oc) - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return None
    sqrt_disc = disc ** 0.5

    # nearest root first
    t1 = (-b - sqrt_disc) / (2.0 * a)
    t2 = (-b + sqrt_disc) / (2.0 * a)

    t_hit = None
    if t_min < t1 < t_max:
        t_hit = t1
    elif t_min < t2 < t_max:
        t_hit = t2

    if t_hit is None:
        return None

    p = ray.at(t_hit)
    n = (p - center).normalized()
    return Hit(t=t_hit, point=p, normal=n, material_name=material_name)


def intersect_plane(ray, point, normal, material_name, t_min, t_max, bounds_xz=None):
    denom = normal.dot(ray.direction)
    if abs(denom) < 1e-8:
        return None

    t = (point - ray.origin).dot(normal) / denom
    if not (t_min < t < t_max):
        return None

    p = ray.at(t)

    if bounds_xz is not None:
        cx, cz = bounds_xz["center"]
        hx, hz = bounds_xz["half_size"]
        if not (cx - hx <= p.x <= cx + hx and cz - hz <= p.z <= cz + hz):
            return None

    n = normal.normalized()
    return Hit(t=t, point=p, normal=n, material_name=material_name)

