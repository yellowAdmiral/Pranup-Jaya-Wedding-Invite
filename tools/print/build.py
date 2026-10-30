"""Builds the printed invitation as three PDFs: both families, bride's side, groom's side.

    ./tools/print/fetch-fonts.sh      # once: the site's fonts, as fixed-weight files
    python3 tools/print/cover.py      # the watercolour still for the cover
    python3 tools/print/build.py      # writes tools/print/out/*.pdf  (needs Playwright + Chromium, segno)


A5 (148 x 210 mm) with 3 mm bleed on every side, so each page is 154 x 216 mm.
Pages: 1 cover, 2 invitation (blank guest name, families), 3 details (venues with map QR codes, travel),
4 reply card (blank form).
"""
import os, re, sys
import segno
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, '..', '..', 'index.html')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
F = lambda n: 'file://' + os.path.join(HERE, 'fonts', n).replace('[', '%5B').replace(']', '%5D')
# Paper grain, dhaka band, PJ monogram and the sacred marks come straight from the site, so they always match.
_site = open(SITE).read()
GRAIN = re.search(r'\.paper \.face \{\s*background-color: var\(--paper\); background-image: (url\("data:image/png;base64,[^"]+"\))', _site).group(1)
BAND = re.search(r'(url\("data:image/svg\+xml,%3Csvg xmlns=\'http://www\.w3\.org/2000/svg\' width=\'30\' height=\'75\'[^"]*"\))', _site).group(1)
_i = _site.index('<svg width="0" height="0"'); _j = _site.index('</svg>', _site.index('<symbol id="mk-knot-paper"')) + len('</svg>')
DEFS = _site[_i:_j]
COVER = 'file://' + os.path.join(HERE, 'out', 'cover-painting.jpg')  # made by cover.py

MAP_WEDDING = 'https://www.google.com/maps/search/?api=1&query=Gymkhana+Darjeeling+West+Bengal'
# The reception venue is not named yet, so this points to Gorubathan itself. Replace with the venue's map link.
MAP_RECEPTION = 'https://www.google.com/maps/search/?api=1&query=Gorubathan+West+Bengal'
RSVP_EMAIL = 'pranupchhetri27@gmail.com'

def qr(url):
    return segno.make(url, error='m').svg_inline(omitsize=True, dark='#14183A', light=None, border=0)

GANESHA = '<svg class="mark" viewBox="0 0 104 124" role="img" aria-label="Ganesha"><use href="#mk-ganesha-paper"/></svg>'
KNOT = '<svg class="mark knot" viewBox="0 0 91.9 108.9" role="img" aria-label="Endless knot"><use href="#mk-knot-paper"/></svg>'

