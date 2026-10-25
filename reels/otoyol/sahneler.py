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
    lines = label.split("\n")
    y_mid = (y0 + y1) / 2 + fs * .35 - (len(lines) - 1) * fs * .55
    spans = "".join(f'<tspan x="{lx}" dy="{0 if k == 0 else fs * 1.1:.0f}">{ln}</tspan>' for k, ln in enumerate(lines))
    return (f'<g{i}><path d="M{x} {y0} V{y1} M{x-16} {y0} H{x+16} M{x-16} {y1} H{x+16}" stroke="#1B1414" stroke-width="13" stroke-linecap="round"/>'
            f'<path d="M{x} {y0} V{y1} M{x-16} {y0} H{x+16} M{x-16} {y1} H{x+16}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<text x="{lx}" y="{y_mid:.0f}" text-anchor="{"end" if side < 0 else "start"}" font-family="Mont" font-weight="800" font-size="{fs}" fill="{col}" '
            f'stroke="#1B1414" stroke-width="9" paint-order="stroke">{spans}</text></g>')


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
    js = ('' + f'tl.fromTo("#olz",{{scale:.2,rotation:-8,svgOrigin:"0 0"}},{{scale:.27,rotation:0,duration:{t_zoom - t0:.2f},ease:"none",immediateRender:false}},{t0:.2f});tl.set("#olz",{{scale:.2,rotation:-8,svgOrigin:"0 0"}},0);'
          f'tl.to("#olz",{{scale:{S_END},duration:{zoom_dur},ease:"power3.inOut"}},{t_zoom:.2f});'
          + (f'tl.fromTo("#olcar",{{y:2600,opacity:1}},{{y:0,duration:1.1,ease:"power3.out",immediateRender:false}},{t_car:.2f});' if t_car else "")
          + 'tl.set("#olcar",{y:2600,opacity:0},0);')
    for sel, t in (("#tp6", t_tape6), ("#tp9", t_tape9), ("#tpc", t_carlbl)):
        js += f'tl.set("{sel}",{{opacity:0}},0);'
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
TUR = [("OTOYOL", 600, 900, "6 + 9 m"), ("DEVLET YOLU", 450, 750, "4,5 + 7,5 m"), ("ŞEHİR İÇİ", 300, 300, "3 + 3 m")]


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


# ---------------- KIYAS: gerçek çizgi ile tahmin aynı ölçekte (kuş bakışı) ----------------
KIYAS_CSS = """
.ktag2 { position:absolute; left:0; right:0; margin:0 auto; top:200px; width:fit-content; padding:12px 24px; border-radius:16px; background:rgba(10,14,22,.88);
         border:3px solid #fff; color:#fff; font-weight:800; font-size:38px; opacity:0; }
.kspd { position:absolute; right:120px; top:300px; width:250px; padding:10px 0 14px; border-radius:20px; background:rgba(8,12,20,.85); border:4px solid #fff;
        text-align:center; color:#fff; font-weight:800; font-size:30px; opacity:0; }
.kspd b { display:block; font-size:80px; color:#FFD23F; line-height:1; }
"""


def kiyas_html(real_cm, guess_cm, real_lab, guess_lab, tag, idp="kz", s=None, speed=False):
    """kuş bakışı iki şeritli yol parçası: ortadaki çizgi gerçek boy, sağdaki sarı çubuk tahmin (aynı ölçek). s px/cm (vars: gerçek çizgi ~560 px)."""
    s = s or 560 / real_cm
    y1 = 1330                           # çizgilerin alt ucu
    y0 = y1 - real_cm * s
    lane = min(375 * s, 420)
    cx = 470
    w = max(15 * s, 6)
    road = (f'<rect x="{cx - lane - 40}" y="0" width="{2 * lane + 80}" height="1920" fill="{SHOULDER}"/>'
            f'<rect x="{cx - lane}" y="0" width="{2 * lane}" height="1920" fill="{ASPHALT}"/>'
            f'<rect x="{cx - lane + 12}" y="0" width="{w:.1f}" height="1920" fill="{PAINT}"/><rect x="{cx + lane - 12 - w:.1f}" y="0" width="{w:.1f}" height="1920" fill="{PAINT}"/>')
    dash = (f'<rect id="{idp}h" x="{cx - w / 2 - 3:.1f}" y="{y0:.1f}" width="{w + 6:.1f}" height="{real_cm * s:.1f}" fill="none" stroke="{PAINT}" stroke-width="3" stroke-dasharray="14 10" opacity=".55"/>'
            f'<text id="{idp}q" x="{cx}" y="{(y0 + y1) / 2 + 40:.0f}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="120" fill="{PAINT}" opacity=".7">?</text>'
            f'<rect id="{idp}r" x="{cx - w / 2:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{real_cm * s:.1f}" fill="{PAINT}"/>')
    gx = cx + 190
    guess = f'<g id="{idp}g"><rect x="{gx - w / 2:.1f}" y="{y1 - guess_cm * s:.1f}" width="{w:.1f}" height="{guess_cm * s:.1f}" fill="{YELLOW}" stroke="#1B1414" stroke-width="3"/></g>'
    t_real = f'<g id="{idp}tr">{vtape(cx - 46, y0 + 4, y1 - 4, real_lab, col="#FFFFFF", fs=52)}</g>'
    t_guess = f'<g id="{idp}tg">{vtape(gx + 34, y1 - guess_cm * s + 2, y1 - 2, guess_lab, col=YELLOW, fs=40, side=1)}</g>'
    hud = '<div class="kspd" id="kspd">HIZ<b id="kspdn">40</b>km/sa</div>' if speed else ""
    return (f'<svg class="fill" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="{GRASS}"/><g id="{idp}w">{road}{dash}{guess}{t_real}{t_guess}</g></svg>'
            f'<div class="ktag2" id="{idp}tag">{tag}</div>{hud}')


