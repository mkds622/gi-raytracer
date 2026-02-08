import yaml
from PIL import Image

from src.math.vec3 import Vec3
from src.core.camera import Camera
from src.core.intersections import intersect_sphere, intersect_plane

def load_config(path="config/scene.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def normalize_scene_config(cfg: dict) -> dict:
    """
    Derive finite-plane bounds from Unity plane parameters when provided.
    Unity Plane is base_size x base_size in XZ at scale (1,1,1).
    """
    for obj in cfg.get("objects", []):
        if obj.get("type") != "plane":
            continue
        if not obj.get("finite", False):
            
            continue
        
        up = obj.get("unity_plane")
        if not up:
            continue
        base = float(up.get("base_size", 10.0))
        sx, _, sz = up["scale"]

        half_wx = (base * float(sx)) / 2.0
        half_dz = (base * float(sz)) / 2.0

        # plane point is [x, y, z] -> bounds center is [x, z]
        px, _, pz = obj["point"]
        obj["bounds_xz"] = {
            "center": [float(px), float(pz)],
            "half_size": [half_wx, half_dz],
        }
    return cfg


def rgb8_tuple(rgb):
    return (int(rgb[0]), int(rgb[1]), int(rgb[2]))


def main():
    cfg = load_config()
    cfg = normalize_scene_config(cfg)

    preset = cfg["render"]["active_preset"]
    res = cfg["render"]["resolution_presets"][preset]
    width, height = int(res["width"]), int(res["height"])
    aspect = width / float(height)

    cam_cfg = cfg["camera"]
    active_cam_preset = cam_cfg["active_camera"]
    active_cam_preset_data = cam_cfg["presets"][active_cam_preset]
    cam = Camera(
        position=Vec3(*active_cam_preset_data["position"]),
        look_at=Vec3(*active_cam_preset_data["look_at"]),
        up=Vec3(*cam_cfg.get("up", [0.0, 1.0, 0.0])),
        fov_y_degrees=float(cam_cfg["fov_y_degrees"]),
        aspect=aspect,
        focal_distance=float(cam_cfg.get("focal_distance", 1.0)),
    )

    bg_rgb = rgb8_tuple(cfg["background"]["color_rgb8"])

    # Material lookup
    mats = cfg["materials"]

    img = Image.new("RGB", (width, height), bg_rgb)
    pix = img.load()

    objects = cfg["objects"]

    # Rendering params
    t_min = 1e-4
    t_max = 1e30

    for j in range(height):
        # v in [-1,1], top to bottom
        v = 1.0 - 2.0 * (j + 0.5) / height
        for i in range(width):
            u = -1.0 + 2.0 * (i + 0.5) / width

            ray = cam.generate_ray(u, v)

            closest_t = t_max
            hit_material = None

            # Intersections (flat color)
            for obj in objects:
                if obj["type"] == "sphere":
                    hit = intersect_sphere(
                        ray=ray,
                        center=Vec3(*obj["center"]),
                        radius=float(obj["radius"]),
                        material_name=obj["material"],
                        t_min=t_min,
                        t_max=closest_t,
                    )
                elif obj["type"] == "plane":
                    hit = intersect_plane(
                        ray=ray,
                        point=Vec3(*obj["point"]),
                        normal=Vec3(*obj["normal"]),
                        material_name=obj["material"],
                        t_min=t_min,
                        t_max=closest_t,
                        bounds_xz=obj.get("bounds_xz") if obj.get("finite", False) else None
                    )
                else:
                    hit = None

                if hit and hit.t < closest_t:
                    closest_t = hit.t
                    hit_material = hit.material_name

            if hit_material is None:
                pix[i, j] = bg_rgb
            else:
                albedo = mats[hit_material]["albedo_rgb8"]
                pix[i, j] = rgb8_tuple(albedo)

    out_path = "outputs/checkpoint2.png"
    img.save(out_path)
    print(f"Saved: {out_path} ({width}x{height})")


if __name__ == "__main__":
    main()