CSS = f'''
/* Fixed-weight copies of the site's fonts (made with fontTools), so print shops get ordinary embedded TrueType */
@font-face {{ font-family: 'Cormorant Garamond'; src: url("{F('static/Cormorant-500.ttf')}"); font-weight: 400 500; font-style: normal; }}
@font-face {{ font-family: 'Cormorant Garamond'; src: url("{F('static/Cormorant-600.ttf')}"); font-weight: 600 700; font-style: normal; }}
@font-face {{ font-family: 'Cormorant Garamond'; src: url("{F('static/Cormorant-Italic-500.ttf')}"); font-weight: 400 700; font-style: italic; }}
@font-face {{ font-family: 'Great Vibes'; src: url("{F('GreatVibes-Regular.ttf')}"); }}
@font-face {{ font-family: 'Jost'; src: url("{F('static/Jost-400.ttf')}"); font-weight: 400; }}
@font-face {{ font-family: 'Jost'; src: url("{F('static/Jost-500.ttf')}"); font-weight: 500 700; }}
@font-face {{ font-family: 'Noto Serif Devanagari'; src: url("{F('static/NotoDeva-400.ttf')}"); font-weight: 400 500; }}
@font-face {{ font-family: 'Noto Serif Devanagari'; src: url("{F('static/NotoDeva-600.ttf')}"); font-weight: 600 700; }}
@page {{ size: 154mm 216mm; margin: 0; }}
:root {{ --indigo:#14183A; --ivory:#FBF5E6; --ivory-dim:#F1E7CE; --marigold:#F2A900; --gold-deep:#D69300; --magenta:#B0285F; --teal:#0E6B6B;
  --ink:#1B1F45; --paper:#F4EFE3;
  --display:'Cormorant Garamond', serif; --script:'Great Vibes', cursive; --body:'Jost', sans-serif; --deva:'Noto Serif Devanagari', serif; }}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ color: var(--ink); font-family: var(--body); font-size: 9.6pt; line-height: 1.5; }}
.date, .when, .h2, .who {{ font-variant-numeric: lining-nums; }}
.page {{ width: 154mm; height: 216mm; position: relative; overflow: hidden; break-after: page; page-break-after: always; }}
.page:last-child {{ break-after: auto; page-break-after: auto; }}
/* everything that must not be trimmed stays 10 mm inside the trim, i.e. 13 mm from the page edge */
.safe {{ position: absolute; inset: 13mm; display: flex; flex-direction: column; }}
.paper {{ background-color: var(--paper); background-image: {GRAIN}; background-size: 26mm 26mm; }}
.band {{ height: 11mm; background-image: {BAND}; background-size: 4.4mm 11mm; background-repeat: repeat-x; background-position: 50% 0; flex: none; }}
.kicker {{ font: 500 7.2pt/1.4 var(--body); letter-spacing: .22em; text-transform: uppercase; color: var(--teal); }}
.h2 {{ font-family: var(--display); font-weight: 600; font-size: 22pt; line-height: 1.08; margin-top: 1.6mm; }}
.h2-ne {{ font-family: var(--deva); font-weight: 600; font-size: 10.5pt; color: var(--teal); margin-top: 1mm; }}
.intro {{ font-family: var(--display); font-style: italic; font-size: 12.5pt; line-height: 1.38; margin-top: 4mm; }}
.intro-ne {{ font-family: var(--deva); font-size: 8.6pt; line-height: 1.75; color: var(--teal); margin-top: 1.5mm; }}
.tbc {{ border-bottom: 1.2pt dashed var(--marigold); }}
.ne {{ font-family: var(--deva); }}

/* Cover */
.cover {{ background: var(--indigo); color: var(--ivory); }}
.cover .safe {{ align-items: center; text-align: center; inset: 15mm 13mm 12mm; }}
.arch {{ position: relative; width: 92mm; height: 100mm; flex: none; }}
.arch .win {{ position: absolute; inset: 0; border-radius: 46mm 46mm 0 0; overflow: hidden; background: url("{COVER}") 50% 18% / cover no-repeat; }}
.arch::after {{ content: ""; position: absolute; inset: -2.2mm; border: .6pt solid var(--marigold); border-bottom: 0; border-radius: 48.2mm 48.2mm 0 0; }}
.arch::before {{ content: ""; position: absolute; left: -6mm; right: -6mm; bottom: -2.2mm; border-bottom: .6pt solid var(--marigold); }}
.hosts {{ font-family: var(--display); font-style: italic; font-size: 11pt; color: var(--ivory-dim); margin-top: 8mm; }}
.names {{ font-family: var(--script); font-size: 40pt; line-height: 1.05; margin-top: 1mm; }}
.names-ne {{ font-family: var(--deva); font-weight: 600; font-size: 12pt; color: var(--ivory-dim); margin-top: .5mm; }}
.when {{ font-family: var(--display); font-style: italic; font-size: 12pt; margin-top: 2mm; }}
.when .tbc {{ border-bottom-color: var(--marigold); }}
.cover .pj {{ width: 20mm; height: 23.1mm; flex: none; margin-top: auto; --pj-letters: var(--ivory); --pj-text: var(--marigold); }}

/* Invitation */
.blessing {{ display: flex; align-items: center; justify-content: center; gap: 4mm; margin: 5mm 0 4mm; }}
.mark {{ display: block; height: 13mm; width: auto; }}
.mark.knot {{ height: 12mm; }}
.dia {{ width: 1.8mm; height: 1.8mm; background: var(--marigold); transform: rotate(45deg); flex: none; }}
.dear {{ display: flex; align-items: baseline; gap: 2mm; font-family: var(--display); font-style: italic; font-size: 14pt; margin-bottom: 5mm; }}
.dear .line {{ flex: 1; border-bottom: .6pt solid rgba(20,24,58,.55); transform: translateY(-1.2mm); }}
.fam-lead {{ font-family: var(--display); font-style: italic; font-size: 11.5pt; color: var(--teal); margin-top: 5mm; }}
.fam-lead span {{ font-family: var(--deva); font-style: normal; font-size: 8.4pt; margin-left: 1.5mm; }}
.families {{ display: grid; gap: 4mm; margin-top: 3mm; }}
.fam {{ display: grid; grid-template-columns: 11mm 1fr; column-gap: 4mm; align-items: start; }}
.fam .mark {{ width: 11mm; height: auto; margin-top: .8mm; }}
.fam .mark.knot {{ width: 9.5mm; margin-left: .7mm; }}
.people {{ list-style: none; padding: 0; display: grid; gap: 2.2mm; }}
.people li {{ display: grid; }}
.role {{ font-family: var(--display); font-style: italic; font-weight: 500; font-size: 10pt; line-height: 1.25; color: var(--teal); }}
.role span {{ font-family: var(--deva); font-style: normal; font-size: 7.6pt; margin-left: .6mm; }}
.who {{ font-family: var(--display); font-weight: 600; font-size: 13pt; line-height: 1.2; }}
.who span {{ font-family: var(--deva); font-weight: 400; font-size: 8pt; opacity: .75; margin-left: 2mm; }}
.grow {{ flex: 1; }}
.inv .h2 {{ font-size: 24pt; }}
.inv .intro {{ font-size: 14pt; }}
.inv .intro-ne {{ font-size: 9.2pt; }}
.inv .dear {{ font-size: 15pt; margin-bottom: 6mm; }}
.inv .fam-lead {{ font-size: 12.5pt; margin-top: 6mm; }}
.inv .who {{ font-size: 14.5pt; }}
.inv .role {{ font-size: 11pt; }}
.inv .role span {{ font-size: 8.2pt; }}
.inv .who span {{ font-size: 8.8pt; }}
.inv .people {{ gap: 3mm; }}
.inv .families {{ gap: 5.5mm; }}
.inv .blessing .mark {{ height: 30mm; }}
.inv .blessing .mark.knot {{ height: 28mm; }}
.inv .blessing {{ gap: 6mm; margin: 4mm 0 5mm; }}
/* Both families on one page: a little tighter so it all fits between the bands */
.side-both .inv .blessing {{ margin: 1mm 0 3mm; }}
.side-both .inv .dear {{ margin-bottom: 4mm; }}
.side-both .inv .intro {{ margin-top: 3mm; }}
.side-both .inv .fam-lead {{ margin-top: 4mm; }}
.side-both .inv .families {{ gap: 3.5mm; margin-top: 2mm; }}
.side-both .inv .people {{ gap: 2mm; }}

/* Details */
.events {{ display: grid; gap: 5mm; margin-top: 5mm; }}
.event {{ display: grid; grid-template-columns: 1fr 24mm; column-gap: 5mm; border-top: .6pt solid rgba(20,24,58,.45); padding-top: 3.5mm; }}
.label {{ font: 500 7.2pt/1.4 var(--body); letter-spacing: .22em; text-transform: uppercase; color: var(--magenta); }}
.label-ne {{ font-family: var(--deva); font-size: 8pt; color: var(--teal); }}
.date {{ font-family: var(--display); font-weight: 600; font-size: 15pt; line-height: 1.15; margin-top: 1.5mm; }}
.date-ne, .line-ne {{ font-family: var(--deva); font-size: 8pt; line-height: 1.6; }}
.line {{ font-size: 9.4pt; margin-top: 1.4mm; }}
.place {{ font-weight: 500; }}
.qr {{ align-self: start; text-align: center; padding-top: 1mm; }}
.qr svg {{ width: 24mm; height: 24mm; display: block; }}
.qr p {{ font-size: 6.8pt; line-height: 1.3; margin-top: 1.5mm; color: var(--ink); }}
.qr p span {{ display: block; font-family: var(--deva); font-size: 6.4pt; color: var(--teal); }}
.travel {{ margin-top: 5mm; padding: 3.5mm 4mm; background: rgba(242,169,0,.14); border-left: .9mm solid var(--marigold); }}
.travel h3 {{ font-family: var(--display); font-weight: 600; font-size: 12.5pt; line-height: 1.2; }}
.travel p {{ font-size: 8.6pt; line-height: 1.5; margin-top: 1.2mm; }}
.travel .ne {{ font-size: 7.8pt; color: var(--teal); }}
.note {{ font-size: 8pt; opacity: .8; margin-top: 3.5mm; }}

/* Reply card */
.form {{ display: grid; gap: 4.6mm; margin-top: 6mm; }}
.field {{ display: grid; gap: 1.2mm; }}
.lbl {{ font: 500 7.2pt/1.4 var(--body); letter-spacing: .16em; text-transform: uppercase; color: var(--teal); }}
.lbl span {{ font-family: var(--deva); letter-spacing: 0; text-transform: none; font-size: 7.6pt; margin-left: 1mm; }}
.write {{ height: 7mm; border-bottom: .6pt solid rgba(20,24,58,.55); }}
.boxes {{ display: flex; flex-wrap: wrap; gap: 2mm 7mm; }}
.box {{ display: flex; align-items: center; gap: 2.2mm; font-size: 10pt; }}
.box i {{ width: 4.2mm; height: 4.2mm; border: .7pt solid var(--indigo); flex: none; }}
.box.round i {{ border-radius: 50%; }}
.box small {{ font-size: 8pt; opacity: .7; }}
.row2 {{ display: grid; grid-template-columns: 42mm 1fr; gap: 6mm; }}
.return {{ font-size: 8.4pt; line-height: 1.5; margin-top: auto; padding-top: 4mm; }}
.return .ne {{ display: block; font-size: 7.8pt; color: var(--teal); }}
'''