def kiyas_js(t0, t_guess, t_real, idp="kz", t_speed=None, dur=None):
    js = (pop_js(f"#{idp}tag", t0 + .1)
          + f'tl.fromTo("#{idp}w",{{scale:1.12,transformOrigin:"540px 1000px"}},{{scale:1,duration:{(dur or 4):.2f},ease:"power1.out",immediateRender:false}},{t0:.2f});'
          + f'tl.set("#{idp}r,#{idp}tr",{{opacity:0}},0);tl.set("#{idp}g,#{idp}tg",{{opacity:0}},0);'
          + f'tl.fromTo("#{idp}g",{{scaleY:0,transformOrigin:"50% 100%",opacity:1}},{{scaleY:1,duration:.4,ease:"back.out(2)",immediateRender:false}},{t_guess:.2f});'
          + f'tl.to("#{idp}tg",{{opacity:1,duration:.25}},{t_guess + .3:.2f});'
          + f'tl.to("#{idp}q",{{opacity:0,duration:.2}},{t_real:.2f});tl.to("#{idp}h",{{opacity:0,duration:.3}},{t_real + .7:.2f});'
          + f'tl.fromTo("#{idp}r",{{scaleY:0,transformOrigin:"50% 100%",opacity:1}},{{scaleY:1,duration:.8,ease:"power2.out",immediateRender:false}},{t_real:.2f});'
          + f'tl.to("#{idp}tr",{{opacity:1,duration:.25}},{t_real + .6:.2f});')
    if t_speed:
        a, b = t_speed
        js += (pop_js("#kspd", a - .3) + f'(function(){{const o={{v:40}};tl.to(o,{{v:97,duration:{b - a:.2f},ease:"power1.inOut",'
               f'onUpdate:()=>{{document.getElementById("kspdn").textContent=Math.round(o.v);}}}},{a:.2f});}})();')
    return js


# ---------------- ÜLKELER: üç çizgi aynı anda boyanır, kısalar durur ----------------
ULKE_CSS = """
.ulab { position:absolute; width:300px; text-align:center; font-weight:800; font-size:38px; color:#fff; text-shadow:0 4px 0 #000; opacity:0; }
.ulab b { display:block; font-size:56px; color:#FFD23F; }
.umul { position:absolute; width:300px; text-align:center; font-weight:800; font-size:96px; color:#FF5A4E; -webkit-text-stroke:5px #000; paint-order:stroke fill; opacity:0; }
"""
ULKE = [("TÜRKİYE", 600, "6 m", ""), ("ABD", 305, "3,05 m", "×2"), ("İNGİLTERE", 200, "2 m", "×3")]


def ulke_html(s=1.45, base=1360):
    cols, labs = [], []
    for i, (name, cm, lab, mul) in enumerate(ULKE):
        cx = 220 + i * 320
        cols.append(f'<rect x="{cx - 90}" y="{base - 900}" width="180" height="960" rx="16" fill="{ASPHALT}" stroke="#1B1414" stroke-width="6"/>'
                    f'<rect class="ub" id="ub{i}" x="{cx - 11}" y="{base - cm * s:.1f}" width="22" height="{cm * s:.1f}" fill="{PAINT}"/>')
        labs.append(f'<div class="ulab" id="ul{i}" style="left:{cx - 150}px;top:{base - 900 - 130}px">{name}<b>{lab}</b></div>')
        if mul:
            labs.append(f'<div class="umul" id="um{i}" style="left:{cx - 150}px;top:{base - cm * s - 150:.0f}px">{mul}</div>')
    return f'<svg class="fill" viewBox="0 0 1080 1920">{"".join(cols)}</svg>{"".join(labs)}'


