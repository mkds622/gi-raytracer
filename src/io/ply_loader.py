from __future__ import annotations
from plyfile import PlyData
from src.math.vec3 import Vec3
from src.objects.triangle import Triangle


def load_ply_triangles(
    path: str,
    material_name: str,
    normalize: bool = True,
    scale: float = 1.0,
    translate: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    ply = PlyData.read(path)

    verts = [Vec3(float(v["x"]), float(v["y"]), float(v["z"])) for v in ply["vertex"]]
    faces = [list(f["vertex_indices"]) for f in ply["face"]]

    if normalize:
        min_x = min(v.x for v in verts); max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts); max_y = max(v.y for v in verts)
        min_z = min(v.z for v in verts); max_z = max(v.z for v in verts)

        cx = (min_x + max_x) * 0.5
        cy = (min_y + max_y) * 0.5
        cz = (min_z + max_z) * 0.5
        extent = max(max_x - min_x, max_y - min_y, max_z - min_z)
        inv = 1.0 / extent if extent > 0 else 1.0

        verts = [
            Vec3((v.x - cx) * inv, (v.y - cy) * inv, (v.z - cz) * inv)
            for v in verts
        ]

    tx, ty, tz = translate
    verts = [Vec3(v.x * scale + tx, v.y * scale + ty, v.z * scale + tz) for v in verts]

    triangles = []
    for f in faces:
        if len(f) < 3:
            continue
        # fan triangulation if needed
        for i in range(1, len(f) - 1):
            triangles.append(
                Triangle(
                    verts[f[0]],
                    verts[f[i]],
                    verts[f[i + 1]],
                    material_name,
                )
            )
    return triangles