#!/usr/bin/env python3
"""Paints the watercolour lighthouse scene used by index.html.

    python3 tools/paint-scene.py          # writes art/*.webp

Needs numpy, scipy and Pillow. It is seeded, so it paints the same picture every run.
Every position is in the page's scene units: the lantern sits at (800, 236) and the
horizon at y = 470, the same numbers the page script uses to frame the camera.

The washes follow Tyler Hobbs' approach: a shape is roughened by recursive midpoint
displacement, then painted as dozens of see-through layers, each roughened a little
differently and broken up by a blotchy texture. Edges are darkened where pigment pools.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'art')
os.makedirs(OUT, exist_ok=True)
R = np.random.default_rng(20270210)


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def noise(h, w, sy, sx=None, seed=None):
    r = np.random.default_rng(seed) if seed is not None else R
    n = gaussian_filter(r.standard_normal((h, w)), (sy, sx if sx is not None else sy), mode='wrap')
    return (n - n.mean()) / (n.std() + 1e-9)


class Layer:
    """A transparent sheet covering a rectangle of the scene, at ppu pixels per scene unit."""

    def __init__(self, x0, y0, w, h, ppu):
        self.x0, self.y0, self.ppu = x0, y0, ppu
        self.W, self.H = int(round(w * ppu)), int(round(h * ppu))
        self.P = np.zeros((self.H, self.W, 3))  # premultiplied colour
        self.A = np.zeros((self.H, self.W))
        self._tex = None

    def px(self, pts):
        pts = np.asarray(pts, float)
        return np.stack([(pts[:, 0] - self.x0) * self.ppu, (pts[:, 1] - self.y0) * self.ppu], 1)

    def tex(self):
        if self._tex is None:  # blotchy masks that break up each glaze, like pigment settling unevenly
            self._tex = []
            for k in range(6):
                n = noise(self.H, self.W, 1.6 * self.ppu, seed=100 + k)
                self._tex.append(np.clip(0.55 + 0.45 * n, 0, 1))
        return self._tex

    def over(self, col, a):
        """Lay paint of colour col (HxWx3 or 3) with alpha a on top."""
        col = np.broadcast_to(col, self.P.shape)
        self.P = col * a[..., None] + self.P * (1 - a[..., None])
        self.A = a + self.A * (1 - a)

    def save(self, name, quality=82):
        a = np.clip(self.A, 0, 1)
        rgb = np.where(a[..., None] > 1e-4, self.P / np.maximum(a, 1e-4)[..., None], 0)
        img = np.dstack([np.clip(rgb, 0, 1), a])
        im = Image.fromarray((img * 255 + .5).astype(np.uint8), 'RGBA')
        im.save(os.path.join(OUT, name), 'WEBP', quality=quality, method=6, alpha_quality=90)
        return im


def deform(P, V, depth, r=R):
    """Recursive midpoint displacement. V is each vertex's variance: high gives soft, wandering edges."""
    for _ in range(depth):
        Q, W = np.roll(P, -1, 0), np.roll(V, -1)
        seg = np.linalg.norm(Q - P, axis=1)
        v = (V + W) / 2
        M = (P + Q) / 2 + r.standard_normal(P.shape) * (seg * v * 0.42)[:, None]
        nP = np.empty((len(P) * 2, 2))
        nV = np.empty(len(P) * 2)
        nP[0::2], nP[1::2] = P, M
        nV[0::2], nV[1::2] = V, v * r.uniform(.5, .85, len(v))
        P, V = nP, nV
    return P, V


def ellipse(cx, cy, rx, ry, n=10, rot=0):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(t), ry * np.sin(t)
    c, s = np.cos(rot), np.sin(rot)
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)


