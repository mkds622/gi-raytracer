import yaml
from PIL import Image

from src.math.vec3 import Vec3
from src.core.camera import Camera
from src.core.world import World
from src.objects.sphere import Sphere
from src.objects.plane import Plane
from src.core.light import PointLight


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

    # Resolution
    preset = cfg["render"]["active_preset"]
    res = cfg["render"]["resolution_presets"][preset]
    width, height = int(res["width"]), int(res["height"])
    aspect = width / float(height)

    # Camera
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

    # Background
    bg_rgb = rgb8_tuple(cfg["background"]["color_rgb8"])

    # Materials
    mats = cfg["materials"]

    ambient_light = Vec3(*cfg["world"]["ambient_light_rgb"])

    # Parse lights
    lights = []
    for l in cfg["lights"]:
        if l["type"] == "point":
            lights.append(
                PointLight(
                    position=Vec3(*l["position"]),
                    color=Vec3(*l["color_rgb"]),
                )
            )
    

    # Build World
    world = World()

    for obj in cfg["objects"]:
        if obj["type"] == "sphere":
            world.add(
                Sphere(
                    center=Vec3(*obj["center"]),
                    radius=float(obj["radius"]),
                    material_name=obj["material"],
                )
            )

        elif obj["type"] == "plane":
            world.add(
                Plane(
                    point=Vec3(*obj["point"]),
                    normal=Vec3(*obj["normal"]),
                    material_name=obj["material"],
                    bounds_xz=obj.get("bounds_xz")
                    if obj.get("finite", False)
                    else None,
                )
            )

    img = cam.render(
        world=world,
        width=width,
        height=height,
        materials=mats,
        background_rgb8=bg_rgb,
        ambient_light=ambient_light,
        lights=lights,
    )

    out_path = "outputs/checkpoint3(AshikhminShirley).png"
    img.save(out_path)
    print(f"Saved: {out_path} ({width}x{height})")


if __name__ == "__main__":
    main()