def fam_block(side):
    groom = f'''<div class="fam">{GANESHA}<ul class="people">
      <li><span class="role">Grandfather of the groom <span>· बेहुलाका हजुरबुबा</span></span><span class="who">Gorey Chhetri<span class="ne">गोरे क्षेत्री</span></span></li>
      <li><span class="role">Father of the groom <span>· बेहुलाका बुबा</span></span><span class="who">Anup Kumar Chhetri<span class="ne">अनुप कुमार क्षेत्री</span></span></li>
      <li><span class="role">Mother of the groom <span>· बेहुलाकी आमा</span></span><span class="who">Pramila Sampang<span class="ne">प्रमिला साम्पाङ</span></span></li>
    </ul></div>'''
    bride = f'''<div class="fam">{KNOT}<ul class="people">
      <li><span class="role">Father of the bride <span>· बेहुलीका बुबा</span></span><span class="who">Kiran Tamang<span class="ne">किरण तामाङ</span></span></li>
      <li><span class="role">Mother of the bride <span>· बेहुलीकी आमा</span></span><span class="who">Manju Tamang<span class="ne">मन्जु तामाङ</span></span></li>
    </ul></div>'''
    return {'groom': groom, 'bride': bride, 'both': groom + bride}[side]

WEDDING = f'''<div class="event"><div>
    <p class="label">Wedding</p><p class="label-ne">विवाह समारोह</p>
    <p class="date">Wednesday, 10 February 2027</p><p class="date-ne">बुधबार, १० फेब्रुअरी २०२७</p>
    <p class="line">11:00 AM <span class="line-ne">· बिहान ११:०० बजे</span></p>
    <p class="line place">Gymkhana, Darjeeling, West Bengal</p><p class="line-ne">जिमखाना, दार्जिलिङ</p>
  </div><div class="qr">{qr(MAP_WEDDING)}<p>Scan for the map<span>नक्साका लागि स्क्यान गर्नुहोस्</span></p></div></div>'''
