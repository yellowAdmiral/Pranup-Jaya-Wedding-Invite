"""Composite the watercolour layers into one still for the printed cover (the arch window)."""
import numpy as np
from PIL import Image
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', '..', 'art') + '/'
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
# region of the scene shown in the window (scene units) and the output size in pixels
X0, Y0, W, H = 570, 140, 470, 506
OUT_W = 1500; S = OUT_W / W; OUT_H = round(H * S)
layers = [  # name, x, y, w, h   (positions from index.html; clouds placed for a still)
    ('bg', 30, -120, 1020, 1100), ('cloud-b', 470, 212, 380, 90), ('cloud-a', 880, 118, 440, 90), ('cloud-c', 560, 58, 320, 90),
    ('glint', 540, 470, 150, 190), ('waves-b', 30, 474, 1020, 330), ('waves-a', 30, 474, 1020, 330),
    ('cliff', 850, 270, 200, 280), ('refl', 740, 486, 120, 130), ('land', 30, 590, 1020, 390),
    ('glow', 670, 106, 260, 260), ('beam', -320, 36, 1120, 400), ('tower', 720, 180, 160, 330)]
can = Image.new('RGBA', (OUT_W, OUT_H), (20, 48, 79, 255))
for n, x, y, w, h in layers:
    im = Image.open(ART + n + '.webp').convert('RGBA')
    # crop to the part inside the window before scaling, to keep it fast
    cx0, cy0 = max(x, X0), max(y, Y0); cx1, cy1 = min(x + w, X0 + W), min(y + h, Y0 + H)
    if cx1 <= cx0 or cy1 <= cy0: continue
    sx, sy = im.width / w, im.height / h
    box = (round((cx0 - x) * sx), round((cy0 - y) * sy), round((cx1 - x) * sx), round((cy1 - y) * sy))
    part = im.crop(box).resize((round((cx1 - cx0) * S), round((cy1 - cy0) * S)), Image.LANCZOS)
    can.alpha_composite(part, (round((cx0 - X0) * S), round((cy0 - Y0) * S)))
# paper grain on top, at a fine scale
grain = Image.open(ART + 'paper.webp').convert('RGBA')
tile = Image.new('RGBA', can.size)
for i in range(0, OUT_W, grain.width):
    for j in range(0, OUT_H, grain.height): tile.paste(grain, (i, j))
a = np.asarray(tile).copy(); a[..., 3] = (a[..., 3] * .8).astype(np.uint8)
can.alpha_composite(Image.fromarray(a))
can.convert('RGB').save(os.path.join(HERE, 'out', 'cover-painting.jpg'), quality=93)
print(can.size)
