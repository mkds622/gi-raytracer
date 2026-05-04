from __future__ import annotations
import math
import random
from dataclasses import dataclass
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.shaders.phong import PhongMaterial, shade_phong
from src.shaders.shader_dispatcher import shade
from src.textures.texture_dispatcher import apply_texture
from src.tone_reproduction.dispatcher import apply_tone_reproduction


@dataclass(frozen=True)
class Camera:
    position: Vec3
    look_at: Vec3
    up: Vec3
    fov_y_degrees: float
    aspect: float
    focal_distance: float = 1.0

    def _clamp01(self, x: float) -> float:
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    def _vec3_to_rgb8(self, c: Vec3) -> tuple[int, int, int]:
        return (
            int(round(self._clamp01(c.x) * 255)),
            int(round(self._clamp01(c.y) * 255)),
            int(round(self._clamp01(c.z) * 255)),
        )

    def _basis(self) -> tuple[Vec3, Vec3, Vec3]:
        # Unity-like world axes, but we define basis explicitly:
        # forward points from camera to look_at
        forward = (self.look_at - self.position).normalized()
        right = self.up.cross(forward).normalized()
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
        direction = (forward * self.focal_distance) + \
            (right * (u * half_w)) + (up * (v * half_h))
        return Ray(self.position, direction.normalized())

    def render(self, world, width, height, materials, background_rgb8, ambient_light, lights, max_depth, integrator, samples_per_pixel, operator=None, Ldmax=1.0, tone_cfg= {}):
        from PIL import Image

        img = Image.new("RGB", (width, height), background_rgb8)
        pix = img.load()

        # sampling buffer
        buffer = [[Vec3(0.0, 0.0, 0.0) for _ in range(width)]
                  for _ in range(height)]

        t_min = 1e-4
        t_max = 1e30

        for j in range(height):
            v = 1.0 - 2.0 * (j + 0.5) / height
            for i in range(width):
                u = -1.0 + 2.0 * (i + 0.5) / width

                color = Vec3(0.0, 0.0, 0.0)

                for s in range(samples_per_pixel):
                    # jitter inside pixel
                    u_jitter = -1.0 + 2.0 * ((i + random.random()) / width)
                    v_jitter = 1.0 - 2.0 * ((j + random.random()) / height)

                    ray = self.generate_ray(u_jitter, v_jitter)

                    color = color + integrator.illuminate(
                        ray, 1, world, materials, background_rgb8, ambient_light, lights, max_depth
                    )

                color = color * (1.0 / samples_per_pixel)

                buffer[j][i] = color

        mapped_buffer = apply_tone_reproduction(buffer, operator, Ldmax, tone_cfg)

        for j in range(height):
            for i in range(width):
                c = mapped_buffer[j][i]

                pix[i, j] = self._vec3_to_rgb8(c)
        return img    
