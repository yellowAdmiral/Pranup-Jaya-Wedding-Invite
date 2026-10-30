"""Tapered, calligraphic strokes: a centre line becomes a filled shape that swells in the middle and thins to a point."""
import math, re

def _cubic(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                    u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    return out

def points(d, n=28):
    """Centre line from 'M x y C ... C ...' (absolute, cubic only)."""
    nums = list(map(float, re.findall(r'-?\d*\.?\d+', d)))
    p = (nums[0], nums[1]); pts = [p]; i = 2
    while i + 5 < len(nums) + 1 and i < len(nums):
        c1, c2, e = (nums[i], nums[i+1]), (nums[i+2], nums[i+3]), (nums[i+4], nums[i+5])
        pts += _cubic(p, c1, c2, e, n)[1:]; p = e; i += 6
    return pts

def stroke(d, wmax=3.0, wmin=0.35, start=1.0, end=1.0, bias=0.5, fill='#14183A', n=28):
    """start/end scale the taper at each end (1 = full point, 0 = blunt); bias moves the widest point."""
    P = points(d, n)
    L = [0.0]
    for a, b in zip(P, P[1:]): L.append(L[-1] + math.hypot(b[0]-a[0], b[1]-a[1]))
    tot = L[-1] or 1
    left, right = [], []
    for i, (x, y) in enumerate(P):
        t = L[i] / tot
        # swell: rises to 1 at 'bias', falls to the end
        s = math.sin(math.pi * min(1, (t / bias) * .5)) if t < bias else math.sin(math.pi * (.5 + .5 * (t - bias) / (1 - bias)))
        s = max(0.0, s)
        if t < bias: s = (1 - start) + start * s
        else: s = (1 - end) + end * s
        w = wmin + (wmax - wmin) * s ** .7
        a = P[max(0, i-1)]; b = P[min(len(P)-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; ln = math.hypot(dx, dy) or 1
        nx, ny = -dy/ln, dx/ln
        left.append((x + nx*w/2, y + ny*w/2)); right.append((x - nx*w/2, y - ny*w/2))
    poly = left + right[::-1]
    return f'<path d="M{" L".join(f"{x:.2f} {y:.2f}" for x, y in poly)} Z" fill="{fill}"/>'
