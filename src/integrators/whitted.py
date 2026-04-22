from src.math.vec3 import Vec3
from src.core.ray import Ray
from src.textures.texture_dispatcher import apply_texture
from src.shaders.shader_dispatcher import shade
import math


class WhittedIntegrator:
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
        mat_cfg = materials[hit.material_name]
        mat_cfg = apply_texture(mat_cfg, hit_point=hit.point, obj=obj)

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

        # Reflection
        kr = mat_cfg.get("kr", 0.0)

        if depth < max_depth and kr > 0.0:
            I = ray.direction.normalized()
            R = I - N * 2.0 * I.dot(N)

            eps = 1e-4
            reflect_origin = P + N * eps
            reflect_ray = Ray(reflect_origin, R.normalized())

            reflected_color = self.illuminate(
                reflect_ray, depth + 1,
                world, materials, background_rgb8, ambient_light, lights, max_depth
            )

            rgb = rgb + reflected_color * kr
        
        # Transmission (Refraction)
        kt = mat_cfg.get("kt", 0.0)
        ior = obj.__dict__.get("ior", 1.0)

        if depth < max_depth and kt > 0.0:
            I = ray.direction.normalized()
            
            # Default to Entering (Air to Glass)
            eta = 1.0 / ior
            Nn = N
            if I.dot(N) > 0: 
                # WE ARE EXITING (Glass to Air)
                eta = ior
                Nn = -N
            cos_i = -I.dot(Nn)
            # else:
            #     # WE ARE ENTERING
            #     cos_i = -cos_i

            # Standard Snell's Law components
            k = 1.0 - eta * eta * (1.0 - cos_i * cos_i)
            
            if k < 0:
                # Total Internal Reflection
                refract_dir = (I - Nn * 2.0 * I.dot(Nn)).normalized()
                # Push back INSIDE
                # refract_origin = P + Nn * 1e-3 
            else:
                # Refraction
                refract_dir = ((I * eta) + Nn * (eta * cos_i - math.sqrt(k))).normalized()
                # Push THROUGH the surface
                # refract_origin = P - Nn * 1e-3 
            
            refract_origin = P - Nn * 1e-4

            refract_ray = Ray(refract_origin, refract_dir)
            refracted_color = self.illuminate(
                refract_ray, depth + 1,
                world, materials, background_rgb8, ambient_light, lights, max_depth
            )
            rgb = rgb + refracted_color * kt

        return rgb