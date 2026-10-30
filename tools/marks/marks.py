"""Draft marks for the invite: Ganesha (groom's side), endless knot and golden fish (bride's side)."""
import math

IND, IVO, MAR, MAG, TEAL, PAPER = '#14183A', '#FBF5E6', '#F2A900', '#B0285F', '#0E6B6B', '#F4EFE3'

# ---------------- Endless knot ----------------
def knot(N=3, unit=18, w=3.2, gap=2.6, ink=IND, bg=PAPER, accent=None, ribbon=False):
    # single-curve arrangement found by search: corner loops at TL and BR
    pairs = {'L': [(0, 1)], 'R': [(1, 2)], 'T': [(1, 2)], 'B': [(0, 1)]} if N == 3 else None
    if N == 5:
        pairs = {'L': [(0, 1), (2, 3)], 'R': [(1, 2), (3, 4)], 'T': [(1, 2), (3, 4)], 'B': [(0, 1), (2, 3)]}
    corner = [(('L', N - 1), ('T', 0), (0, N)), (('R', 0), ('B', N - 1), (N, 0))]
    pos = lambda s, k: {'L': (0, k + .5), 'R': (N, k + .5), 'B': (k + .5, 0), 'T': (k + .5, N)}[s]
    out = {'L': (-1, 0), 'R': (1, 0), 'B': (0, -1), 'T': (0, 1)}
    edges = {}
    def link(a, b, kind, data=None):
        edges.setdefault(a, []).append((b, kind, data)); edges.setdefault(b, []).append((a, kind, data))
    for k in range(N):
        link(('L', k), ('R', k), 'line'); link(('B', k), ('T', k), 'line')
    for s, ps in pairs.items():
        for a, b in ps: link((s, a), (s, b), 'side')
    for a, b, c in corner: link(a, b, 'corner', c)
    # walk the cycle
    start = ('L', 0); prev = None; cur = start; pts = []
    used = set()
    while True:
        opts = [e for e in edges[cur] if (frozenset((cur, e[0])), e[1]) not in used]
        nxt, kind, data = opts[0] if prev is None else [e for e in opts][0]
        used.add((frozenset((cur, nxt)), kind))
        p0, p1 = pos(*cur), pos(*nxt)
        if kind == 'line':
            seg = [p0, p1]
        elif kind == 'side':
            s = cur[0]; ox, oy = out[s]
            cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            a0 = math.atan2(p0[1] - cy, p0[0] - cx); a1 = math.atan2(p1[1] - cy, p1[0] - cx)
            mid = math.atan2(oy, ox)
            # go from a0 to a1 passing through the outward direction
            def norm(a): return (a + 2 * math.pi) % (2 * math.pi)
            d = norm(a1 - a0)
            if abs(norm(mid - a0)) > d: d = d - 2 * math.pi
            seg = [(cx + .5 * math.cos(a0 + d * t / 24), cy + .5 * math.sin(a0 + d * t / 24)) for t in range(25)]
        else:
            cx, cy = data
            a0 = math.atan2(p0[1] - cy, p0[0] - cx); a1 = math.atan2(p1[1] - cy, p1[0] - cx)
            inward = math.atan2(N / 2 - cy, N / 2 - cx)
            def norm(a): return (a + 2 * math.pi) % (2 * math.pi)
            d = norm(a1 - a0)
            if norm(inward - a0) < d: d = d - 2 * math.pi   # go the long way, around the outside
            r = .5 * math.sqrt(2) * 1.0
            r = math.hypot(p0[0] - cx, p0[1] - cy)
            seg = [(cx + r * math.cos(a0 + d * t / 40), cy + r * math.sin(a0 + d * t / 40)) for t in range(41)]
        pts += seg if not pts else seg[1:]
        prev, cur = cur, nxt
        if cur == start: break
    # rotate 45 degrees, scale
    c = N / 2; ang = math.radians(45)
    def tf(p):
        x, y = p[0] - c, -(p[1] - c)
        return (unit * (x * math.cos(ang) - y * math.sin(ang)), unit * (x * math.sin(ang) + y * math.cos(ang)))
    P = [tf(p) for p in pts]
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    pad = w + 4
    minx, maxx, miny, maxy = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    d = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in P) + ' Z'
    over = []
    for i in range(N):
        for j in range(N):
            x, y = i + .5, j + .5
            if (i + j) % 2 == 0: a, b = (x - .3, y), (x + .3, y)
            else: a, b = (x, y - .3), (x, y + .3)
            A, B = tf(a), tf(b)
            over.append(f'M{A[0]:.2f} {A[1]:.2f} L{B[0]:.2f} {B[1]:.2f}')
    ov = ' '.join(over)
    sw = f'stroke-linecap="round" stroke-linejoin="round" fill="none"'
    if ribbon:  # a hollow ribbon: wide ink, thin background core
        body = (f'<path d="{d}" stroke="{ink}" stroke-width="{w*2.2}" {sw}/><path d="{d}" stroke="{bg}" stroke-width="{w*0.9}" {sw}/>'
                f'<path d="{ov}" stroke="{bg}" stroke-width="{w*2.2+gap*2}" stroke-linecap="butt" fill="none"/>'
                f'<path d="{ov}" stroke="{ink}" stroke-width="{w*2.2}" stroke-linecap="butt" fill="none"/>'
                f'<path d="{ov}" stroke="{bg}" stroke-width="{w*0.9}" stroke-linecap="butt" fill="none"/>')
        pad2 = w * 1.6; minx -= pad2; miny -= pad2; maxx += pad2; maxy += pad2
    else:
        body = (f'<path d="{d}" stroke="{ink}" stroke-width="{w}" {sw}/>'
                f'<path d="{ov}" stroke="{bg}" stroke-width="{w+gap*2}" stroke-linecap="butt" fill="none"/>'
                f'<path d="{ov}" stroke="{ink}" stroke-width="{w}" stroke-linecap="butt" fill="none"/>')
    if accent:
        body = f'<circle cx="0" cy="0" r="{unit*0.16}" fill="{accent}"/>' + body if False else body
    vb = f'{minx:.1f} {miny:.1f} {maxx-minx:.1f} {maxy-miny:.1f}'
    return vb, body

