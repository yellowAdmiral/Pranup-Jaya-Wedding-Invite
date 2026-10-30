#!/usr/bin/env python3
"""Prints the SVG symbols for the sacred marks used in index.html.

    python3 tools/marks/build.py > /tmp/symbols.svg

Ganesha (Pranup's side): tapered lines in ivory, marigold crown, sindoor tilak.
Endless knot (Jaya's side): the finer five-strand weave, in marigold, with its
over-under gaps cut in indigo, for the footer; the -paper versions are for the cream pages.
Paste the output over the <symbol> blocks in index.html (ids mk-ganesha-paper, mk-knot-paper).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marks as M, elegant as E

g = E.ganesha(ink=M.IVO)
kvb, kb = M.knot(5, unit=12, w=2.0, gap=1.8, ink=M.MAR, bg=M.IND)
# Paper versions for the cream pages: Ganesha in indigo lines with the gold crown; the knot in gold
# with its over-under gaps cut in the paper colour.
gp = E.ganesha(ink=M.IND)
kvbp, kbp = M.knot(5, unit=12, w=2.1, gap=1.8, ink='#D69300', bg=M.PAPER)  # a deeper gold, so the fine weave holds on cream
# Ivory / indigo-gap versions (g, kvb, kb) are kept for dark grounds but are not used on the page now.
print(f'<symbol id="mk-ganesha-paper" viewBox="8 0 104 124">{gp}</symbol>')
print(f'<symbol id="mk-knot-paper" viewBox="{kvbp}">{kbp}</symbol>')