RECEPTION = f'''<div class="event"><div>
    <p class="label">Reception</p><p class="label-ne">स्वागत समारोह</p>
    <p class="date"><span class="tbc">[Friday 12 / Saturday 13]</span> February 2027</p><p class="date-ne">[१२ / १३] फेब्रुअरी २०२७</p>
    <p class="line">11:00 AM <span class="line-ne">· बिहान ११:०० बजे</span></p>
    <p class="line place"><span class="tbc">[Venue name]</span>, Gorubathan, West Bengal</p><p class="line-ne">[स्थान], गोरुबथान</p>
  </div><div class="qr">{qr(MAP_RECEPTION)}<p>Scan for the map<span>नक्साका लागि स्क्यान गर्नुहोस्</span></p></div></div>'''

T = {  # wording per side
    'both':  dict(hosts='We invite you to the wedding of', when='10 February 2027 · Darjeeling &amp; Gorubathan',
                  kicker='The celebrations', h2='Two days to be with us', h2ne='उत्सवका दिनहरू', marks=f'{GANESHA}<i class="dia"></i>{KNOT}',
                  events=WEDDING + RECEPTION, dest='Darjeeling', arrive='<b>Arrive by 9 February.</b> The wedding starts at 11 AM on the 10th, and the drive up into the hills takes about 3 hours.'),
    'bride': dict(hosts='We invite you to the wedding of', when='Wednesday, 10 February 2027 · Darjeeling',
                  kicker='The wedding', h2='Join us for our wedding', h2ne='विवाह समारोह', marks=KNOT,
                  events=WEDDING, dest='Darjeeling', arrive='<b>Arrive by 9 February.</b> The wedding starts at 11 AM on the 10th, and the drive up into the hills takes about 3 hours.'),
    'groom': dict(hosts='We invite you to the wedding reception of', when='<span class="tbc">[12 / 13]</span> February 2027 · Gorubathan',
                  kicker='The reception', h2='Join us for our reception', h2ne='स्वागत समारोह', marks=GANESHA,
                  events=RECEPTION, dest='Gorubathan', arrive='<b>Arrive the day before the reception.</b> It starts at 11 AM, and the drive from Bagdogra takes about 3 hours.'),
}

