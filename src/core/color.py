from __future__ import annotations
from dataclasses import dataclass

def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float

    @staticmethod
    def from_rgb8(r: int, g: int, b: int) -> "Color":
        return Color(r / 255.0, g / 255.0, b / 255.0)

    def to_rgb8(self) -> tuple[int, int, int]:
        rr = int(round(_clamp01(self.r) * 255))
        gg = int(round(_clamp01(self.g) * 255))
        bb = int(round(_clamp01(self.b) * 255))
        return rr, gg, bb