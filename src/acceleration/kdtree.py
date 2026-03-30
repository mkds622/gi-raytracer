from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from src.math.vec3 import Vec3
from src.core.intersections import Hit


def _axis_name(axis: int) -> str:
    return ("x", "y", "z")[axis]


@dataclass
class AABB:
    min_v: Vec3
    max_v: Vec3

    def union(self, other: "AABB") -> "AABB":
        return AABB(
            Vec3(
                min(self.min_v.x, other.min_v.x),
                min(self.min_v.y, other.min_v.y),
                min(self.min_v.z, other.min_v.z),
            ),
            Vec3(
                max(self.max_v.x, other.max_v.x),
                max(self.max_v.y, other.max_v.y),
                max(self.max_v.z, other.max_v.z),
            ),
        )

    def hit(self, ray, t_min: float, t_max: float) -> tuple[bool, float]:
        t0 = t_min
        t1 = t_max

        for axis in ("x", "y", "z"):
            origin = getattr(ray.origin, axis)
            direction = getattr(ray.direction, axis)
            mn = getattr(self.min_v, axis)
            mx = getattr(self.max_v, axis)

            if abs(direction) < 1e-12:
                if origin < mn or origin > mx:
                    return False, t_min
                continue

            inv_d = 1.0 / direction
            t_near = (mn - origin) * inv_d
            t_far = (mx - origin) * inv_d
            if t_near > t_far:
                t_near, t_far = t_far, t_near

            t0 = max(t0, t_near)
            t1 = min(t1, t_far)
            if t1 < t0:
                return False, t0

        return True, t0


@dataclass
class KDNode:
    bbox: AABB
    left: Optional["KDNode"] = None
    right: Optional["KDNode"] = None
    triangles: Optional[list] = None
    axis: int = 0
    split: float = 0.0

    @property
    def is_leaf(self) -> bool:
        return self.triangles is not None


def _triangles_bbox(triangles) -> AABB:
    first_min, first_max = triangles[0].bbox()
    box = AABB(first_min, first_max)
    for tri in triangles[1:]:
        mn, mx = tri.bbox()
        box = box.union(AABB(mn, mx))
    return box


def _centroid_bbox(triangles) -> AABB:
    cs = [t.centroid() for t in triangles]
    min_v = Vec3(min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))
    max_v = Vec3(max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs))
    return AABB(min_v, max_v)


class KDTree:
    def __init__(self, triangles, max_tris_per_leaf: int = 8, max_depth: int = 32):
        self.max_tris_per_leaf = max_tris_per_leaf
        self.max_depth = max_depth
        self.root = self._build(triangles, 0)

    def _build(self, triangles, depth: int) -> KDNode:
        bbox = _triangles_bbox(triangles)

        if len(triangles) <= self.max_tris_per_leaf or depth >= self.max_depth:
            return KDNode(bbox=bbox, triangles=triangles)

        cbox = _centroid_bbox(triangles)
        extents = (
            cbox.max_v.x - cbox.min_v.x,
            cbox.max_v.y - cbox.min_v.y,
            cbox.max_v.z - cbox.min_v.z,
        )
        axis = extents.index(max(extents))

        cents = [getattr(t.centroid(), _axis_name(axis)) for t in triangles]
        split = sorted(cents)[len(cents) // 2]

        left_tris = []
        right_tris = []
        for t in triangles:
            c = getattr(t.centroid(), _axis_name(axis))
            if c <= split:
                left_tris.append(t)
            else:
                right_tris.append(t)

        if len(left_tris) == 0 or len(right_tris) == 0:
            return KDNode(bbox=bbox, triangles=triangles)

        left = self._build(left_tris, depth + 1)
        right = self._build(right_tris, depth + 1)
        return KDNode(bbox=bbox, left=left, right=right, axis=axis, split=split)

    def intersect(self, ray, t_min: float, t_max: float) -> Optional[Hit]:
        return self._intersect_node(self.root, ray, t_min, t_max)

    def _intersect_node(self, node: KDNode, ray, t_min: float, t_max: float) -> Optional[Hit]:
        ok, entry = node.bbox.hit(ray, t_min, t_max)
        if not ok:
            return None

        if node.is_leaf:
            closest = None
            closest_t = t_max
            for tri in node.triangles:
                hit = tri.intersect(ray, t_min, closest_t)
                if hit and hit.t < closest_t:
                    closest_t = hit.t
                    closest = hit
            return closest

        candidates = []
        for child in (node.left, node.right):
            if child is None:
                continue
            ok, entry = child.bbox.hit(ray, t_min, t_max)
            if ok:
                candidates.append((entry, child))

        candidates.sort(key=lambda x: x[0])

        closest = None
        closest_t = t_max
        for _, child in candidates:
            hit = self._intersect_node(child, ray, t_min, closest_t)
            if hit and hit.t < closest_t:
                closest_t = hit.t
                closest = hit

        return closest


class KDWorld:
    def __init__(self, tree: KDTree):
        self.tree = tree

    def intersect(self, ray, t_min: float, t_max: float):
        return self.tree.intersect(ray, t_min, t_max)