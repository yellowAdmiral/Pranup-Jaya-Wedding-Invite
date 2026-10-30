#!/bin/sh
# Fetches the site's fonts (SIL Open Font License) from github.com/google/fonts and makes fixed-weight copies,
# so the PDFs embed ordinary TrueType fonts. Needs git and Python fontTools.
set -e
cd "$(dirname "$0")"
mkdir -p fonts/static
if [ ! -d .gf ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts .gf
  (cd .gf && git sparse-checkout set ofl/cormorantgaramond ofl/greatvibes ofl/jost ofl/notoserifdevanagari)
fi
cp .gf/ofl/greatvibes/GreatVibes-Regular.ttf fonts/
python3 - <<'PY'
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
jobs = [('.gf/ofl/cormorantgaramond/CormorantGaramond[wght].ttf', {'wght': 500}, 'Cormorant-500.ttf'),
        ('.gf/ofl/cormorantgaramond/CormorantGaramond[wght].ttf', {'wght': 600}, 'Cormorant-600.ttf'),
        ('.gf/ofl/cormorantgaramond/CormorantGaramond-Italic[wght].ttf', {'wght': 500}, 'Cormorant-Italic-500.ttf'),
        ('.gf/ofl/jost/Jost[wght].ttf', {'wght': 400}, 'Jost-400.ttf'),
        ('.gf/ofl/jost/Jost[wght].ttf', {'wght': 500}, 'Jost-500.ttf'),
        ('.gf/ofl/notoserifdevanagari/NotoSerifDevanagari[wdth,wght].ttf', {'wght': 400, 'wdth': 100}, 'NotoDeva-400.ttf'),
        ('.gf/ofl/notoserifdevanagari/NotoSerifDevanagari[wdth,wght].ttf', {'wght': 600, 'wdth': 100}, 'NotoDeva-600.ttf')]
for src, loc, dst in jobs:
    instancer.instantiateVariableFont(TTFont(src), loc).save('fonts/static/' + dst)
PY
echo "fonts ready"
