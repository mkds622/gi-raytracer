from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from src.core.ray import Ray

@dataclass(frozen=True)
class Hit:
    t: float
    point: "Vec3"
    normal: "Vec3"
    material_name: str

class Object:
    def __init__(self, material_name: str):
        self.material_name = material_name

    def intersect(self, ray: Ray, t_min: float, t_max: float) -> Optional[Hit]:
        raise NotImplementedError