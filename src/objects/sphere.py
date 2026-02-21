from __future__ import annotations
from typing import Optional
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.core.intersections import Hit
from src.objects.base import Object


class Sphere(Object):
    def __init__(self, center: Vec3, radius: float, material_name: str):
        super().__init__(material_name)
        self.center = center
        self.radius = radius

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b * b - 4.0 * a * c
        if disc < 0.0:
            return None

        sqrt_disc = disc ** 0.5
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
        n = (p - self.center).normalized()
        return Hit(t=t_hit, point=p, normal=n, material_name=self.material_name)