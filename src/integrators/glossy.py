from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.textures.texture_dispatcher import apply_texture
from src.shaders.shader_dispatcher import shade

import random
import math


class GlossyIntegrator:
    def illuminate(self, ray, depth, world, materials, background_rgb8, ambient_light, lights, max_depth):
        t_min = 1e-4
        t_max = 1e30

        result = world.intersect(ray, t_min, t_max)

        if result is None:
            return Vec3(
                background_rgb8[0] / 255.0,
                background_rgb8[1] / 255.0,
                background_rgb8[2] / 255.0,
            )

        hit, obj = result

        # TODO: support multiple lights, for now we just take the first one
        light = lights[0]
        mat_cfg = materials[hit.material_name].copy()
        mat_cfg = apply_texture(mat_cfg, hit_point=hit.point, obj=obj)

        P = hit.point
        N = hit.normal.normalized()
        V = (-ray.direction).normalized()   # hit -> camera

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
        light_rgb = Vec3(0.0, 0.0, 0.0) if in_shadow else (light.color * light.intensity)

        rgb = shade(
            material_cfg=mat_cfg,
            ambient_light_rgb=ambient_light,
            light_pos=light.position,
            light_rgb=light_rgb,
            hit_point=P,
            normal=N,
            view_dir=V,
        )

        # Reflection
        kr = mat_cfg.get("kr", 0.0)

        if depth < max_depth and kr > 0.0:
            I = ray.direction.normalized()
            R = I - N * 2.0 * I.dot(N)

            num_samples = 16  # You can adjust this for better quality/performance tradeoff
            accum = Vec3(0.0, 0.0, 0.0)

            for _ in range(num_samples):
                # Sample around reflection direction (Phong lobe)
                phi = 2 * math.pi * random.random()
                cos_theta = random.random() ** (1.0 / (mat_cfg.get("ke", 32)))
                sin_theta = math.sqrt(1 - cos_theta * cos_theta)

                # Build orthonormal basis around R
                w = R.normalized()
                u = Vec3(0.0, 1.0, 0.0).cross(w)
                if u.length() < 1e-3:
                    u = Vec3(1.0, 0.0, 0.0).cross(w)
                u = u.normalized()
                v = w.cross(u)

                # Sample direction
                dir_sample = (
                    u * (math.cos(phi) * sin_theta) +
                    v * (math.sin(phi) * sin_theta) +
                    w * cos_theta
                ).normalized()

                reflect_origin = P + N * eps
                reflect_ray = Ray(reflect_origin, dir_sample)

                accum += self.illuminate(
                    reflect_ray, depth + 1,
                    world, materials, background_rgb8, ambient_light, lights, max_depth
                )

            rgb = rgb + kr * (accum * (1.0 / num_samples))
        
        #TODO: Implement refraction for glossy, and add shadow attenuation instead of killing light

        return rgb