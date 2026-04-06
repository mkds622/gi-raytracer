from __future__ import annotations
from typing import Optional
from src.core.ray import Ray
from src.core.intersections import Hit
from src.objects.base import Object


class World:
    def __init__(self):
        self.objects: list[Object] = []

    def add(self, obj: Object):
        self.objects.append(obj)

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        closest_hit = None
        closest_obj = None
        closest_t = t_max

        for obj in self.objects:
            hit = obj.intersect(ray, t_min, closest_t)
            if hit and hit.t < closest_t:
                closest_t = hit.t
                closest_hit = hit
                closest_obj = obj

        if closest_hit is None:
            return None        
        
        return closest_hit, closest_obj