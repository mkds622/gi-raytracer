from __future__ import annotations
from typing import Optional
from src.core.ray import Ray
from src.objects.base import Hit, Object

class World:
    def __init__(self) -> None:
        self.objects: list[Object] = []

    def add(self, obj: Object) -> None:
        self.objects.append(obj)

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        closest: Optional[Hit] = None
        closest_t = t_max

        for obj in self.objects:
            hit = obj.intersect(ray, t_min, closest_t)
            if hit is not None and hit.t < closest_t:
                closest_t = hit.t
                closest = hit

        return closest