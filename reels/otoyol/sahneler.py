"""Otoyol kesik çizgi reeli sahne parçaları (zamanlar parametre). Koordinatlar 1080×1920 sayfa, görsel alan 200-1410, yanlar 100-980.
DİKKAT: transform özniteliği olan SVG <g>'yi GSAP ile oynatma; dışına id'li boş <g> sar."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from roadart import ASPHALT, GRASS, PAINT, SHOULDER, YELLOW, car_top, road_top, tape  # noqa: E402


def pop_js(sel, t, s0=.4, dur=.3):
    return (f'tl.fromTo("{sel}",{{scale:{s0},opacity:0}},{{scale:1,opacity:1,duration:{dur},ease:"back.out(2.4)",immediateRender:false}},{t:.2f});'
            f'tl.set("{sel}",{{opacity:0}},0);')


# ---------------- KUŞ BAKIŞI ÖLÇEK: drone iner, çizginin yanına otomobil gelir, 6 m / 9 m ----------------
S_END = .75                     # px/cm (son yakınlık): 6 m = 450 px, 9 m = 675 px
L_CM = 9000                     # gösterilen yol uzunluğu (6 döngü)
LANES = 3


def olcek_html(dash=600, gap=900):
    H = LANES * 375
    road = road_top(L_CM, dash, gap, s=1, lanes=LANES, offset=150, idp="ol")
    grass = f'<rect x="-4000" y="-4000" width="{L_CM + 8000}" height="{H + 8000}" fill="{GRASS}"/>'
    # yol dikey: rotate(-90) → x ekseni yukarı; merkez (L/2, H/2)
    world = f'<g transform="rotate(-90) translate({-L_CM / 2} {-H / 2})">{grass}{road}</g>'
    car = f'<g id="olcar"><g transform="rotate(-90)">{car_top("#E8423A")}</g></g>'
    return (f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:hidden"><g id="olw" transform="translate(540 805)"><g id="olz">{world}{car}</g></g>'
            f'<g id="oltp"></g></svg>')


def olcek_js(t0, t_zoom, t_car, t_tape6, t_tape9, zoom_dur=1.6):
    """t0: yüksekten (0,22 px/cm) başlar ve yavaş alçalır; t_zoom: tek çizgiye iner; t_car: araç gelip yanına durur; tape: ölçü bantları."""
    return (f'tl.fromTo("#olz",{{scale:.2,rotation:-6,svgOrigin:"0 0"}},{{scale:.26,rotation:0,duration:{t_zoom - t0:.2f},ease:"none",immediateRender:false}},{t0:.2f});tl.set("#olz",{{scale:.2,svgOrigin:"0 0"}},0);'
            f'tl.to("#olz",{{scale:{S_END},duration:{zoom_dur},ease:"power3.inOut"}},{t_zoom:.2f});')
