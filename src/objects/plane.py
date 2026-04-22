from __future__ import annotations
from typing import Optional
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.core.intersections import Hit
from src.objects.base import Object

class Plane(Object):
    def __init__(
        self,
        point: Vec3,
        normal: Vec3,
        material_name: str,
        ior: float,
        bounds_xz: dict | None = None,
    ):
        super().__init__(material_name, ior)
        self.point = point
        self.normal = normal.normalized()
        self.bounds_xz = bounds_xz

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-8:
            return None

        t = (self.point - ray.origin).dot(self.normal) / denom
        if not (t_min < t < t_max):
            return None

        p = ray.at(t)

        if self.bounds_xz is not None:
            cx, cz = self.bounds_xz["center"]
            hx, hz = self.bounds_xz["half_size"]
            if not (cx - hx <= p.x <= cx + hx and cz - hz <= p.z <= cz + hz):
                return None

        return Hit(t=t, point=p, normal=self.normal, material_name=self.material_name)
    
    def get_uv(self, P):
        local = P - self.point
        return local.x, local.z