def ulke_js(t0, t_paint, t_mul, s=1.45):
    """üç çizgi aynı hızla boyanır (sabit cm/sn): kısa olanlar önce durur."""
    v = 600 / 1.6                          # cm/sn: Türk çizgisi 1,6 sn'de biter
    js = "".join(pop_js(f"#ul{i}", t0 + .15 * i) for i in range(3))
    for i, (name, cm, lab, mul) in enumerate(ULKE):
        js += (f'tl.fromTo("#ub{i}",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:{cm / v:.2f},ease:"none",immediateRender:false}},{t_paint:.2f});'
               f'tl.set("#ub{i}",{{scaleY:0,transformOrigin:"50% 100%"}},0);')
        if mul:
            js += pop_js(f"#um{i}", t_mul + (.25 if i == 2 else 0), 2, .3)
    return js


# ---------------- CAM KÜRE: kesit, far ışını küreye girer ve geri döner ----------------
KURE_CSS = """
.kur { position:absolute; font-weight:800; font-size:40px; color:#fff; text-shadow:0 4px 0 #000; opacity:0; }
"""


def kure_html():
    beads = []
    for i, (x, r) in enumerate([(150, 95), (370, 130), (600, 105), (820, 140), (1010, 90)]):
        y = 1060 + r * .15
        beads.append(f'<g class="kb" id="kb{i}"><circle cx="{x}" cy="{y:.0f}" r="{r}" fill="url(#glassg)" stroke="#1B1414" stroke-width="6"/>'
                     f'<path d="M{x - r * .55:.0f} {y - r * .35:.0f} A{r * .6:.0f} {r * .6:.0f} 0 0 1 {x - r * .05:.0f} {y - r * .62:.0f}" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" opacity=".85"/></g>')
    paint = ('<path d="M0 1080 L1080 1080 L1080 1280 L0 1280 Z" fill="#F4F1E6" stroke="#1B1414" stroke-width="6"/>'
             '<path d="M0 1280 L1080 1280 L1080 1920 L0 1920 Z" fill="#3E4046"/>'
             + "".join(f'<circle cx="{(k * 97) % 1080}" cy="{1320 + (k * 53) % 380}" r="{6 + k % 5}" fill="#2E3036"/>' for k in range(40)))
    ray_in = "M60 260 L760 960"
    ray_back = "M870 1000 L820 1120 L760 1010 L90 300"
    return (f'<svg class="fill" viewBox="0 0 1080 1920"><defs><radialGradient id="glassg" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/>'
            f'<stop offset=".5" stop-color="#CFEFFF" stop-opacity=".6"/><stop offset="1" stop-color="#7AB8D8" stop-opacity=".75"/></radialGradient>'
            f'<filter id="rayglow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter></defs>'
            f'<rect width="1080" height="1920" fill="#06080E"/>{"".join(beads)}{paint}'
            f'<path id="kray1" d="{ray_in}" stroke="#FFE680" stroke-width="18" fill="none" stroke-linecap="round" filter="url(#rayglow)" opacity=".9"/>'
            f'<path id="kray1c" d="{ray_in}" stroke="#FFF8D8" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path id="kray2" d="{ray_back}" stroke="#FFB02A" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#rayglow)" opacity=".9"/>'
            f'<path id="kray2c" d="{ray_back}" stroke="#FFF0C8" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
            '<div class="kur" id="kurl1" style="left:130px;top:1170px;color:#1B1414;text-shadow:none">BOYA</div><div class="kur" id="kurl2" style="left:690px;top:800px">CAM KÜRE</div>'
            '<div class="kur" id="kurl3" style="left:130px;top:210px">FAR IŞIĞI</div>')


