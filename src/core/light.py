from __future__ import annotations
from dataclasses import dataclass
from src.math.vec3 import Vec3


@dataclass(frozen=True)
class PointLight:
    position: Vec3
    color: Vec3  # radiance in 0–1 range
    intensity: float
    range: float