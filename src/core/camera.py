from __future__ import annotations
import math
from dataclasses import dataclass
from src.math.vec3 import Vec3
from src.core.ray import Ray


@dataclass(frozen=True)
class Camera:
    position: Vec3
    look_at: Vec3
    up: Vec3
    fov_y_degrees: float
    aspect: float
    focal_distance: float = 1.0

    def _basis(self) -> tuple[Vec3, Vec3, Vec3]:
        # Unity-like world axes, but we define basis explicitly:
        # forward points from camera to look_at
        forward = (self.look_at - self.position).normalized()
        right   = self.up.cross(forward).normalized()
        true_up = forward.cross(right).normalized()
        return right, true_up, forward

    def generate_ray(self, u: float, v: float) -> Ray:
        """
        u, v in [-1, +1] where:
          u=-1 left, u=+1 right
          v=-1 bottom, v=+1 top
        """
        right, up, forward = self._basis()

        fov_y = math.radians(self.fov_y_degrees)
        half_h = math.tan(fov_y / 2.0) * self.focal_distance
        half_w = half_h * self.aspect

        # Point on virtual screen
        direction = (forward * self.focal_distance) + (right * (u * half_w)) + (up * (v * half_h))
        return Ray(self.position, direction.normalized())
    
    def render(self, world, width, height, materials, background_rgb8):
        from PIL import Image

        img = Image.new("RGB", (width, height), background_rgb8)
        pix = img.load()

        t_min = 1e-4
        t_max = 1e30

        for j in range(height):
            v = 1.0 - 2.0 * (j + 0.5) / height
            for i in range(width):
                u = -1.0 + 2.0 * (i + 0.5) / width

                ray = self.generate_ray(u, v)
                hit = world.intersect(ray, t_min, t_max)

                if hit is None:
                    pix[i, j] = background_rgb8
                else:
                    albedo = materials[hit.material_name]["albedo_rgb8"]
                    pix[i, j] = (int(albedo[0]), int(albedo[1]), int(albedo[2]))

        return img
