import marks as M
from brush import stroke as S

IND, MAR, MAG, PAPER = M.IND, M.MAR, M.MAG, M.PAPER

def ganesha(ink=IND, gold=MAR, tilak=MAG, k=1.0):
    """A refined Ganesha in a few tapered strokes: crown, long petal ears, an S-curved trunk."""
    w = lambda x: x * k
    g = []
    # crown: a slender spire, two outer strokes and a fine band
    g.append(S('M48 41 C49 31 54 21 60 11', w(2.4), .3, start=.8, end=1, fill=gold))
    g.append(S('M72 41 C71 31 66 21 60 11', w(2.4), .3, start=.8, end=1, fill=gold))
    g.append(S('M54 33 C58 31 62 31 66 33', w(1.4), .3, fill=gold))
    g.append(S('M45 43 C53 40 67 40 75 43', w(1.8), .4, fill=gold))
    g.append(f'<circle cx="60" cy="7.5" r="{1.7*k}" fill="{gold}"/>')
    g.append(S('M60 24 C58 27 58 29 60 31 C62 29 62 27 60 24', w(1.0), .4, fill=gold))
    # ears: long petals sweeping out and down, open toward the face
    g.append(S('M47 47 C38 41 25 41 19 49 C13 58 17 73 30 79 C37 82 43 79 46 74', w(2.6), .3, bias=.45, fill=ink))
    g.append(S('M73 47 C82 41 95 41 101 49 C107 58 103 73 90 79 C83 82 77 79 74 74', w(2.6), .3, bias=.45, fill=ink))
    # temples sweeping down into the trunk
    g.append(S('M48 46 C47 56 50 66 55 74', w(2.2), .3, start=.9, fill=ink))
    g.append(S('M72 46 C73 56 70 66 65 74', w(2.2), .3, start=.9, fill=ink))
    # trunk: a long S that turns to the viewer's right and closes in a small curl
    g.append(S('M57 60 C55 74 56 88 60 98 C64 108 76 110 80 102 C83 96 79 91 74 92 C71 93 70 96 72 98',
               w(2.6), .3, start=.6, end=1, bias=.35, fill=ink))
    g.append(S('M63 60 C64 68 64 76 63 84', w(1.6), .3, fill=ink))
    # eyes, tilak, and the single tusk
    g.append(S('M50 53 C52 51 55 51 57 53', w(1.3), .3, fill=ink))
    g.append(S('M63 53 C65 51 68 51 70 53', w(1.3), .3, fill=ink))
    g.append(S('M60 44 C59 46 59 48 60 50 C61 48 61 46 60 44', w(1.6), .4, fill=tilak))
    g.append(S('M53 75 C50 79 48 83 48 88', w(2.0), .3, start=.3, fill=ink))
    return ''.join(g)

def fish(ink=MAR, eye=IND, k=1.0):
    """Two slender fish, heads up and facing, tails crossed: drawn with tapered outlines."""
    w = lambda x: x * k
    one = []
    one.append(S('M57 13 C40 18 27 42 29 64 C31 81 42 93 51 99', w(2.4), .3, bias=.45, fill=ink))   # back
    one.append(S('M57 13 C51 28 46 50 47 68 C48 82 50 92 51 99', w(1.8), .3, bias=.4, fill=ink))    # belly, bowed away
    one.append(S('M51 99 C47 104 42 108 36 112', w(2.0), .3, start=.4, fill=ink))                   # tail, outer
    one.append(S('M51 99 C55 103 60 107 67 110', w(2.0), .3, start=.4, fill=ink))                   # tail, inner (crosses)
    one.append(S('M41 33 C44 36 48 36 52 33', w(1.1), .3, fill=ink))                                # gill
    one.append(S('M29 58 C23 57 20 62 23 67', w(1.3), .3, fill=ink))                                # fin
    one.append(f'<circle cx="49" cy="24" r="{1.4*k}" fill="{eye}"/>')
    for i, y in enumerate((50, 61, 72)):
        one.append(S(f'M{36+i} {y} C{38+i} {y+4} {42} {y+4} {45-i*.5} {y}', w(.8), .25, fill=ink))
    one = ''.join(one)
    return f'<g>{one}</g><g transform="translate(124 0) scale(-1 1)">{one}</g>'

def arch(ink=MAR, k=1.0):
    """A fine temple doorway framing a mark."""
    return (S('M14 122 C14 88 14 60 22 40 C32 18 46 8 60 2', 1.4*k, .5, start=.2, end=.3, fill=ink) +
            S('M106 122 C106 88 106 60 98 40 C88 18 74 8 60 2', 1.4*k, .5, start=.2, end=.3, fill=ink))

def sep(cx, cy, ink=MAR):
    """A small diamond between paired marks."""
    return f'<path d="M{cx} {cy-4} L{cx+3} {cy} L{cx} {cy+4} L{cx-3} {cy} Z" fill="{ink}"/>'