def page_html(side):
    t = T[side]
    both_events = side == 'both'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Pranup &amp; Jaya - invitation ({side})</title>
<style>{CSS}</style></head><body class="side-{side}">{DEFS}

<section class="page cover"><div class="safe">
  <div class="arch"><div class="win" role="img" aria-label="Watercolour of a lighthouse at dusk"></div></div>
  <p class="hosts">{t["hosts"]}</p>
  <p class="names">Pranup &amp; Jaya</p>
  <p class="names-ne">प्रनुप र जया</p>
  <p class="when">{t["when"]}</p>
  <svg class="pj" role="img" aria-label="PJ monogram"><use href="#pj"/></svg>
</div></section>

<section class="page paper inv"><div class="safe">
  <div class="band"></div>
  <div class="grow"></div>
  <div class="blessing">{t["marks"]}</div>
  <p class="dear">Dear <span class="line"></span>,</p>
  <p class="kicker">{t["kicker"]}</p>
  <p class="h2">{t["h2"]}</p>
  <p class="h2-ne">{t["h2ne"]}</p>
  <p class="intro">With joy in our hearts, we invite you to celebrate our wedding.</p>
  <p class="intro-ne">हामी विवाह बन्धनमा बाँधिँदै छौँ, र यो खुशीको क्षणमा सहभागी हुन तपाईँलाई हार्दिक निमन्त्रणा गर्दछौँ।</p>
  <p class="fam-lead">With love, <span>शुभेच्छासहित</span></p>
  <div class="families">{fam_block(side)}</div>
  <div class="grow"></div>
  <div class="band"></div>