def blob_alpha(L, poly, layers=36, alpha=.06, var=.5, base_depth=5, layer_depth=3, tex=.6):
    """The alpha of one watercolour shape, before colour is applied."""
    P = L.px(poly)
    V = np.full(len(P), var) * R.uniform(.7, 1.3, len(P))
    base, bv = deform(P, V, base_depth)
    A = np.zeros((L.H, L.W))
    bank = L.tex()
    for i in range(layers):
        pts, _ = deform(base, bv.copy(), layer_depth)
        x0, y0 = np.floor(pts.min(0)).astype(int) - 2
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 2
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, L.W), min(y1, L.H)
        if x1 <= x0 or y1 <= y0:
            continue
        im = Image.new('L', (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(im).polygon([(float(a - x0), float(b - y0)) for a, b in pts], fill=255)
        m = np.asarray(im, float) / 255
        t = bank[i % len(bank)]
        dy, dx = R.integers(0, L.H), R.integers(0, L.W)
        t = t[np.ix_((np.arange(y0, y1) + dy) % L.H, (np.arange(x0, x1) + dx) % L.W)]
        m *= (1 - tex) + tex * t
        A[y0:y1, x0:x1] = 1 - (1 - A[y0:y1, x0:x1]) * (1 - alpha * m)
    return A


def pooled(L, A, col, col2=None, edge=.35, vary=.5, sigma=2.5, gain=1.0):
    """Colour a shape: variegated between two colours, darker where pigment pools at the edge."""
    s = sigma * L.ppu
    E = np.clip(A - gaussian_filter(A, s), 0, None)
    E /= (np.percentile(E[A > .02], 99) if (A > .02).any() else 1) + 1e-6
    E = np.clip(E, 0, 1)
    c1 = hexc(col)
    if col2 is not None:
        t = np.clip(.5 + vary * .5 * noise(L.H, L.W, 18 * L.ppu), 0, 1)[..., None]
        C = c1 * (1 - t) + hexc(col2) * t
    else:
        C = np.broadcast_to(c1, (L.H, L.W, 3))
    C = C * (1 - edge * E[..., None])
    L.over(C, np.clip(A * gain, 0, 1))


def paint(L, poly, col, col2=None, layers=36, alpha=.06, var=.5, edge=.35, tex=.6, gain=1.0,
          base_depth=5, layer_depth=3, sigma=2.5):
    A = blob_alpha(L, poly, layers, alpha, var, base_depth, layer_depth, tex)
    pooled(L, A, col, col2, edge=edge, sigma=sigma, gain=gain)
    return A


def ink(L, pts, col='#1F2350', width=1.1, alpha=.72, jitter=.5, passes=2):
    """A slightly wandering pen line over the washes."""
    pts = np.asarray(pts, float)
    dense = []
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(2, int(np.linalg.norm(b - a) / 3))
        for t in np.linspace(0, 1, n, endpoint=False):
            dense.append(a + (b - a) * t)
    dense.append(pts[-1])
    dense = np.array(dense)
    acc = np.zeros((L.H, L.W))
    for p in range(passes):
        d = dense + np.cumsum(R.normal(0, jitter * .25, dense.shape), 0) * .4 + R.normal(0, jitter * .3, dense.shape)
        q = L.px(d)
        im = Image.new('L', (L.W, L.H), 0)
        w = max(1, int(round(width * L.ppu * R.uniform(.8, 1.1))))
        ImageDraw.Draw(im).line([tuple(map(float, xy)) for xy in q], fill=255, width=w, joint='curve')
        m = np.asarray(im, float) / 255
        acc = 1 - (1 - acc) * (1 - m * alpha * R.uniform(.7, 1))
    L.over(hexc(col), acc)


def strokes(L, n, region, col, length=(8, 40), thick=(1, 2.5), alpha=(.15, .45), lean=0, ycurve=None, seedcol=None):
    """Many short dry-brush strokes, used for waves and grass."""
    acc = np.zeros((L.H, L.W))
    ccol = np.zeros((L.H, L.W, 3))
    x0, y0, x1, y1 = region
    for _ in range(n):
        x, y = R.uniform(x0, x1), R.uniform(y0, y1)
        if ycurve is not None and y < ycurve(x):
            continue
        ln = R.uniform(*length)
        th = R.uniform(*thick)
        ang = lean + R.normal(0, .06)
        pts = ellipse(x, y, ln / 2, th / 2, 8, ang)
        a = blob_alpha(L, pts, layers=3, alpha=R.uniform(*alpha) / 1.6, var=.35, base_depth=2, layer_depth=1, tex=.4)
        c = hexc(seedcol(x, y) if seedcol else col)
        ccol = ccol * (1 - a[..., None]) + c * a[..., None]
        acc = 1 - (1 - acc) * (1 - a)
    L.over(np.clip(ccol / np.maximum(acc, 1e-4)[..., None], 0, 1), acc)


def ramp(y, stops):
    ys = np.array([s[0] for s in stops], float)
    cs = np.array([hexc(s[1]) for s in stops])
    return np.stack([np.interp(y, ys, cs[:, k]) for k in range(3)], -1)


# ---------------------------------------------------------------------------
# 1. Sky and sea (opaque backdrop). Covers x 30..1050, y -120..980.
# ---------------------------------------------------------------------------
def backdrop():
    L = Layer(30, -120, 1020, 1100, 1.5)
    H, W, p = L.H, L.W, L.ppu
    yy = (np.arange(H)[:, None] / p + L.y0) * np.ones((1, W))
    xx = (np.arange(W)[None, :] / p + L.x0) * np.ones((H, 1))
    hor = 470 + 0.8 * noise(1, W, 1, 14 * p, seed=7)[0]  # a hand-drawn horizon
    sky = ramp(yy, [(-120, '#141947'), (60, '#1E2462'), (200, '#3E3780'), (310, '#73508A'), (390, '#B86C77'),
                    (440, '#E39470'), (470, '#F4BC78')])
    sea = ramp(yy, [(470, '#C7A6A2'), (482, '#9C8AA6'), (520, '#6E7099'), (600, '#465585'), (720, '#2C3D6B'),
                    (980, '#17234A')])
    # The sky glows warmer around the sun.
    sx, sy = 612, 466
    d = np.hypot((xx - sx) / 1.6, yy - sy)
    halo = np.exp(-(d / 150) ** 2)[..., None]
    sky = sky * (1 - .45 * halo) + hexc('#FFC985') * .45 * halo
    seaglow = np.exp(-((xx - sx) / 170) ** 2 - ((yy - 470) / 90) ** 2)[..., None]
    sea = sea * (1 - .3 * seaglow) + hexc('#E6A77C') * .3 * seaglow
    is_sky = (yy < hor[None, :])[..., None]
    C = np.where(is_sky, sky, sea)

    # Watercolour character: broad mottling, brush streaks, a few backruns, granulation.
    C *= (1 + .045 * noise(H, W, 70 * p, seed=11))[..., None]
    streak = noise(H, W, 3.5 * p, 90 * p, seed=12) * np.clip(.6 + .5 * noise(H, W, 60 * p, seed=14), 0, 1.2)
    C *= (1 + np.where(is_sky[..., 0], .022, .045) * streak)[..., None]
    for (bx, by, br) in [(150, 120, 120), (420, 40, 150), (260, 300, 90), (940, 160, 110), (700, 330, 80)]:
        A = blob_alpha(L, ellipse(bx, by, br, br * .6, 9, R.uniform(-.3, .3)), layers=18, alpha=.09, var=.85, tex=.3)
        E = np.clip(A - gaussian_filter(A, 3 * p), 0, None)
        E /= E.max() + 1e-6
        C *= (1 + .05 * A - .16 * E)[..., None]  # paler inside, a darker cauliflower rim
    # Pigment pools along the top of the sea wash.
    band = np.exp(-((yy - hor[None, :] - 1.5) / 1.6) ** 2) * (yy > hor[None, :] - 1)
    C *= (1 - .18 * band)[..., None]
    lum = C.mean(-1)
    g = np.clip(noise(H, W, .7, seed=13), 0, None)
    C *= (1 - .05 * g * (1.2 - lum))[..., None]

    # The sun, half sunk, painted as a soft wet blob.
    S = Layer(L.x0, L.y0, 1020, 1100, p)
    S.P, S.A = np.zeros_like(L.P), np.zeros_like(L.A)
    A = blob_alpha(S, ellipse(sx, sy, 44, 43, 16), layers=50, alpha=.06, var=.14, tex=.3)
    A = gaussian_filter(A, 1.2 * p) * (yy < hor[None, :] + .5)
    A = np.clip(A * 1.15, 0, .97)
    pale = hexc('#FFE7AE') * (1 - .2 * np.clip((yy - 430) / 40, 0, 1))[..., None] + hexc('#F7B46E') * .2 * np.clip((yy - 430) / 40, 0, 1)[..., None]
    C = C * (1 - A[..., None]) + pale * A[..., None]

    L.P, L.A = np.clip(C, 0, 1), np.ones((H, W))
    im = L.save('bg.webp', quality=80)
    return L, hor


# ---------------------------------------------------------------------------
# 2. Clouds: long rose and lavender wisps that drift.
# ---------------------------------------------------------------------------
def cloud(name, length, seed):
    r = np.random.default_rng(seed)
    globals()['R'] = r
    L = Layer(0, 0, length + 80, 90, 1.5)
    cy = 48
    for k in range(5):
        cx = 40 + length * r.uniform(.15, .85)
        rx = length * r.uniform(.18, .4)
        ry = r.uniform(6, 13)
        A = blob_alpha(L, ellipse(cx, cy + r.normal(0, 5), rx, ry, 12), layers=44, alpha=.028, var=.55, tex=.5)
        pooled(L, gaussian_filter(A, .8 * L.ppu), '#E2A3A4', '#C394B4', edge=.3, sigma=2)
    A = blob_alpha(L, ellipse(40 + length * .5, cy + 9, length * .4, 4.5, 12), layers=30, alpha=.03, var=.5, tex=.5)
    pooled(L, gaussian_filter(A, .8 * L.ppu), '#6F5F96', '#8C70A0', edge=.3, sigma=2)  # shadowed underside
    L.save(name)
    globals()['R'] = np.random.default_rng(seed + 500)
    return L


# ---------------------------------------------------------------------------
# 3. Sea strokes (two sheets that bob against each other) and the sun's glitter path.
# ---------------------------------------------------------------------------
def arcs(L, n, region, colfn, length, thick, alpha, sag=.12):
    """Painted wave marks: short, gently curved strokes that taper at both ends."""
    x0, y0, x1, y1 = region
    acc = np.zeros((L.H, L.W))
    cc = np.zeros((L.H, L.W, 3))
    for _ in range(n):
        x, y = R.uniform(x0, x1), R.uniform(y0, y1)
        ln, th = R.uniform(*length), R.uniform(*thick)
        k = np.linspace(-1, 1, 9)
        pts = np.stack([x + k * ln / 2, y + sag * ln * (k ** 2 - 1) * R.choice([-1, 1]) * .5 + R.normal(0, .3, 9)], 1)
        q = L.px(pts)
        im = Image.new('L', (L.W, L.H), 0)
        d = ImageDraw.Draw(im)
        for i in range(len(q) - 1):  # taper: thick in the middle, thin at the ends
            w = max(1, int(round(th * L.ppu * (1 - abs(k[i] + k[i + 1]) / 2) ** .7)))
            d.line([tuple(q[i]), tuple(q[i + 1])], fill=255, width=w)
        m = gaussian_filter(np.asarray(im, float) / 255, .45 * L.ppu) * R.uniform(*alpha)
        cc = cc * (1 - m[..., None]) + hexc(colfn(x, y)) * m[..., None]
        acc = 1 - (1 - acc) * (1 - m)
    L.over(np.clip(cc / np.maximum(acc, 1e-4)[..., None], 0, 1), acc)


def waves():
    out = []
    for name, seed, n in [('waves-a.webp', 31, 300), ('waves-b.webp', 32, 250)]:
        globals()['R'] = np.random.default_rng(seed)
        L = Layer(30, 474, 1020, 330, 1.5)

        def col(x, y):
            near = np.exp(-((x - 612) / 150) ** 2) * np.exp(-((y - 476) / 70) ** 2)
            if R.random() < near * 1.5:
                return '#FBDDA2'
            return '#E6D8EE' if R.random() < .5 + .35 * np.exp(-(y - 474) / 90) else '#14214D'
        # marks get longer and bolder towards the viewer
        for (yA, yB, k, ln, th) in [(475, 520, .4, (12, 34), (1.3, 2.2)), (520, 640, .35, (26, 64), (2, 3.4)),
                                    (640, 804, .25, (50, 120), (3, 5.5))]:
            arcs(L, int(n * k), (30, yA, 1050, yB), col, ln, th, (.35, .75), sag=.05)
        L.save(name)
        out.append(L)
    globals()['R'] = np.random.default_rng(20270211)
    G = Layer(540, 470, 150, 190, 2)
    arcs(G, 150, (560, 472, 665, 655), lambda x, y: '#FFE2A6', (6, 28), (1.8, 3.6), (.55, .95), sag=.03)
    # narrow towards the horizon
    yy = (np.arange(G.H)[:, None] / G.ppu + G.y0)
    xx = (np.arange(G.W)[None, :] / G.ppu + G.x0)
    width = 18 + (yy - 470) * .32
    G.A *= np.clip(1 - (np.abs(xx - 612) - width) / 14, 0, 1)
    G.P *= np.clip(1 - (np.abs(xx - 612) - width) / 14, 0, 1)[..., None]
    G.save('glint.webp')


# ---------------------------------------------------------------------------
# 4. The chalk cliff on the right, lit pink by the sunset.
# ---------------------------------------------------------------------------
def cliff():
    L = Layer(850, 270, 200, 280, 2)
    face = [(874, 482), (871, 452), (878, 420), (868, 388), (874, 356), (866, 328), (900, 318), (960, 306),
            (1010, 300), (1052, 296), (1052, 482)]
    paint(L, face, '#FBE6D3', '#F4C9B4', layers=40, alpha=.07, var=.18, edge=.32, tex=.5)
    # cool shadow in the folds of the chalk
    for x in [886, 905, 930, 952, 978, 1004, 1030]:
        top = 318 - (x - 866) * .14
        pts = [(x, top + 6), (x + R.uniform(5, 10), top + 8), (x + R.uniform(2, 9), 476), (x - R.uniform(2, 5), 476)]
        paint(L, pts, '#A795C6', '#C3A2BC', layers=14, alpha=R.uniform(.02, .04), var=.45, edge=.25, tex=.75)
    paint(L, [(1004, 300), (1052, 296), (1052, 482), (1016, 482)], '#9C8DBB', layers=14, alpha=.035, var=.4, edge=.2)
    # the grassy cap, drooping over the edge
    cap = [(862, 330), (900, 316), (960, 303), (1010, 296), (1054, 291), (1054, 302), (1010, 306), (960, 313),
           (902, 326), (872, 338)]
    paint(L, cap, '#8E8C4C', '#6F6A3E', layers=26, alpha=.08, var=.35, edge=.35, tex=.6)
    # surf at the foot
    paint(L, [(868, 474), (1052, 472), (1052, 486), (868, 486)], '#E9E2F1', layers=14, alpha=.06, var=.6, edge=.2, tex=.8)
    ink(L, [(874, 480), (871, 452), (878, 420), (868, 388), (874, 356), (866, 330)], width=.8, alpha=.35, jitter=.6)
    yy = (np.arange(L.H)[:, None] / L.ppu + L.y0) * np.ones((1, L.W))
    keep = np.clip((492 - yy) / 6, 0, 1)  # stop the chalk wash spilling into the sea
    L.A *= keep
    L.P *= keep[..., None]
    L.save('cliff.webp')


# ---------------------------------------------------------------------------
# 5. Golden grass in the foreground, rising to the right like the hillside in the film.
# ---------------------------------------------------------------------------
def land():
    L = Layer(30, 590, 1020, 390, 1.2)

    def top(x):
        return 792 - (x - 30) * .13 - 18 * np.exp(-((x - 960) / 90) ** 2) + 4 * np.sin(x / 37)
    xs = np.linspace(30, 1050, 30)
    poly = [(x, top(x)) for x in xs] + [(1050, 980), (30, 980)]
    paint(L, poly, '#B98A45', '#9C7040', layers=34, alpha=.08, var=.12, edge=.3, tex=.55)
    # deepen towards the viewer
    yy = (np.arange(L.H)[:, None] / L.ppu + L.y0)
    shade = np.clip((yy - 700) / 220, 0, 1) * np.ones((1, L.W))
    L.P = L.P * (1 - .55 * shade[..., None]) + hexc('#3E3140') * .55 * shade[..., None] * L.A[..., None]
    # blades of grass catching the last light along the crest
    def col(x, y):
        return '#E8C27C' if R.random() < .55 else ('#7A5A36' if R.random() < .6 else '#C99A55')
    acc = np.zeros((L.H, L.W))
    cc = np.zeros((L.H, L.W, 3))
    im_list = []
    for _ in range(1700):
        x = R.uniform(30, 1050)
        y = top(x) + abs(R.normal(0, 26))
        h = R.uniform(8, 30)
        lean = R.normal(.35, .25)
        pts = [(x, y), (x + lean * h * .5, y - h * .55), (x + lean * h, y - h)]
        q = L.px(pts)
        im = Image.new('L', (L.W, L.H), 0)
        ImageDraw.Draw(im).line([tuple(map(float, v)) for v in q], fill=255, width=1)
        im_list.append((np.asarray(im, float) / 255 * R.uniform(.25, .7), hexc(col(x, y))))
        if len(im_list) == 200:
            for m, c in im_list:
                cc = cc * (1 - m[..., None]) + c * m[..., None]
                acc = 1 - (1 - acc) * (1 - m)
            im_list = []
    for m, c in im_list:
        cc = cc * (1 - m[..., None]) + c * m[..., None]
        acc = 1 - (1 - acc) * (1 - m)
    L.over(np.clip(cc / np.maximum(acc, 1e-4)[..., None], 0, 1), acc)
    L.save('land.webp', quality=70)


# ---------------------------------------------------------------------------
# 6. The lighthouse, crisp-edged washes with a light pen line.
# ---------------------------------------------------------------------------
def tower():
    L = Layer(720, 180, 160, 330, 3)
    # rock and surf at the base
    paint(L, [(736, 488), (758, 476), (800, 471), (842, 475), (866, 487), (846, 496), (800, 499), (754, 496)],
          '#262B4F', '#3E4370', layers=30, alpha=.08, var=.4, edge=.3)
    body = [(771, 478), (829, 478), (818, 262), (782, 262)]
    paint(L, body, '#F8F1E6', '#F1E3D6', layers=40, alpha=.09, var=.06, edge=.22, tex=.4, base_depth=4)
    paint(L, [(772, 478), (779, 478), (786, 262), (782, 262)], '#FFD3A0', layers=18, alpha=.06, var=.15, edge=.1)  # sunset side
    paint(L, [(805, 478), (829, 478), (818, 262), (806, 262)], '#A898C8', '#B4A3C9', layers=22, alpha=.055, var=.12, edge=.25)  # shade
    for (a, b) in [(398, 421), (322, 345)]:
        wa = 29 - (478 - a) * 11 / 216
        wb = 29 - (478 - b) * 11 / 216
        paint(L, [(800 - wb, b), (800 + wb, b), (800 + wa, a), (800 - wa, a)], '#B0285F', '#C23A64',
              layers=34, alpha=.08, var=.22, edge=.35, tex=.5)
        paint(L, [(806, b), (800 + wb, b), (800 + wa, a), (806, a)], '#5B1E52', layers=16, alpha=.05, var=.15, edge=.2)
    paint(L, [(793, 478), (807, 478), (807, 462), (800, 455), (793, 462)], '#34305C', layers=16, alpha=.1, var=.1)
    for wy in (372, 296):
        paint(L, [(797, wy), (803, wy), (803, wy + 10), (797, wy + 10)], '#2A2D58', layers=12, alpha=.12, var=.1)
    paint(L, [(774, 250), (826, 250), (826, 264), (774, 264)], '#23285A', layers=26, alpha=.12, var=.05, edge=.2)
    paint(L, [(782, 222), (818, 222), (818, 251), (782, 251)], '#FFE6A0', '#FFF4CF', layers=26, alpha=.12, var=.04, edge=.15)
    paint(L, [(772, 225), (828, 225), (800, 194)], '#23285A', layers=26, alpha=.12, var=.05, edge=.2)
    paint(L, ellipse(800, 192, 3.2, 3.2, 8), '#23285A', layers=10, alpha=.2, var=.05)
    # surf around the base
    paint(L, [(744, 485), (770, 478), (800, 482), (832, 478), (858, 485), (832, 490), (800, 488), (768, 490)],
          '#ECE7F6', layers=16, alpha=.07, var=.5, edge=.15, tex=.8)
    # pen line
    ink(L, [(771, 478), (782, 262)], width=.9)
    ink(L, [(829, 478), (818, 262)], width=.9)
    ink(L, [(774, 264), (826, 264)], width=.8)
    ink(L, [(774, 250), (826, 250)], width=.8)
    for x in range(776, 827, 7):
        ink(L, [(x, 250), (x, 245)], width=.5, alpha=.6, passes=1)
    ink(L, [(772, 245), (828, 245)], width=.6, alpha=.6, passes=1)
    for x in (791, 800, 809):
        ink(L, [(x, 225), (x, 250)], width=.45, alpha=.55, passes=1)
    ink(L, [(772, 225), (800, 194), (828, 225)], width=.8)
    ink(L, [(738, 488), (760, 480)], width=.6, alpha=.5, passes=1)
    ink(L, [(842, 480), (864, 488)], width=.6, alpha=.5, passes=1)
    L.save('tower.webp', quality=86)

    # its wavering reflection
    F = Layer(740, 486, 120, 130, 2)
    for i in range(70):
        y = R.uniform(490, 610)
        spread = 1 + (y - 490) / 70
        x = 800 + R.normal(0, 10 * spread)
        t = abs(x - 800)
        if y < 560 and (y - 490) % 46 < 14 and t < 22:
            c = '#B0285F'
        elif t < 28:
            c = '#EDE4EE'
        else:
            continue
        paint(F, ellipse(x, y, R.uniform(4, 12), R.uniform(.7, 1.6), 8), c, layers=4, alpha=.12, var=.3,
              base_depth=2, layer_depth=1, edge=.1)
    yy = (np.arange(F.H)[:, None] / F.ppu + F.y0)
    fade = np.clip(1 - (yy - 492) / 120, 0, 1) * np.ones((1, F.W))
    F.A *= fade
    F.P *= fade[..., None]
    F.save('refl.webp')


# ---------------------------------------------------------------------------
# 7. Light: the beam, the lantern's halo, and the two blooms that flood the screen.
# ---------------------------------------------------------------------------
def light():
    # Beam: from the lantern at its right-centre, spreading left. Covers x -320..800, y 36..436.
    L = Layer(-320, 36, 1120, 400, 1)
    yy = (np.arange(L.H)[:, None] / L.ppu + L.y0) * np.ones((1, L.W))
    xx = (np.arange(L.W)[None, :] / L.ppu + L.x0) * np.ones((L.H, 1))
    dist = np.clip((800 - xx) / 1110, 0, 1)
    half = 5 + 134 * dist
    up = yy < 236
    wob = 1 + .07 * np.where(up, noise(1, L.W, 1, 110, seed=61)[0][None, :], noise(1, L.W, 1, 110, seed=62)[0][None, :])
    u = np.abs(yy - 236) / half
    body = np.clip((wob - u) / .45, 0, 1) ** 1.3          # soft, slightly wandering edges
    core = np.exp(-(u / .38) ** 2)                         # a brighter heart along the axis
    streak = 1 + .16 * noise(L.H, L.W, 2.5, 45, seed=63)  # soft brush streaks along the light
    A = (body * .62 + core * .35) * (1 - dist) ** .85 * streak * (xx < 801)
    C = hexc('#FFF0C2') * (1 - .25 * dist[..., None]) + hexc('#FFD9A0') * .25 * dist[..., None]
    L.over(C, np.clip(A, 0, 1))
    L.save('beam.webp')

    G = Layer(670, 106, 260, 260, 1.5)
    A = blob_alpha(G, ellipse(800, 236, 64, 62, 14), layers=40, alpha=.04, var=.35, tex=.5)
    A = gaussian_filter(A, 7 * G.ppu)
    yy = (np.arange(G.H)[:, None] / G.ppu + G.y0)
    xx = (np.arange(G.W)[None, :] / G.ppu + G.x0)
    r = np.hypot(xx - 800, yy - 236)
    core = np.exp(-(r / 46) ** 2)
    wide = np.exp(-(r / 105) ** 2)
    window = np.clip(1 - (r / 128) ** 2, 0, 1) ** 1.5  # nothing left at the edge of the image
    G.over(hexc('#FFE3A2'), np.clip((A * .45 + core * .55 + wide * .22) * window, 0, .95))
    G.save('glow.webp')

    for name, col, col2, seed in [('bloom-a.webp', '#FFDF9C', '#FFCF86', 41), ('bloom-b.webp', '#FFF6E2', '#FFEFCF', 42)]:
        globals()['R'] = np.random.default_rng(seed)
        B = Layer(-150, -150, 300, 300, 1.6)
        A = blob_alpha(B, ellipse(0, 0, 108, 104, 14), layers=48, alpha=.09, var=.85, tex=.35)
        A = np.clip(A * 1.35, 0, 1)
        E = np.clip(A - gaussian_filter(A, 4 * B.ppu), 0, None)
        E /= E.max() + 1e-6
        t = np.clip(.5 + .3 * noise(B.H, B.W, 25), 0, 1)[..., None]
        C = (hexc(col) * (1 - t) + hexc(col2) * t) * (1 - .12 * E[..., None])
        B.over(C, A)
        B.save(name)
    globals()['R'] = np.random.default_rng(20270212)


# ---------------------------------------------------------------------------
# 8. Paper grain, tiled over the whole painting.
# ---------------------------------------------------------------------------
def paper():
    n = 384
    g = noise(n, n, .8, seed=91) * .6 + noise(n, n, 3, seed=92) * .4
    fib = np.zeros((n, n))
    r = np.random.default_rng(93)
    big = Image.new('L', (n * 3, n * 3), 0)
    d = ImageDraw.Draw(big)
    for _ in range(140):
        x, y = r.uniform(0, n, 2)
        a = r.uniform(0, np.pi)
        l = r.uniform(8, 40)
        for ox in (0, n, 2 * n):
            for oy in (0, n, 2 * n):
                d.line([(x + ox, y + oy), (x + ox + np.cos(a) * l, y + oy + np.sin(a) * l)], fill=int(r.uniform(60, 140)), width=1)
    fib = np.asarray(big, float)[n:2 * n, n:2 * n] / 255
    alpha = np.clip(g * .06 + .05, 0, .16) + fib * .07
    rgb = np.ones((n, n, 3)) * hexc('#4A3A2C')
    im = Image.fromarray((np.dstack([rgb, alpha]) * 255).astype(np.uint8), 'RGBA')
    im.save(os.path.join(OUT, 'paper.webp'), 'WEBP', quality=70, alpha_quality=70)


if __name__ == '__main__':
    import time
    steps = [('backdrop', backdrop), ('clouds', lambda: [cloud('cloud-a.webp', 360, 1), cloud('cloud-b.webp', 300, 2),
                                                         cloud('cloud-c.webp', 240, 3)]),
             ('waves', waves), ('cliff', cliff), ('land', land), ('tower', tower), ('light', light), ('paper', paper)]
    only = set(sys.argv[2:])
    for name, fn in steps:
        if only and name not in only:
            continue
        t = time.time()
        fn()
        print(f'{name}: {time.time() - t:.1f}s')
    for f in sorted(os.listdir(OUT)):
        print(f'{f:16s} {os.path.getsize(os.path.join(OUT, f)) // 1024:5d} KB')