# ---------------- Golden fish ----------------
# Two fish, heads up and facing each other, bodies bowed outward, tails crossing at the foot.
BACK  = 'M58 14 C42 20 31 42 33 64 C35 80 44 91 51 97'
BELLY = 'M58 14 C61 28 61 52 59 70 C58 82 55 91 51 97'
TAILS = 'M51 97 C47 102 43 106 38 111 M51 97 C55 101 60 105 66 109'
def fish(ink=MAR, w=2.6, eye=IND, fill=None, detail=None, scales=True):
    detail = detail or ink
    body = BACK + ' ' + BELLY[BELLY.index('C'):].replace('C', 'C', 1)
    shape = 'M58 14 C42 20 31 42 33 64 C35 80 44 91 51 97 C55 91 58 82 59 70 C61 52 61 28 58 14 Z'
    one = ''
    if fill:
        one += f'<path d="{shape}" fill="{fill}"/>'
    else:
        one += f'<path d="{shape}" fill="none" stroke="{ink}" stroke-width="{w}" stroke-linejoin="round"/>'
    one += f'<path d="{TAILS}" fill="none" stroke="{fill or ink}" stroke-width="{w*1.1}" stroke-linecap="round"/>'
    one += f'<circle cx="51" cy="27" r="{w*0.75}" fill="{eye}"/>'
    one += f'<path d="M40 36 C46 40 53 40 59 36" fill="none" stroke="{detail}" stroke-width="{w*0.6}" stroke-linecap="round"/>'
    if scales:
        for k in range(3):
            y = 50 + k * 10
            one += f'<path d="M{39+k} {y} q{9-k*1.2} 6 {18-k*3} 0" fill="none" stroke="{detail}" stroke-width="{w*0.5}" stroke-linecap="round" opacity=".85"/>'
    one += f'<path d="M33 58 C26 56 23 62 27 67" fill="none" stroke="{fill or ink}" stroke-width="{w*0.75}" stroke-linecap="round"/>'
    return f'<g>{one}</g><g transform="translate(124 0) scale(-1 1)">{one}</g>'

def ring(cx=62, cy=62, r=58, ink=MAR, w=1.6):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ink}" stroke-width="{w}"/>'

