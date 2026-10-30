#!/usr/bin/env python3
"""Prints the SVG symbols for the sacred marks used in index.html.

    python3 tools/marks/build.py > /tmp/symbols.svg

Ganesha (Pranup's side): tapered lines in ivory, marigold crown, sindoor tilak.
Endless knot (Jaya's side): the finer five-strand weave, in marigold, with its
over-under gaps cut in indigo, so it is meant for indigo grounds.
Paste the output over the two <symbol> blocks in index.html (ids mk-ganesha, mk-knot).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marks as M, elegant as E

g = E.ganesha(ink=M.IVO)
kvb, kb = M.knot(5, unit=12, w=2.0, gap=1.8, ink=M.MAR, bg=M.IND)
print(f'<symbol id="mk-ganesha" viewBox="8 0 104 124">{g}</symbol>')
print(f'<symbol id="mk-knot" viewBox="{kvb}">{kb}</symbol>')
