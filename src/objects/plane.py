from __future__ import annotations
from typing import Optional
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.objects.base import Hit, Object

class Plane(Object):
    def __init__(
        self,
        point: Vec3,
        normal: Vec3,
        material_name: str,
        cam_pos: Vec3 | None = None,
        cam_right: Vec3 | None = None,
        cam_forward: Vec3 | None = None,
        cam_bounds: dict | None = None,
    ):
        super().__init__(material_name)
        self.point = point
        self.normal = normal.normalized()

        # optional camera-relative clipping (your working fix)
        self.cam_pos = cam_pos
        self.cam_right = cam_right
        self.cam_forward = cam_forward
        self.cam_bounds = cam_bounds

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-8:
            return None

        t = (self.point - ray.origin).dot(self.normal) / denom
        if not (t_min < t < t_max):
            return None

        p = ray.at(t)

        # camera-relative finite floor
        if self.cam_bounds is not None:
            v = p - self.cam_pos
            r = v.dot(self.cam_right)
            f = v.dot(self.cam_forward)

            if not (self.cam_bounds["right_min"] <= r <= self.cam_bounds["right_max"] and
                    self.cam_bounds["forward_min"] <= f <= self.cam_bounds["forward_max"]):
                return None

        return Hit(t=t, point=p, normal=self.normal, material_name=self.material_name)