# ---------------- Ganesha ----------------
def ganesha_line(ink=IND, gold=MAR, tilak=MAG, w=3):
    s = f'fill="none" stroke="{ink}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'
    g = f'fill="none" stroke="{gold}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'
    return (
        # crown: a tiered dome with a finial
        f'<path d="M45 40 C45 30 52 22 60 15 C68 22 75 30 75 40" {g}/>'
        f'<path d="M43 41 L77 41" {g}/>'
        f'<path d="M51 31 L69 31" {g} stroke-width="{w*0.6}"/>'
        f'<circle cx="60" cy="10.5" r="{w*0.9}" fill="{gold}"/>'
        # ears: broad, fan-like, wavy outer edge
        f'<path d="M45 46 C34 38 20 40 17 50 C14 60 18 72 28 76 C35 78 41 74 45 68" {s}/>'
        f'<path d="M75 46 C86 38 100 40 103 50 C106 60 102 72 92 76 C85 78 79 74 75 68" {s}/>'
        # head and cheeks
        f'<path d="M45 44 C44 56 46 66 52 72" {s}/>'
        f'<path d="M75 44 C76 56 74 66 68 72" {s}/>'
        # eyes
        f'<path d="M50 53 q3 -3 6 0" {s} stroke-width="{w*0.75}"/>'
        f'<path d="M64 53 q3 -3 6 0" {s} stroke-width="{w*0.75}"/>'
        # tilak
        f'<path d="M60 44 L60 50" fill="none" stroke="{tilak}" stroke-width="{w*0.9}" stroke-linecap="round"/>'
        # trunk: down the middle and curling to the viewer's right
        f'<path d="M56 58 C55 70 56 82 59 90 C62 98 71 101 76 96 C80 92 78 86 73 86 C70 86 69 89 70 91" {s}/>'
        f'<path d="M64 58 C65 66 65 74 64 80" {s}/>'
        # single tusk on the viewer's left (the other is broken)
        f'<path d="M52 72 C49 76 47 80 47 84" {s} stroke-width="{w*0.85}"/>'
    )

def ganesha_emblem(ink=IND, gold=MAR, tilak=MAG, bg=PAPER):
    # filled, with the ears as two lotus petals; a calmer, stamp-like mark
    return (
        f'<path d="M60 12 C67 19 74 28 74 38 L46 38 C46 28 53 19 60 12 Z" fill="{gold}"/>'
        f'<circle cx="60" cy="8" r="2.6" fill="{gold}"/>'
        f'<rect x="43" y="38" width="34" height="5" rx="2.5" fill="{gold}"/>'
        f'<path d="M45 47 C30 36 14 44 16 58 C18 70 30 78 45 70 Z" fill="{ink}"/>'
        f'<path d="M75 47 C90 36 106 44 104 58 C102 70 90 78 75 70 Z" fill="{ink}"/>'
        f'<path d="M45 44 L75 44 C76 58 72 68 66 74 C66 82 66 88 70 92 C74 96 80 94 80 89 C80 85 76 84 74 86 '
        f'C72 82 76 80 79 82 C86 87 84 100 74 102 C64 104 58 96 56 86 C55 80 54 76 54 74 C48 68 44 58 45 44 Z" fill="{ink}"/>'
        f'<path d="M51 54 q3 -2.6 6 0" fill="none" stroke="{bg}" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M63 54 q3 -2.6 6 0" fill="none" stroke="{bg}" stroke-width="2" stroke-linecap="round"/>'
        f'<path d="M60 46 L60 51" fill="none" stroke="{tilak}" stroke-width="2.6" stroke-linecap="round"/>'
        f'<path d="M53 71 C50 75 48 79 48 83" fill="none" stroke="{bg}" stroke-width="2.4" stroke-linecap="round"/>'
    )

def arch(ink=MAR, w=1.6):
    return (f'<path d="M14 116 L14 52 C14 26 36 6 60 2 C84 6 106 26 106 52 L106 116" fill="none" stroke="{ink}" stroke-width="{w}"/>'
            f'<path d="M8 116 L112 116" stroke="{ink}" stroke-width="{w}"/>')

def lotus(cx, cy, s=1, ink=MAR, w=1.8):
    return (f'<g transform="translate({cx} {cy}) scale({s})" fill="none" stroke="{ink}" stroke-width="{w/s}" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M0 0 C-6 -6 -6 -14 0 -20 C6 -14 6 -6 0 0 Z"/>'
            '<path d="M-2 0 C-10 -2 -15 -8 -16 -14 C-9 -13 -4 -8 -2 0"/>'
            '<path d="M2 0 C10 -2 15 -8 16 -14 C9 -13 4 -8 2 0"/>'
            '<path d="M-14 1 C-6 3 6 3 14 1"/></g>')

def svg(vb, body, size=120, title=''):
    return f'<svg viewBox="{vb}" width="{size}" height="{size}" role="img" aria-label="{title}">{body}</svg>'
