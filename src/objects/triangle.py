from __future__ import annotations
from typing import Optional
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.core.intersections import Hit
from src.objects.base import Object


class Triangle(Object):
    def __init__(self, v0: Vec3, v1: Vec3, v2: Vec3, material_name: str):
        super().__init__(material_name)
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.e1 = self.v1 - self.v0
        self.e2 = self.v2 - self.v0
        self.normal = self.e1.cross(self.e2).normalized()

    def centroid(self) -> Vec3:
        return (self.v0 + self.v1 + self.v2) / 3.0

    def bbox(self) -> tuple[Vec3, Vec3]:
        min_v = Vec3(
            min(self.v0.x, self.v1.x, self.v2.x),
            min(self.v0.y, self.v1.y, self.v2.y),
            min(self.v0.z, self.v1.z, self.v2.z),
        )
        max_v = Vec3(
            max(self.v0.x, self.v1.x, self.v2.x),
            max(self.v0.y, self.v1.y, self.v2.y),
            max(self.v0.z, self.v1.z, self.v2.z),
        )
        return min_v, max_v

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        eps = 1e-8

        pvec = ray.direction.cross(self.e2)
        det = self.e1.dot(pvec)

        if abs(det) < eps:
            return None

        inv_det = 1.0 / det
        tvec = ray.origin - self.v0
        u = tvec.dot(pvec) * inv_det
        if u < 0.0 or u > 1.0:
            return None

        qvec = tvec.cross(self.e1)
        v = ray.direction.dot(qvec) * inv_det
        if v < 0.0 or (u + v) > 1.0:
            return None

        t = self.e2.dot(qvec) * inv_det
        if not (t_min < t < t_max):
            return None

        p = ray.at(t)
        return Hit(t=t, point=p, normal=self.normal, material_name=self.material_name)