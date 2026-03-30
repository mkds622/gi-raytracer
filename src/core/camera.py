from __future__ import annotations
import math
from dataclasses import dataclass
from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.shaders.phong import PhongMaterial, shade_phong
from src.shaders.shader_dispatcher import shade


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
    
    def render(self, world, width, height, materials, background_rgb8, ambient_light, lights):
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

                    light = lights[0]
                    mat_cfg = materials[hit.material_name]

                    P = hit.point
                    N = hit.normal.normalized()
                    V = (-ray.direction).normalized()  # hit -> camera

                    # Shadow ray: hit point -> light
                    to_light = light.position - P
                    light_dist = to_light.length()
                    Sdir = to_light.normalized()

                    eps = 1e-4
                    shadow_origin = P + N * eps
                    shadow_ray = Ray(shadow_origin, Sdir)

                    shadow_hit = world.intersect(shadow_ray, t_min=eps, t_max=light_dist - eps)
                    in_shadow = shadow_hit is not None

                    # If in shadow: only ambient (we do this by zeroing light contribution)
                    light_rgb = Vec3(0.0, 0.0, 0.0) if in_shadow else light.color

                    rgb = shade(
                        material_cfg=mat_cfg,
                        ambient_light_rgb=ambient_light,
                        light_pos=light.position,
                        light_rgb=light_rgb,
                        hit_point=P,
                        normal=N,
                        view_dir=V,
                    )

                    pix[i, j] = self._vec3_to_rgb8(rgb)

        return img
