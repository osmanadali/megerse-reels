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


# ---------------- POV: yol üstünde ilerleyen kamera (gündüz / sis / sarı / gece) ----------------
POV_CSS = """
.hud { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:12px 30px; border-radius:22px; background:rgba(8,12,20,.82); border:4px solid #fff;
       color:#fff; font-weight:800; font-size:54px; text-align:center; opacity:0; }
.hud b { color:#FFD23F; font-size:96px; display:inline-block; min-width:1.6em; }
.hud small { display:block; font-size:30px; color:#C9D4DE; }
"""
SKY = {"gun": "linear-gradient(180deg,#5E9BD6 0%,#BFD6E8 33%,#E6EDF2 37%)",
       "sis": "linear-gradient(180deg,#B9C2CA 0%,#D8DEE3 33%,#E4E8EB 38%)",
       "gece": "linear-gradient(180deg,#05070E 0%,#101828 33%,#1A2234 37%)"}


def pov_scene(cam, sid, dash=600, gap=900, paint=None, cones=False, guard=True, z1=60000, night=False):
    from roadart import PAINT as P, cone, guard_post, highway
    sc = highway(cam, sid=sid, dash=dash, gap=gap, paint=paint or ("#FFF6D0" if night else P), z1=z1, night=night)
    if guard:
        for z in range(-1000, z1, 800):
            sc.add(375 * 1.5 + 260, z, guard_post(), 75, 75, shadow=False)
    if cones:
        for z in range(1500, z1, 900):
            sc.add(375 * .5 - 30, z, cone(), 75, 75, shadow=False)
    return sc


def pov_html(sc, mood="gun", fog=False, night=False, hud=""):
    over = ""
    if fog:
        over += '<div class="fill" style="background:linear-gradient(180deg,rgba(228,232,235,0) 0%,rgba(228,232,235,.96) 36%,rgba(228,232,235,.75) 46%,rgba(228,232,235,.25) 62%,rgba(228,232,235,0) 80%)"></div>'
    if night:
        over += ('<div class="fill" style="background:radial-gradient(60% 34% at 50% 78%,rgba(255,240,190,.22),rgba(0,0,0,0) 70%),'
                 'linear-gradient(180deg,rgba(0,0,0,0) 36%,rgba(0,0,0,.55) 100%)"></div>')
    return f'<div class="fill" style="background:{SKY[mood]}"></div>{sc.svg()}{over}{hud}'


def pov_js(sc, sid, t0, dur, speed_kmh=120, ease="none", counter=None, cycle=1500):
    """kamera hızı gerçek: km/sa → cm/sn. counter=(element id, t_on): geçilen çizgi sayısını yazar."""
    v = speed_kmh * 100000 / 3600
    js = sc.js() + f"window.PROJ_{sid}();" + sc.camera_js(t0, dur, dz=round(v * dur), ease=ease)
    if counter:
        cid, t_on = counter
        js += (f'(function(){{const o={{v:0}};tl.to(o,{{v:{v * dur / cycle:.3f},duration:{dur},ease:"{ease}",'
               f'onUpdate:()=>{{const e=document.getElementById("{cid}");if(e)e.textContent=Math.floor(o.v);}}}},{t0:.2f});}})();'
               + pop_js(f"#{cid}w", t_on))          # sayaç kabı: id="<cid>w"
    return js


# ---------------- YOL TÜRLERİ: üç şerit yan yana akar (aynı hız, farklı ritim) ----------------
TUR_CSS = """
.turl { position:absolute; top:250px; width:270px; text-align:center; font-weight:800; font-size:34px; line-height:1.1; color:#fff; text-shadow:0 4px 0 #000; opacity:0; }
.turl b { display:block; font-size:44px; color:#FFD23F; white-space:nowrap; }
"""
TUR = [("OTOYOL", 600, 900, "6 + 9 m"), ("ŞEHİRLERARASI", 450, 750, "4,5 + 7,5 m"), ("ŞEHİR İÇİ", 300, 300, "3 + 3 m")]


def turler_html(scale=.36, top=420, bottom=1400, travel=4400, tur=TUR):
    """her kolon: dikey yol şeridi parçası; kesik çizgi deseni yukarıdan aşağı akar (turler_js travel kadar kaydırır)."""
    defs, body = [], []
    for i, (name, d, g, lab) in enumerate(tur):
        cx, w = 205 + i * 335, 230
        y, dashes = top - travel - (d + g) * scale, []
        while y < bottom + (d + g) * scale:
            dashes.append(f'<rect x="{cx - 7}" y="{y:.1f}" width="14" height="{d * scale:.1f}" fill="{PAINT}"/>')
            y += (d + g) * scale
        defs.append(f'<clipPath id="tc{i}"><rect x="{cx - w / 2}" y="{top}" width="{w}" height="{bottom - top}" rx="18"/></clipPath>')
        body.append(f'<g clip-path="url(#tc{i})"><rect x="{cx - w / 2}" y="{top}" width="{w}" height="{bottom - top}" fill="{ASPHALT}"/>'
                    f'<g id="ts{i}">{"".join(dashes)}</g>'
                    f'<g transform="translate({cx + 58} {bottom - 230}) rotate(-90) scale({scale:.3f})">{car_top(["#E8423A", "#2F6FD0", "#2FB36E"][i])}</g></g>'
                    f'<rect x="{cx - w / 2}" y="{top}" width="{w}" height="{bottom - top}" rx="18" fill="none" stroke="#1B1414" stroke-width="6"/>')
    labs = "".join(f'<div class="turl" id="tl{i}" style="left:{205 + i * 335 - 135}px">{name}<b>{lab}</b></div>' for i, (name, d, g, lab) in enumerate(tur))
    return f'<svg class="fill" viewBox="0 0 1080 1920"><defs>{"".join(defs)}</defs>{"".join(body)}</svg>{labs}'


def turler_js(t0, dur, t_labels, speed_px=520, tur=TUR):
    """aynı hızla akar (speed_px px/sn, travel'ı aşmamalı): ritim farkı göze çarpar."""
    js = ""
    for i, (name, d, g, lab) in enumerate(tur):
        js += f'tl.fromTo("#ts{i}",{{y:0}},{{y:{speed_px * dur:.0f},duration:{dur},ease:"none",immediateRender:false}},{t0:.2f});'
        js += pop_js(f"#tl{i}", t_labels[i])
    return js
