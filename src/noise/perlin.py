import math
import random

perm = list(range(256))
random.shuffle(perm)
perm += perm


def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(a, b, t):
    return a + t * (b - a)


def grad(hash, x, y, z):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in [12, 14] else z)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


def perlin(x, y, z):
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255

    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)

    u = fade(xf)
    v = fade(yf)
    w = fade(zf)

    aaa = perm[perm[perm[xi] + yi] + zi]
    aba = perm[perm[perm[xi] + yi + 1] + zi]
    aab = perm[perm[perm[xi] + yi] + zi + 1]
    abb = perm[perm[perm[xi] + yi + 1] + zi + 1]
    baa = perm[perm[perm[xi + 1] + yi] + zi]
    bba = perm[perm[perm[xi + 1] + yi + 1] + zi]
    bab = perm[perm[perm[xi + 1] + yi] + zi + 1]
    bbb = perm[perm[perm[xi + 1] + yi + 1] + zi + 1]

    x1 = lerp(grad(aaa, xf, yf, zf), grad(baa, xf - 1, yf, zf), u)
    x2 = lerp(grad(aba, xf, yf - 1, zf), grad(bba, xf - 1, yf - 1, zf), u)
    y1 = lerp(x1, x2, v)

    x3 = lerp(grad(aab, xf, yf, zf - 1), grad(bab, xf - 1, yf, zf - 1), u)
    x4 = lerp(grad(abb, xf, yf - 1, zf - 1), grad(bbb, xf - 1, yf - 1, zf - 1), u)
    y2 = lerp(x3, x4, v)

    return (lerp(y1, y2, w) + 1) * 0.5  # [0,1]