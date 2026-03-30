import time
import yaml

from src.math.vec3 import Vec3
from src.core.camera import Camera
from src.core.light import PointLight
from src.core.world import World
from src.io.ply_loader import load_ply_triangles
from src.acceleration.kdtree import KDTree, KDWorld


def load_config(path="config/bunny.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def rgb8_tuple(rgb):
    return (int(rgb[0]), int(rgb[1]), int(rgb[2]))


def main():
    cfg = load_config()

    # resolution
    preset = cfg["render"]["active_preset"]
    res = cfg["render"]["resolution_presets"][preset]
    width, height = int(res["width"]), int(res["height"])
    aspect = width / float(height)

    # camera
    cam_cfg = cfg["camera"]
    active = cam_cfg["active_camera"]
    cam_data = cam_cfg["presets"][active]
    cam = Camera(
        position=Vec3(*cam_data["position"]),
        look_at=Vec3(*cam_data["look_at"]),
        up=Vec3(*cam_cfg.get("up", [0.0, 1.0, 0.0])),
        fov_y_degrees=float(cam_cfg["fov_y_degrees"]),
        aspect=aspect,
        focal_distance=float(cam_cfg.get("focal_distance", 1.0)),
    )

    # world/light/materials
    ambient_light = Vec3(*cfg["world"]["ambient_light_rgb"])
    bg_rgb = rgb8_tuple(cfg["background"]["color_rgb8"])
    materials = cfg["materials"]

    lights = []
    for l in cfg["lights"]:
        if l["type"] == "point":
            lights.append(
                PointLight(
                    position=Vec3(*l["position"]),
                    color=Vec3(*l["color_rgb"]),
                )
            )

    # load mesh
    mesh_cfg = cfg["mesh"]
    triangles = load_ply_triangles(
        path=mesh_cfg["path"],
        material_name=mesh_cfg["material"],
        normalize=bool(mesh_cfg.get("normalize", True)),
        scale=float(mesh_cfg.get("scale", 1.0)),
        translate=tuple(mesh_cfg.get("translate", [0.0, 0.0, 0.0])),
    )
    print(f"Loaded triangles: {len(triangles)}")

    # brute force world
    brute_world = World()
    for tri in triangles:
        brute_world.add(tri)

    # brute force render
    run_bruteforce = bool(cfg["kdtree"].get("run_bruteforce", True))
    if run_bruteforce:
        t0 = time.perf_counter()
        brute_img = cam.render(
            world=brute_world,
            width=width,
            height=height,
            materials=materials,
            background_rgb8=bg_rgb,
            ambient_light=ambient_light,
            lights=lights,
        )
        brute_render_time = time.perf_counter() - t0
        brute_img.save("outputs/bunny_bruteforce.png")
        print(f"Brute render time: {brute_render_time:.3f}s")
    else:
        brute_render_time = None
        print("Brute render time: TOO LONG / SKIPPED")

    # build kdtree
    t0 = time.perf_counter()
    tree = KDTree(
        triangles,
        max_tris_per_leaf=int(cfg["kdtree"].get("max_tris_per_leaf", 8)),
        max_depth=int(cfg["kdtree"].get("max_depth", 32)),
    )
    build_time = time.perf_counter() - t0
    print(f"KD build time: {build_time:.3f}s")

    kd_world = KDWorld(tree)

    # kd render
    t0 = time.perf_counter()
    kd_img = cam.render(
        world=kd_world,
        width=width,
        height=height,
        materials=materials,
        background_rgb8=bg_rgb,
        ambient_light=ambient_light,
        lights=lights,
    )
    kd_render_time = time.perf_counter() - t0
    kd_img.save("outputs/bunny_kdtree.png")
    print(f"KD render time: {kd_render_time:.3f}s")

    print("---- Summary ----")
    print(f"KD build:   {build_time:.3f}s")
    print(f"KD render:  {kd_render_time:.3f}s")
    if brute_render_time is None:
        print("Brute force render: TOO LONG / SKIPPED")
    else:
        print(f"Brute force render: {brute_render_time:.3f}s")


if __name__ == "__main__":
    main()