def kure_js(t0, t_ray, t_back):
    L1, L2 = 1000, 1250
    js = (f'tl.fromTo(".kb",{{y:-700,opacity:0}},{{y:0,opacity:1,duration:.45,stagger:.08,ease:"bounce.out",immediateRender:false}},{t0:.2f});tl.set(".kb",{{opacity:0}},0);'
          + pop_js("#kurl1", t0 + .3) + pop_js("#kurl2", t0 + .7) + pop_js("#kurl3", t_ray - .2))
    for sel in ("#kray1", "#kray1c"):
        js += f'tl.fromTo("{sel}",{{strokeDasharray:{L1},strokeDashoffset:{L1}}},{{strokeDashoffset:0,duration:.55,ease:"power1.in",immediateRender:false}},{t_ray:.2f});tl.set("{sel}",{{strokeDasharray:{L1},strokeDashoffset:{L1}}},0);'
    for sel in ("#kray2", "#kray2c"):
        js += f'tl.fromTo("{sel}",{{strokeDasharray:{L2},strokeDashoffset:{L2}}},{{strokeDashoffset:0,duration:.7,ease:"power1.out",immediateRender:false}},{t_back:.2f});tl.set("{sel}",{{strokeDasharray:{L2},strokeDashoffset:{L2}}},0);'
    js += f'tl.fromTo("#kb3 circle",{{fill:"url(#glassg)"}},{{filter:"drop-shadow(0 0 30px #FFE680)",duration:.3,immediateRender:false}},{t_ray + .5:.2f});'
    return js


# ---------------- MEĞERSE: çizginin yanına bir otomobil, boşluğa iki otomobil (kuş bakışı) ----------------
MEG_CSS = """
.megt { position:absolute; left:0; right:0; top:200px; text-align:center; font-weight:800; font-size:150px; color:#FFD23F; -webkit-text-stroke:7px #000; paint-order:stroke fill;
        text-shadow:0 12px 0 #000; opacity:0; z-index:5; }
"""
CAR_CM = 405                    # 2025'te en çok satan otomobilin boyu ≈ 4,05-4,12 m


def meg_html(dash=600, gap=900, cols=("#E8E4DA", "#2F6FD0", "#2FB36E")):
    H = LANES * 375
    road = road_top(L_CM, dash, gap, s=1, lanes=LANES, offset=150, idp="mg")
    grass = f'<rect x="-6000" y="-6000" width="{L_CM + 12000}" height="{H + 12000}" fill="{GRASS}"/>'
    world = f'<g transform="rotate(-90) translate({-U_C} {-H / 2})">{grass}{road}</g>'
    k = CAR_CM / 450
    us = (4650, 4950 + CAR_CM / 2 + 20, 4950 + CAR_CM * 1.5 + 40)
    cars = "".join(f'<g id="mgc{i}"><g transform="translate(0 {(U_C - u):.0f}) rotate(-90) scale({k:.3f})">{car_top(cols[i])}</g></g>' for i, u in enumerate(us))
    S = S_END
    xd = 540 + (375 - H / 2) * S
    y = lambda u: CY + (U_C - u) * S
    tapes = (f'<g id="mgt1">{vtape(xd - 44, y(4950) + 6, y(4350) - 6, "6 m", fs=56)}</g>'
             f'<g id="mgt2">{vtape(xd - 44, y(5850) + 6, y(4950) - 6, "9 m", col="#FFFFFF", fs=56)}</g>'
             f'<g id="mgl1">{vtape(540 + 140, y(4650 + CAR_CM / 2), y(4650 - CAR_CM / 2), "1 ARAÇ", col="#FFFFFF", fs=40, side=1)}</g>'
             f'<g id="mgl2">{vtape(540 + 140, y(us[2] + CAR_CM / 2), y(us[1] - CAR_CM / 2), "2 ARAÇ", col=YELLOW, fs=40, side=1)}</g>')
    return (f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:hidden"><g transform="translate(540 {CY})"><g id="mgz">{world}{cars}</g></g>{tapes}</svg>'
            '<div class="megt" id="megt">MEĞERSE</div>')


def meg_js(t0, t_car1, t_cars2, t_lab1=None, t_lab2=None):
    js = (f'tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out",immediateRender:false}},{t0 + .05:.2f});tl.set("#megt",{{opacity:0}},0);'
          f'tl.to("#megt",{{y:-40,scale:.55,duration:.5,ease:"power2.inOut"}},{t_car1 - .4:.2f});'
          f'tl.fromTo("#mgz",{{scale:.32,svgOrigin:"0 0"}},{{scale:{S_END},duration:1.4,ease:"power3.inOut",immediateRender:false}},{t0:.2f});tl.set("#mgz",{{scale:.32,svgOrigin:"0 0"}},0);'
          + pop_js("#mgt1", t0 + 1.0) + pop_js("#mgt2", t0 + 1.2))
    for i, t in ((0, t_car1), (1, t_cars2), (2, t_cars2 + .25)):
        js += f'tl.fromTo("#mgc{i}",{{y:2600,opacity:1}},{{y:0,duration:1.0,ease:"power3.out",immediateRender:false}},{t:.2f});tl.set("#mgc{i}",{{y:2600,opacity:0}},0);'
    js += pop_js("#mgl1", t_lab1 or t_car1 + .9) + pop_js("#mgl2", t_lab2 or t_cars2 + 1.1)
    return js
