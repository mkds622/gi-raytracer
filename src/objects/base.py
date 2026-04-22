from __future__ import annotations
from typing import Optional
from src.core.ray import Ray
from src.core.intersections import Hit


class Object:
    def __init__(self, material_name: str, ior: float):
        self.material_name = material_name
        self.ior = ior

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        raise NotImplementedError