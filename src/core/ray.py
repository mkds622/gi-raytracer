from __future__ import annotations
from dataclasses import dataclass
from src.math.vec3 import Vec3


@dataclass(frozen=True)
class Ray:
    origin: Vec3
    direction: Vec3  # expected normalized

    def at(self, t: float) -> Vec3:
        return self.origin + self.direction * t
