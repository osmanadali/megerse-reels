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


U_C = 5100                      # görüntü merkezindeki yol konumu (cm): 4350-4950 çizgi, 4950-5850 boşluk
CY = 805


def vtape(x, y0, y1, label, col=YELLOW, fs=44, side=-1, idn=""):
    """dikey ölçü bandı (sayfa koordinatı); etiket bandın solunda (side=-1) ya da sağında."""
    i = f' id="{idn}"' if idn else ""
    lx = x + side * 26
    return (f'<g{i}><path d="M{x} {y0} V{y1} M{x-16} {y0} H{x+16} M{x-16} {y1} H{x+16}" stroke="#1B1414" stroke-width="13" stroke-linecap="round"/>'
            f'<path d="M{x} {y0} V{y1} M{x-16} {y0} H{x+16} M{x-16} {y1} H{x+16}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<text x="{lx}" y="{(y0 + y1) / 2 + fs * .35:.0f}" text-anchor="{"end" if side < 0 else "start"}" font-family="Mont" font-weight="800" font-size="{fs}" fill="{col}" '
            f'stroke="#1B1414" stroke-width="9" paint-order="stroke">{label}</text></g>')


def olcek_html(dash=600, gap=900, car_label="OTOMOBİL"):
    H = LANES * 375
    road = road_top(L_CM, dash, gap, s=1, lanes=LANES, offset=150, idp="ol")
    grass = f'<rect x="-6000" y="-6000" width="{L_CM + 12000}" height="{H + 12000}" fill="{GRASS}"/>'
    world = f'<g transform="rotate(-90) translate({-U_C} {-H / 2})">{grass}{road}</g>'
    car = f'<g id="olcar"><g transform="translate(0 {(U_C - 4650):.0f}) rotate(-90)">{car_top("#E8423A")}</g></g>'
    S = S_END
    xd = 540 + (375 - H / 2) * S                      # sol şerit çizgisi
    y_d0, y_d1 = CY + (U_C - 4950) * S, CY + (U_C - 4350) * S
    y_g0 = CY + (U_C - 5850) * S
    tapes = (vtape(xd - 44, y_d0 + 6, y_d1 - 6, "6 METRE", idn="tp6") + vtape(xd - 44, max(y_g0, 215) + 6, y_d0 - 6, "9 METRE", col="#FFFFFF", idn="tp9")
             + f'<g id="tpc">{vtape(540 + 150, CY + (U_C - 4650 - 225) * S, CY + (U_C - 4650 + 225) * S, car_label, col="#FFFFFF", fs=36, side=1)}</g>')
    return (f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:hidden"><g transform="translate(540 {CY})"><g id="olz">{world}{car}</g></g>'
            f'{tapes}</svg>')


def olcek_js(t0, t_zoom, t_car, t_tape6, t_tape9, t_carlbl=None, zoom_dur=1.6):
    """t0: yüksekten (0,2 px/cm) başlar, yavaş alçalır; t_zoom: tek çizgiye iner; t_car: araç gelip yanına durur; tape: ölçü bantları."""
    js = (f'tl.fromTo("#olz",{{scale:.2,rotation:-8,svgOrigin:"0 0"}},{{scale:.27,rotation:0,duration:{t_zoom - t0:.2f},ease:"none",immediateRender:false}},{t0:.2f});tl.set("#olz",{{scale:.2,rotation:-8,svgOrigin:"0 0"}},0);'
          f'tl.to("#olz",{{scale:{S_END},duration:{zoom_dur},ease:"power3.inOut"}},{t_zoom:.2f});'
          f'tl.fromTo("#olcar",{{y:2600,opacity:1}},{{y:0,duration:1.1,ease:"power3.out",immediateRender:false}},{t_car:.2f});tl.set("#olcar",{{y:2600,opacity:0}},0);')
    for sel, t in (("#tp6", t_tape6), ("#tp9", t_tape9), ("#tpc", t_carlbl)):
        if t:
            js += (f'tl.fromTo("{sel}",{{opacity:0,scaleY:0,transformOrigin:"50% 50%"}},{{opacity:1,scaleY:1,duration:.35,ease:"back.out(1.8)",immediateRender:false}},{t:.2f});'
                   f'tl.set("{sel}",{{opacity:0}},0);')
    return js
