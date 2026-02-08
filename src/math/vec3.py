from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Union

Number = Union[int, float]


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, s: Number) -> "Vec3":
        return Vec3(self.x * float(s), self.y * float(s), self.z * float(s))

    def __rmul__(self, s: Number) -> "Vec3":
        return self.__mul__(s)

    def __truediv__(self, s: Number) -> "Vec3":
        s = float(s)
        if s == 0.0:
            raise ZeroDivisionError("Vec3 division by zero")
        inv = 1.0 / s
        return Vec3(self.x * inv, self.y * inv, self.z * inv)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def normalized(self) -> "Vec3":
        L = self.length()
        if L == 0.0:
            return Vec3(0.0, 0.0, 0.0)
        return self / L

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)