</div></section>

<section class="page paper"><div class="safe">
  <div class="band"></div>
  <p class="kicker" style="margin-top:6mm">When and where</p>
  <p class="h2">{"The two days" if both_events else ("The wedding day" if side == "bride" else "The reception")}</p>
  <p class="h2-ne">कहिले र कहाँ</p>
  <div class="events">{t["events"]}</div>
  <div class="travel">
    <h3>Coming from abroad? Fly to Bagdogra.</h3>
    <p>Fly into Delhi, Kolkata, Mumbai or Bengaluru, then take a direct flight to Bagdogra (IXB). Send us your flight and landing time, and one of us will meet you at arrivals and drive you to {t["dest"]}.</p>
    <p>{t["arrive"]}</p>
    <p class="ne">बागडोगरा विमानस्थलसम्म आउनुहोस्, त्यहाँबाट हामी तपाईँलाई लिन आउनेछौँ।</p>
  </div>
  <p class="note">Times may change slightly; we will let you know.</p>
  <div class="grow"></div>
  <div class="band"></div>
</div></section>

<section class="page paper"><div class="safe">
  <div class="band"></div>
  <p class="kicker" style="margin-top:6mm">RSVP</p>
  <p class="h2">Let us know if you can come</p>
  <p class="h2-ne">उपस्थिति जनाउनुहोस्</p>
  <div class="form">
    <div class="field"><p class="lbl">Your name</p><div class="write"></div></div>
    <div class="field"><p class="lbl">Will you join us?</p>
      <div class="boxes"><span class="box round"><i></i>Joyfully accepts</span><span class="box round"><i></i>Regretfully declines</span></div></div>
    {'<div class="field"><p class="lbl">Which celebrations?</p><div class="boxes"><span class="box"><i></i>Wedding <small>10 Feb, Darjeeling</small></span><span class="box"><i></i>Reception <small>Gorubathan</small></span></div></div>' if both_events else ''}
    <div class="row2">
      <div class="field"><p class="lbl">How many of you?</p><div class="write"></div></div>
      <div class="field"><p class="lbl">Food needs</p><div class="write"></div></div>
    </div>
    <div class="field"><p class="lbl">Flying in? Flight, date and landing time at Bagdogra</p><div class="write"></div></div>
    <div class="field"><p class="lbl">A note for us</p><div class="write"></div><div class="write"></div><div class="write"></div></div>
  </div>
  <p class="return">Please fill this in and hand it back to us, or send the same details to {RSVP_EMAIL}.
    <span class="ne">कृपया यो कार्ड भरेर हामीलाई फिर्ता दिनुहोस्।</span></p>
  <div class="band" style="margin-top:4mm"></div>
</div></section>
</body></html>'''

if __name__ == '__main__':
    names = {'both': 'Pranup-Jaya-invitation-both-families.pdf', 'bride': 'Pranup-Jaya-invitation-brides-side.pdf',
             'groom': 'Pranup-Jaya-invitation-grooms-side.pdf'}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for side, fname in names.items():
            path = os.path.join(OUT, f'print-{side}.html')  # intermediate page, kept with the PDFs
            open(path, 'w').write(page_html(side))
            pg = b.new_page()
            pg.goto('file://' + path); pg.wait_for_timeout(600)
            pg.evaluate('document.fonts.ready')
            pg.pdf(path=os.path.join(OUT, fname), width='154mm', height='216mm', print_background=True, prefer_css_page_size=True)
            pg.close()
            print('wrote', fname)
        b.close()
