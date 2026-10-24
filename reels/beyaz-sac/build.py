"""Beyaz saç koparma miti reel'i v2: tam metin (Meğerse sonda, iki fare deneyi), Osman'ın kendi seslendirmesi.

Ses akışı: Osman'ın kaydı → scripts/tighten.py (boşluk kısaltma) → hf/assets/beyazsac/voice-osman.mp3
         → scripts/align.py --text reels/beyaz-sac/metin-v2.txt → reels/beyaz-sac/words-v2.json
         → scripts/mouth.py → hf/avatar/mouth-beyazsac-v2.json
Kayıt yokken geçici zamanlarla (words-gecici.json + sessiz ses) yerleşim testi: BEYAZSAC_GECICI=1
python3 reels/beyaz-sac/build.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/beyazsac-v2.mp4)
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import depth  # noqa: E402

depth.W, depth.H = 1080, 1920
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, Scene, defs as depth_defs  # noqa: E402
from hairart import bathroom_bg, follicle, hair_strand, lab_mouse, mirror_glass, tweezers  # noqa: E402
from portrait import DEFS_P, light_shafts  # noqa: E402
from reelkit2 import HF, anchor, flash_js, page, punch_js, shake_js  # noqa: E402
from toon import INK, cel, darker, toon_figure  # noqa: E402

GECICI = os.environ.get("BEYAZSAC_GECICI") == "1"
words = json.loads((ROOT / ("reels/beyaz-sac/words-gecici.json" if GECICI else "reels/beyaz-sac/words-v2.json")).read_text(encoding="utf-8"))
mouth = json.loads((HF / ("avatar/mouth-beyazsac-gecici.json" if GECICI else "avatar/mouth-beyazsac-v2.json")).read_text())
VOICE = "assets/beyazsac/gecici.mp3" if GECICI else "assets/beyazsac/mix-v2.mp3"
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.4, 2)
TOTAL = round(VOICE_END + 3.5, 2)
A = lambda p, after=0.0: anchor(words, p, after)

T = {"hook": 0.0, "fol": A("Her saç teli"), "regrow": A("Yani bir teli"), "root": A("Çünkü rengin"), "why": A("Peki neden"),
     "clocks": A("Çünkü beyaz"), "lab": A("Ama işin"), "exp1": A("İlkinde"), "exp2": A("İkincisinde"), "pct": A("Kök hücresi sıkışan"),
     "warn": A("Ama bunlar"), "risk": A("İnsanda bilinen"), "meg": A("Meğerse"), "cta": A("Sizin evde"), "sources": VOICE_END}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
X = .12


def win(k):
    a, b = S[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


def scene(k, inner, bg="#000"):
    a, d = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{d}" data-track-index="1" style="background:{bg}"><div class="fill" id="{k}-in">{inner}</div></div>'


def svg(inner, idn="", style=""):
    i = f' id="{idn}"' if idn else ""
    return f'<svg class="fill"{i} viewBox="0 0 1080 1920" style="overflow:visible;{style}">{inner}</svg>'


def tag(idn, text, x, y, cls="", style=""):
    return f'<div class="tag {cls}" id="{idn}" style="left:{x}px;top:{y}px;opacity:0;{style}">{text}</div>'


def pop_js(sel, t, s0=.4):
    return f'tl.fromTo("{sel}",{{scale:{s0},opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)",immediateRender:false}},{t:.2f});tl.set("{sel}",{{opacity:0}},0);'


s = lambda k: S[k][0]
d = lambda k: win(k)[1]
JS, SFX = [], []
DARK = "radial-gradient(70% 50% at 50% 35%,#2A2238,#0E0A14)"

HERO = dict(outfit="tee", shirt="#2F5D7C", sleeve="#2F5D7C", hair_style="short", hair="#2A1E18", skin="#E2B48C", shorts=False, pants="#2A2C33")
GREYS = "".join(f'<path d="M{x} {y} q{dx} -3 {dx*1.6} -6" stroke="#F4F4F0" stroke-width="1.1" fill="none" stroke-linecap="round"/>' for x, y, dx in [(6, -174, 2), (11, -171, 2), (-8, -173, -2), (14, -167, 2.4)])


def mirror_scene(idn, expr, pose="pluck", glow=True):
    fig = toon_figure(pose=pose, look=(0, -1), expr=expr, **HERO)
    g = '<circle cx="-1" cy="-194" r="7" fill="#FFF6C8" opacity=".9" filter="url(#glow)"/>' if glow and pose == "pluck" else ""
    refl = (f'<defs><clipPath id="{idn}-mc"><rect x="170" y="330" width="740" height="940" rx="10"/></clipPath></defs>'
            f'<g clip-path="url(#{idn}-mc)"><rect x="170" y="330" width="740" height="940" fill="#BFD0D6"/>'
            + "".join(f'<rect x="{170 + (c*120 + (r%2)*60) - 60}" y="{330 + r*60}" width="116" height="56" rx="6" fill="#B2C4CA" stroke="#9AB0B6" stroke-width="3"/>' for r in range(16) for c in range(8))
            + f'<g id="{idn}-fig" transform="translate(560 1620) scale(5.6)">{fig}{GREYS}{g}</g></g>')
    return svg(bathroom_bg() + refl + mirror_glass(), f"{idn}-svg")


# 1) KANCA: ayna + tahmin kartları + "cevap sonda" kilidi
hook = (mirror_scene("hk", dict(lid=.15, smile=-.3, brow=.7))
        + '<div class="cards" id="cards">' + "".join(f'<div class="card" id="cd{i}">{n}</div>' for i, n in enumerate(["1", "2", "5", "10"])) + "</div>"
        + '<div class="qline" id="qline">YERİNE KAÇ TANE ÇIKAR?</div>')
JS.append(f'''
tl.fromTo("#hk-fig",{{attr:{{transform:"translate(560 1700) scale(6.4)"}}}},{{attr:{{transform:"translate(560 1620) scale(5.6)"}},duration:1.4,ease:"power2.out"}},0);
tl.fromTo("#qline",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"back.out(2)"}},{A("Beyaz saçı")});
tl.fromTo(".card",{{y:-160,opacity:0,rotation:-12}},{{y:0,opacity:1,rotation:0,duration:.35,stagger:.12,ease:"back.out(1.8)"}},{A("Beyaz saçı")+.2});
tl.to(".card",{{rotation:8,duration:.06,repeat:7,yoyo:true,ease:"none"}},{A("doğru mu")});
''' + punch_js("#hk-svg", A("Beyaz saçı"), 1.07))
SFX += [(0.0, "heartbeat"), (A("Beyaz saçı"), "pop")] + [(A("Beyaz saçı") + .2 + i * .12, "tick", .6) for i in range(4)] + [(A("doğru mu"), "tick")]

LOCK = ('<div id="lock"><svg viewBox="0 0 120 150" width="120" height="150">'
        '<path id="shackle" d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#1B1414" stroke-width="16" stroke-linecap="round"/>'
        '<path d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#C9CDD2" stroke-width="9" stroke-linecap="round" id="shackle2"/>'
        '<rect x="12" y="62" width="96" height="80" rx="14" fill="#FFD23F" stroke="#1B1414" stroke-width="7"/><circle cx="60" cy="96" r="10" fill="#1B1414"/><rect x="56" y="100" width="8" height="22" fill="#1B1414"/></svg>'
        '<span>CEVAP SONDA</span></div>')
m0 = A("Meğerse")
JS.append(f'''
tl.fromTo("#lock",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2.4)"}},{A("sandığından")});
tl.to("#lock",{{scale:1.07,duration:.6,yoyo:true,repeat:{max(1, int((m0 - A("sandığından")) / .6) - 2)},ease:"sine.inOut"}},{A("sandığından")+.4});
tl.to("#shackle,#shackle2",{{y:-18,rotation:-28,transformOrigin:"90px 66px",duration:.3,ease:"back.out(3)"}},{m0});
tl.to("#lock",{{scale:1.8,opacity:0,duration:.4,ease:"power2.in"}},{m0+.45});
''')
SFX += [(A("sandığından"), "heartbeat", .8)]

# 2) FOLİKÜL: makro kafa derisi dalışı → kesit
cam = Cam(horizon=760, vpx=540, f=1000, eye=110, sun=(-1, -.4), alt=46, haze="#E2B89A", zfar=4000)
sc = Scene(cam, "sp", ground=("#C98E6C", "#E2B89A"), sky=False)
for i in range(380):
    x = ((i * 137) % 2600) - 1300
    z = 180 + ((i * 71) % 60) * 55
    if abs(x) < 110 and z < 520:
        continue
    sc.add(x, z, hair_strand(white=(i % 17 == 5), h=480 + (i * 53) % 160, bend=((i * 29) % 9 - 4) / 18, seed=i), 640, 230, w=12)
sc.add(0, 330, hair_strand(white=True, h=560, bend=.04, seed=1), 560, 260, w=12)
FY = 470
fol = (svg('<defs><linearGradient id="scalpsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1810"/><stop offset=".35" stop-color="#8A5A42"/><stop offset=".42" stop-color="#E2B89A"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#scalpsky)"/>')
       + sc.svg()
       + f'<div class="fill" id="folwrap" style="opacity:0;background:{DARK}">{svg(f"<g transform=\"translate(540 {FY}) scale(.62)\">{follicle(grey=True, stem_ok=False)}</g>", "folsvg")}</div>'
       + tag("onefol", "1 FOLİKÜL = 1 TEL", 210, 150) + f'<div class="lbl" id="lbl1" style="left:640px;top:{FY+520}px;opacity:0">← FOLİKÜL (yuva)</div>')
cut = A("folikül.") if True else 0
JS.append(sc.js() + sc.camera_js(s("fol"), cut - s("fol"), dz=270, ease="power3.in"))
JS.append(f'''
tl.set("#folwrap",{{opacity:1}},{cut-.05});
tl.fromTo("#folsvg",{{scale:2.4,transformOrigin:"50% 22%"}},{{scale:1,duration:.7,ease:"power3.out",immediateRender:false}},{cut-.05});
''' + pop_js("#onefol", A("tek bir tel")) + f'tl.fromTo("#lbl1",{{x:30,opacity:0}},{{x:0,opacity:1,duration:.3,immediateRender:false}},{cut+.3});tl.set("#lbl1",{{opacity:0}},0);' + flash_js(cut - .05, .9, .3))
SFX += [(s("fol"), "whoosh", 1.2), (cut - .05, "swish"), (A("tek bir tel"), "ding", .7)]


# 3) BÖLÜNMÜŞ EKRAN: mit (yeni yuva, çok tel) vs gerçek (aynı yerden tek tel, yine beyaz)
def mini_skin(x0, tint):
    return (f'<rect x="{x0}" y="760" width="540" height="420" fill="{tint}"/>'
            + cel(f"M{x0} 1180 L{x0} 900 L{x0+540} 900 L{x0+540} 1180 Z", "#F2C4B0", "#D9A890", -1, 8, 5)
            + cel(f"M{x0} 900 L{x0} 860 L{x0+540} 860 L{x0+540} 900 Z", "#E9B996", "#C99876", -1, 4, 5)
            + f'<ellipse cx="{x0+270}" cy="866" rx="22" ry="8" fill="#6A3A2A" stroke="{INK}" stroke-width="4"/>')


myth_hairs = "".join(f'<g transform="translate({270 + dx} 866) rotate({rot})"><g class="mh{grp}">{hair_strand(white=True, h=300 + (i*37) % 80, bend=0, seed=i)}</g></g>'
                     for i, (grp, dx, rot) in enumerate([(1, -14, -18), (1, 14, 18), (2, -26, -34), (2, 26, 34), (2, 0, -4)]))
regrow = svg('<rect width="1080" height="1920" fill="#120A16"/>' + mini_skin(0, "#4A1218") + mini_skin(540, "#0E3A3A") + f'<g>{myth_hairs}</g>'
             + f'<g transform="translate(810 866)"><g id="realhair">{hair_strand(white=True, h=330, bend=0, seed=2)}</g></g>'
             + '<g id="mythx" opacity="0"><path d="M120 560 L420 860 M420 560 L120 860" stroke="#FF4D4D" stroke-width="40" stroke-linecap="round"/></g>'
             + '<path d="M540 300 V1300" stroke="#fff" stroke-width="6" stroke-dasharray="18 14"/>', "rgsvg") + \
    ('<div class="half l">MİT</div><div class="half r">GERÇEK</div>'
     + tag("mythn", "YENİ YUVA? ✗", 70, 600, "red") + tag("realn", "AYNI YUVA, 1 TEL", 590, 600, "", "background:#22C3A6;color:#fff;font-size:38px")
     + tag("yinebeyaz", "YİNE BEYAZ", 640, 1430, "dark"))
JS.append(f'''
tl.fromTo(".mh1",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)",immediateRender:false}},{s("regrow")+.2});
tl.fromTo(".mh2",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)",immediateRender:false}},{s("regrow")+.6});
tl.set(".mh1,.mh2",{{scale:0}},0);
tl.to("#mythx",{{opacity:1,duration:.1}},{A("açılmaz")});
tl.fromTo("#realhair",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:1.2,ease:"power1.out"}},{A("Aynı yerden")});
''' + pop_js("#mythn", A("açılmaz")) + pop_js("#realn", A("tek bir tel", s("regrow"))) + pop_js("#yinebeyaz", A("yine beyaz")) + punch_js("#rgsvg", A("yine beyaz"), 1.06))
SFX += [(s("regrow") + .2, "pop"), (s("regrow") + .6, "pop"), (A("açılmaz"), "boom", .6), (A("yine beyaz"), "ding", .6)]

# 4) KÖK: rengin kararı kökte; pigment hücresi yok
root = (f'<div class="fill" style="background:{DARK}"></div>'
        + svg(f'<g transform="translate(540 {FY}) scale(.62)"><g id="rtfol">{follicle(grey=True, stem_ok=False)}</g></g>'
              f'<circle id="rtring" cx="540" cy="{FY + .62*840:.0f}" r="90" fill="none" stroke="#FFD23F" stroke-width="10" stroke-dasharray="20 12" opacity="0"/>', "rtsvg")
        + tag("rt1", "RENK KÖKTE VERİLİR", 190, 150) + tag("rt2", "PİGMENT YOK → BEYAZ", 200, 1430, "dark"))
JS.append(f'tl.fromTo("#rtsvg",{{scale:1,transformOrigin:"50% 52%"}},{{scale:1.5,duration:{d("root")},ease:"power1.inOut"}},{s("root")});'
          f'tl.to("#rtring",{{opacity:1,duration:.2}},{A("kökte")});' + pop_js("#rt1", A("kökte")) + pop_js("#rt2", A("pigment")))
SFX += [(A("kökte"), "ding", .5)]

# 5) PEKİ NEDEN?
why = '<div class="fill" style="background:#0A0A0E"></div><div class="big" id="qmark" style="top:330px;font-size:560px;color:#FFD23F">?</div>'
JS.append(f'tl.fromTo("#qmark",{{scale:0,rotation:-30}},{{scale:1,rotation:0,duration:.45,ease:"back.out(2.5)",immediateRender:false}},{s("why")+.08});')
SFX += [(s("why") + .08, "pop")]

# 6) HER FOLİKÜLÜN KENDİ SAATİ + YAŞ
cells = []
for r in range(7):
    for c in range(5):
        i = r * 5 + c
        cx, cy = 150 + c * 195 + (r % 2) * 40, 240 + r * 118
        cells.append(f'<g transform="translate({cx} {cy})"><ellipse cx="0" cy="18" rx="30" ry="10" fill="#B07A5A" stroke="{INK}" stroke-width="3"/>'
                     f'<path id="gh{i}" d="M-3 18 C-6 -10 4 -30 10 -46" stroke="#2A1E18" stroke-width="9" stroke-linecap="round" fill="none"/>'
                     f'<g transform="translate(46 -26)"><circle r="20" fill="#F4F1EA" stroke="{INK}" stroke-width="3.5"/><path class="hand" d="M0 0 V-14" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/></g></g>')
order = sorted(range(35), key=lambda i: (i * 7919) % 35)
clocks = svg('<rect width="1080" height="1920" fill="#D9A07E"/>' + "".join(cells), "clsvg") + \
    tag("nocont", "BULAŞICI DEĞİL", 200, 120, "", "background:#22C3A6;color:#fff") + '<div class="agec" id="agec">YAŞ <b id="agen">30</b></div>' + tag("notw", "CIMBIZ DEĞİL, ZAMAN", 300, 1430, "dark")
age_t = A("Yaşla")
JS.append(f'tl.fromTo(".hand",{{rotation:0,transformOrigin:"0 0"}},{{rotation:"+=720",duration:{d("clocks")},ease:"none",stagger:{{each:.03}}}},{s("clocks")});'
          + pop_js("#nocont", A("bulaşıcı"))
          + "".join(f'tl.to("#gh{i}",{{attr:{{stroke:"#F2F2EE"}},duration:.15}},{s("clocks") + .4 + n * (d("clocks") - .6) / 35:.2f});' for n, i in enumerate(order[:24]))
          + f'tl.fromTo("#agec",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{age_t});tl.set("#agec",{{opacity:0}},0);'
          + f'(function(){{const o={{v:30}};tl.to(o,{{v:55,duration:{max(.6, S["clocks"][1]-age_t-.3):.2f},ease:"power1.in",onUpdate:()=>{{document.getElementById("agen").textContent=Math.round(o.v);}}}},{age_t});}})();'
          + pop_js("#notw", A("Sen kopardığın")))
SFX += [(s("clocks") + i * .3, "tick", .45) for i in range(int(d("clocks") / .3))] + [(age_t, "riser", .6)]

# 7) LABORATUVAR: iki deney
lab_bg = ('<rect width="1080" height="1920" fill="#1C2A36"/>' + light_shafts(80, 0, angle=-18, n=4, length=1500, spread=170, col="#CFE8FF", op=.18)
          + '<rect y="1180" width="1080" height="740" fill="#2E3E4C"/>' + cel("M0 1150 L1080 1150 L1080 1210 L0 1210 Z", "#C9D2D8", "#9AA6AE", -1, 8, 6)
          + "".join(f'<g transform="translate({x} 1150)">' + cel("M-150 0 L-150 -300 L150 -300 L150 0 Z", "#9FC3D6", "#6E96AA", -1, 10, 6)
                    + "".join(f'<path d="M{-150+k*30} -300 V0" stroke="#5A7A8A" stroke-width="5"/>' for k in range(11))
                    + f'<g transform="translate(0 -20) scale(.9)">{lab_mouse()}</g>'
                    + f'<rect x="-120" y="-380" width="240" height="64" rx="14" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/><text x="0" y="-336" text-anchor="middle" font-family="Mont" font-weight="800" font-size="38" fill="#1B1414">DENEY {n}</text></g>'
                    for n, x in ((1, 290), (2, 790)))
          + cel("M490 1150 L590 1150 L600 1120 L480 1120 Z", "#3A3A44", "#22222A", -1, 4, 5)
          + '<rect x="525" y="900" width="30" height="230" fill="#4A4A54" stroke="#1B1414" stroke-width="5"/>'
          + cel("M500 900 L580 900 L600 830 L560 800 L520 810 Z", "#5A5A64", "#3A3A44", -1, 6, 5))
lab = svg(lab_bg, "labsvg") + tag("labt", "LABORATUVAR", 270, 150, "dark")
JS.append(f'tl.fromTo("#labsvg",{{scale:1.15,transformOrigin:"50% 60%"}},{{scale:1,duration:{d("lab")},ease:"power2.out"}},{s("lab")});' + pop_js("#labt", s("lab") + .1))
SFX += [(s("lab") - .4, "riser", .6), (A("iki ilginç"), "ding", .6)]

# 8) DENEY 1 (Cell 2015, fare): 200 kıl koparıldı → ~1300 kıl yeniden büyüdü, uykudaki foliküller uyandı
dots, sprouts = [], []
for i in range(36 * 30):
    gx, gy = i % 36, i // 36
    x, y = 150 + gx * 22 + (gy % 2) * 11, 410 + gy * 20
    r2 = (x - 540) ** 2 + (y - 700) ** 2
    if r2 < 120 ** 2:
        dots.append(f'<circle class="pk" cx="{x}" cy="{y}" r="5" fill="#1E1A18"/>')
    elif r2 < 290 ** 2 and (i * 37) % 5 < 4:
        sprouts.append(f'<path class="sp" d="M{x} {y} l{(i*13)%7-3} -18" stroke="#1E1A18" stroke-width="5" stroke-linecap="round"/>')
        dots.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#6A4A3E" opacity=".7"/>')
    else:
        dots.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#6A4A3E" opacity=".7"/>')
exp1 = (svg('<rect width="1080" height="1920" fill="#14202A"/>' + cel("M130 390 L950 390 L950 1010 L130 1010 Z", "#E9B8A8", "#C9988A", -1, 10, 6)
            + "".join(dots) + f'<g id="sprouts">{"".join(sprouts)}</g>'
            + '<circle id="pkc" cx="540" cy="700" r="122" fill="none" stroke="#FFD23F" stroke-width="8" stroke-dasharray="18 12"/>'
            + '<g id="zzz" opacity="0">' + "".join(f'<text x="{x}" y="{y}" font-family="Mont" font-weight="800" font-size="{fs}" fill="#9FC3D6" stroke="#000" stroke-width="5" paint-order="stroke">z</text>' for x, y, fs in [(300, 560, 50), (330, 520, 64), (370, 470, 80), (740, 900, 50), (770, 860, 64)]) + '</g>'
            + '<g id="alarm" opacity="0" transform="translate(870 470)"><circle r="70" fill="#FF4D4D" stroke="#1B1414" stroke-width="8"/><circle r="52" fill="#FFF8E6"/><path d="M0 0 V-34 M0 0 L22 14" stroke="#1B1414" stroke-width="7" stroke-linecap="round"/><circle cx="-56" cy="-60" r="22" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/><circle cx="56" cy="-60" r="22" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/></g>', "e1svg")
        + tag("e1t", "DENEY 1 · CELL 2015 · FARE", 130, 150) + '<div class="cnt" id="c200"><b>200</b> kıl koparıldı</div><div class="cnt" id="c1300"><b>≈1300</b> kıl yeniden büyüdü</div>'
        + tag("e1w", "YENİ YUVA YOK · UYKUDAKİLER UYANDI", 290, 1430, "dark", "font-size:30px"))
JS.append(pop_js("#e1t", s("exp1") + .1)
          + f'tl.to(".pk",{{y:-140,opacity:0,duration:.35,stagger:{{each:.004,from:"center"}},ease:"power2.in"}},{A("iki yüz")});'
          + f'tl.fromTo("#c200",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{A("iki yüz")});tl.set("#c200",{{opacity:0}},0);'
          + f'tl.to("#c200",{{opacity:0,duration:.2}},{A("bin üç")-.1});'
          + f'tl.fromTo(".sp",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.5,stagger:{{each:.0025,from:"center"}},ease:"back.out(2)",immediateRender:false}},{A("bin üç")});tl.set(".sp",{{scaleY:0}},0);'
          + f'tl.fromTo("#c1300",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{A("bin üç")+.2});tl.set("#c1300",{{opacity:0}},0);'
          + f'tl.to("#zzz",{{opacity:1,duration:.2}},{A("Uykudaki")});tl.to("#zzz",{{opacity:0,duration:.2}},{A("alarm")+.2});'
          + f'tl.to("#alarm",{{opacity:1,duration:.1}},{A("alarm")});tl.fromTo("#alarm",{{rotation:-12}},{{rotation:12,duration:.05,repeat:15,yoyo:true,ease:"none",immediateRender:false}},{A("alarm")});'
          + pop_js("#e1w", A("topluca")) + punch_js("#e1svg", A("bin üç"), 1.06))
SFX += [(A("iki yüz"), "pluck"), (A("iki yüz") + .15, "pluck", .7), (A("bin üç"), "riser", .5), (A("bin üç") + .5, "boom", .7)] + [(A("alarm") + i * .1, "tick", .7) for i in range(8)]

# 9) DENEY 2 (Nature 2023, fare): renk kök hücreleri gidip gelir; yaşlanınca sıkışır; tekrarlı koparma
exp2 = (f'<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#203040,#0A0E14)"></div>'
        + svg(f'<g transform="translate(540 {FY}) scale(.62)"><g id="e2fol">{follicle(grey=False)}</g>'
              + "".join(f'<circle class="mv" cx="{-62 if i % 2 else 62}" cy="380" r="14" fill="#7FC6E8" stroke="{INK}" stroke-width="3"/>' for i in range(4))
              + '<g id="jam" opacity="0"><rect x="-150" y="300" width="300" height="140" rx="26" fill="none" stroke="#FF4D4D" stroke-width="10" stroke-dasharray="26 16"/></g></g>'
              + '<g transform="translate(610 330) scale(2)"><g id="e2tw">' + tweezers(.3) + '</g></g>', "e2svg")
        + tag("e2t", "DENEY 2 · NATURE 2023 · FARE", 110, 150, "", "background:#7FC6E8")
        + tag("e2a", "RENK KÖK HÜCRELERİ", 560, 560, "dark", "font-size:34px") + tag("e2b", "SIKIŞTI → RENK YOK", 560, 640, "red", "font-size:38px")
        + tag("e2c", "TEKRAR TEKRAR KOPARMA", 300, 1430, "dark", "font-size:36px"))
JS.append(pop_js("#e2t", s("exp2") + .1) + pop_js("#e2a", A("kök hücreleri"))
          + f'tl.fromTo(".mv",{{y:0}},{{y:420,duration:.7,stagger:.18,yoyo:true,repeat:5,ease:"sine.inOut",immediateRender:false}},{A("aşağı yukarı")-.3});'
          + f'tl.to(".mv",{{y:0,attr:{{fill:"#FF4D4D"}},duration:.3,overwrite:true}},{A("sıkışıp")});tl.to("#jam",{{opacity:1,duration:.2}},{A("sıkışıp")});'
          + pop_js("#e2b", A("sıkışıp")) + shake_js("#e2svg", A("sıkışıp"), 8, 4)
          + "".join(f'tl.to("#e2fol .shaft",{{y:-260,duration:.12,ease:"power3.in"}},{A("tekrar tekrar koparıp") + k*.32:.2f});tl.set("#e2fol .shaft",{{y:0}},{A("tekrar tekrar koparıp") + k*.32 + .2:.2f});'
                    f'tl.to("#e2tw",{{y:40,duration:.1}},{A("tekrar tekrar koparıp") + k*.32:.2f});tl.to("#e2tw",{{y:0,duration:.14}},{A("tekrar tekrar koparıp") + k*.32 + .12:.2f});' for k in range(3))
          + pop_js("#e2c", A("tekrar tekrar koparıp")))
SFX += [(A("sıkışıp"), "boom", .7)] + [(A("tekrar tekrar koparıp") + k * .32, "pluck") for k in range(3)]

# 10) %15 → neredeyse yarısı
grid = "".join(f'<circle class="{"g0" if i in (2, 9, 15) else ("g1" if i in (0, 4, 6, 11, 13, 17, 19) else "gx")}" cx="{180 + (i % 5) * 180}" cy="{530 + (i // 5) * 140}" r="56" fill="#3A4A5A" stroke="#fff" stroke-width="6"/>' for i in range(20))
pct = (svg('<rect width="1080" height="1920" fill="#0E1218"/>' + grid, "pcsvg")
       + '<div class="pctn" id="pctn"><b id="pcv">%15</b><span>kök hücresi sıkışan folikül (fare)</span></div>' + tag("half", "≈ NEREDEYSE YARISI", 300, 1430))
JS.append(f'tl.to(".g0",{{attr:{{fill:"#FF4D4D"}},duration:.2,stagger:.1}},{s("pct")+.3});'
          f'(function(){{const o={{v:15}};tl.to(o,{{v:50,duration:1.4,ease:"power2.inOut",onUpdate:()=>{{document.getElementById("pcv").textContent=(o.v>=49.5?"≈%50":"%"+Math.round(o.v));}}}},{A("neredeyse")-.6});}})();'
          f'tl.to(".g1",{{attr:{{fill:"#FF4D4D"}},duration:.15,stagger:.12}},{A("neredeyse")-.5});' + pop_js("#half", A("yarıya")))
SFX += [(A("neredeyse") - .6 + i * .12, "tick", .5) for i in range(11)] + [(A("yarıya"), "ding", .8)]

# 11) FARE ≠ İNSAN
warn = ('<div class="fill" style="background:#14181E"></div>'
        + svg('<g transform="translate(270 820) scale(1.3)">' + lab_mouse(grey=.5) + '</g>'
              + f'<g transform="translate(780 1240) scale(4.6)">{toon_figure(look=(-1, 0), expr=dict(lid=.3, smile=-.2, brow=.4), flip=True, **HERO)}</g>', "prsvg")
        + '<div class="big" id="neq" style="top:520px;font-size:260px;color:#FFD23F">≠</div>'
        + '<div class="tape" id="tape">HENÜZ İNSANDA KANITLANMADI · HENÜZ İNSANDA KANITLANMADI</div>')
JS.append(f'tl.fromTo("#neq",{{scale:0}},{{scale:1,duration:.35,ease:"back.out(3)",immediateRender:false}},{s("warn")+.15});'
          f'tl.fromTo("#tape",{{x:-1400}},{{x:0,duration:.4,ease:"power3.out",immediateRender:false}},{A("kanıtlanmadı")-.3});tl.set("#tape",{{x:-1400}},0);')
SFX += [(s("warn") + .15, "pop"), (A("kanıtlanmadı") - .3, "whoosh", .8)]

# 12) İNSANDAKİ RİSK: tekrar tekrar koparma → iltihap, iz, kel bölge
risk = (f'<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#40202A,#120A16)"></div>'
        + svg(f'<g transform="translate(540 {FY}) scale(.62)"><g id="cfol">{follicle(grey=True, stem_ok=True)}</g>'
              f'<circle id="inflam" cx="0" cy="820" r="40" fill="#FF3A2A" opacity="0" filter="url(#glow)"/>'
              f'<g id="scar" opacity="0"><path d="M-300 520 l60 -30 l40 40 l60 -40 l50 30 M80 560 l60 -40 l50 40 l60 -30" stroke="#F7E7DC" stroke-width="16" fill="none" stroke-linecap="round"/></g></g>', "cssvg")
        + '<div class="words3"><span id="w1">ENFEKSİYON</span><span id="w2">İZ</span><span id="w3">KEL BÖLGE</span></div>'
        + svg('<rect width="1080" height="1920" fill="#C98E6C"/>' + "".join(
            f'<path d="M{(i*97)%1100-10} {(i*53)%1300+200} l{4+(i%3)*3} -26" stroke="{"#F2F2EE" if i % 9 == 0 else "#2A1E18"}" stroke-width="7" stroke-linecap="round"/>'
            for i in range(900) if ((((i*97)%1100-10)-540)**2 + (((i*53)%1300+200)-760)**2) > 190**2)
            + '<ellipse cx="540" cy="760" rx="190" ry="190" fill="#D99A7E" opacity=".85"/>', "bald", "opacity:0")
        + tag("tt", "TEKRAR TEKRAR", 300, 1430, "red"))
sh_t = A("tekrar tekrar koparmak")
JS.append("".join(f'tl.to("#cfol .shaft",{{y:-260,duration:.12,ease:"power3.in"}},{sh_t + k*.32:.2f});tl.set("#cfol .shaft",{{y:0}},{sh_t + k*.32 + .2:.2f});' + shake_js("#cssvg", sh_t + k * .32 + .1, 10, 2) for k in range(3))
          + pop_js("#tt", sh_t)
          + f'tl.to("#inflam",{{opacity:.85,attr:{{r:170}},duration:.4}},{A("enfeksiyona")});tl.fromTo("#w1",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in",immediateRender:false}},{A("enfeksiyona")});'
          + f'tl.to("#scar",{{opacity:1,duration:.2}},{A("iz kalmasına")});tl.fromTo("#w2",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in",immediateRender:false}},{A("iz kalmasına")});'
          + f'tl.to("#bald",{{opacity:1,duration:.15}},{A("kel")});tl.fromTo("#bald",{{scale:1.6,transformOrigin:"50% 40%"}},{{scale:1,duration:.8,ease:"power3.out",immediateRender:false}},{A("kel")});'
          + f'tl.fromTo("#w3",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in",immediateRender:false}},{A("kel")});tl.set("#w1,#w2,#w3",{{opacity:0}},0);')
SFX += [(sh_t + k * .32, "pluck") for k in range(3)] + [(A("enfeksiyona"), "boom", .5), (A("iz kalmasına"), "boom", .5), (A("kel"), "boom", .8)]

# 13) MEĞERSE (final): kilit açılır, büyük cevap, sonra uyarı
meg = ('<div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#3A2A10,#0A0806)"></div>'
       + '<div class="megt" id="megt">MEĞERSE</div>'
       + '<div class="ans" id="ans1"><i>✓</i>KOPARINCA BEYAZ<br>ÇOĞALMIYOR</div>'
       + svg('<rect width="1080" height="1920" fill="#C98E6C"/>' + "".join(
           f'<path d="M{(i*97)%1100-10} {(i*53)%1300+200} l{4+(i%3)*3} -26" stroke="{"#F2F2EE" if i % 7 == 0 else "#2A1E18"}" stroke-width="7" stroke-linecap="round"/>'
           for i in range(900) if ((((i*97)%1100-10)-540)**2 + (((i*53)%1300+200)-760)**2) > 150**2)
           + '<circle id="spot" cx="540" cy="760" r="150" fill="#D99A7E"/>', "megbald", "opacity:0")
       + tag("ans2", "KOPARMAYA DEVAM EDERSEN…", 290, 1430, "red", "font-size:34px"))
JS.append(flash_js(m0, .95, .4) + shake_js("#meg-in", m0, 14, 6)
          + f'tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out",immediateRender:false}},{m0});tl.set("#megt",{{opacity:0}},0);'
          + f'tl.to("#megt",{{y:-560,scale:.6,duration:.5,ease:"power2.inOut"}},{A("yıllardır")});'
          + f'tl.fromTo("#ans1",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2.4)",immediateRender:false}},{A("koparınca beyaz")});tl.set("#ans1",{{opacity:0}},0);'
          + f'tl.to("#ans1",{{opacity:0,y:-60,duration:.3}},{A("Ama koparmaya")});'
          + f'tl.to("#megbald",{{opacity:1,duration:.3}},{A("Ama koparmaya")});tl.fromTo("#megbald",{{scale:1.8,transformOrigin:"50% 40%"}},{{scale:1,duration:1.2,ease:"power2.out",immediateRender:false}},{A("Ama koparmaya")});'
          + pop_js("#ans2", A("Ama koparmaya"))
          + f'tl.fromTo("#spot",{{attr:{{r:20}}}},{{attr:{{r:150}},duration:1.6,ease:"power2.inOut",immediateRender:false}},{A("hiç saç")-.6});')
SFX += [(m0 - 1.2, "riser", 1.0), (m0, "boom", 1.0), (A("koparınca beyaz"), "ding"), (A("hiç saç"), "heartbeat", .9)]

# 14) CTA
cta = (mirror_scene("ct", dict(lid=.25, smile=.6, brow=.3))
       + '<div class="ctaq" id="ctaq">SİZİN EVDE KAÇ TANE<br>ÇIKAR DENİRDİ?</div>' + tag("ctaw", "RAKAMI YAZ ↓", 250, 420, "", "font-size:64px")
       + tag("ctas", "Cımbızcı arkadaşına gönder", 300, 1440, "dark", "font-size:36px"))
JS.append(f'tl.fromTo("#ctaq",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{s("cta")+.1});tl.set("#ctaq",{{opacity:0}},0);'
          + pop_js("#ctaw", A("Rakamı")) + f'tl.to("#ctaw",{{y:16,duration:.35,yoyo:true,repeat:5,ease:"sine.inOut"}},{A("Rakamı")+.4});' + pop_js("#ctas", A("Rakamı") + .4))
SFX += [(s("cta"), "swish"), (A("Rakamı"), "pop")]

sources = ('<div class="fill" style="background:#0B0E14"></div><div style="position:absolute;left:70px;right:70px;top:250px" class="src"><b style="color:#FFD23F;font-size:48px">KAYNAKLAR</b><br>'
           'UAMS Health · Medical Myths (2019)<br>Cleveland Clinic · Gray Hair<br>Healthline · Hair follicle pulled out (2021)<br>'
           'Chen ve ark., Cell (2015) · fare çalışması<br>Sun ve ark., Nature (2023) · fare çalışması<br><br>Tıbbi tavsiye değildir.</div>')

HTML = dict(hook=hook, fol=fol, regrow=regrow, root=root, why=why, clocks=clocks, lab=lab, exp1=exp1, exp2=exp2, pct=pct, warn=warn, risk=risk, meg=meg, cta=cta, sources=sources)
scenes_html = "".join(scene(k, HTML[k]) for k in keys) + LOCK
js = "".join(f'tl.fromTo("#{k}-in",{{scale:1.12,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.out",immediateRender:false}},{s(k)});' for k in keys if k != "hook")
js += "".join(JS)
SFX += [(s(k) - .05, "swish", .6) for k in keys if k not in ("hook", "fol", "meg", "why")]

css = """
.cards { position:absolute; left:0; right:0; top:180px; display:flex; justify-content:center; gap:28px; }
.card { width:170px; height:170px; border-radius:28px; background:#FFF8E6; color:#111; border:7px solid #111; box-shadow:0 10px 0 #111; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:92px; }
.qline { position:absolute; left:0; right:0; top:390px; text-align:center; font-weight:800; font-size:58px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; text-shadow:0 6px 0 #000; }
#lock { position:absolute; right:40px; top:150px; width:160px; text-align:center; opacity:0; z-index:60; }
#lock span { display:block; font-weight:800; font-size:26px; color:#FFD23F; -webkit-text-stroke:2px #000; paint-order:stroke fill; }
.lbl { position:absolute; font-weight:800; font-size:40px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; }
.half { position:absolute; top:480px; width:540px; text-align:center; font-weight:800; font-size:76px; -webkit-text-stroke:4px #000; paint-order:stroke fill; }
.half.l { left:0; color:#FF7A7A; } .half.r { left:540px; color:#5EF0D2; }
.agec { position:absolute; right:60px; top:380px; padding:14px 26px; border-radius:20px; background:rgba(10,10,14,.85); border:3px solid #fff; font-weight:800; font-size:44px; opacity:0; }
.agec b { color:#FFD23F; font-size:64px; }
.cnt { position:absolute; left:0; right:0; top:1090px; text-align:center; font-weight:600; font-size:40px; color:#fff; opacity:0; -webkit-text-stroke:2px #000; paint-order:stroke fill; }
.cnt b { font-weight:800; font-size:110px; color:#FFD23F; -webkit-text-stroke:5px #000; }
#c200, #c1300 { top:230px; } #c200 b { color:#FF4D4D; }
.words3 { position:absolute; left:0; right:0; top:150px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.words3 span { font-weight:800; font-size:78px; color:#FF4D4D; -webkit-text-stroke:4px #000; paint-order:stroke fill; text-shadow:0 6px 0 #000; opacity:0; }
.megt { position:absolute; left:0; right:0; top:700px; text-align:center; font-weight:800; font-size:200px; color:#FFD23F; -webkit-text-stroke:7px #000; paint-order:stroke fill; text-shadow:0 12px 0 #000; opacity:0; z-index:5; }
.ans { position:absolute; left:60px; right:60px; top:560px; padding:36px 30px; border-radius:36px; background:#22C3A6; border:8px solid #111; box-shadow:0 14px 0 #111; text-align:center; font-weight:800; font-size:86px; line-height:1.05; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; opacity:0; }
.ans i { display:block; font-style:normal; font-size:120px; }
.pctn { position:absolute; left:0; right:0; top:170px; text-align:center; }
.pctn b { display:block; font-weight:800; font-size:220px; line-height:1; color:#FF4D4D; -webkit-text-stroke:6px #000; paint-order:stroke fill; }
.pctn span { font-weight:600; font-size:40px; color:#D9DEE8; }
.tape { position:absolute; left:-200px; width:1500px; top:1000px; padding:18px 0; background:#FFD23F; border-top:14px solid #111; border-bottom:14px solid #111; transform:rotate(-8deg); text-align:center; font-weight:800; font-size:46px; color:#111; }
.ctaq { position:absolute; left:0; right:0; top:170px; text-align:center; font-weight:800; font-size:80px; line-height:1.05; color:#fff; -webkit-text-stroke:5px #000; paint-order:stroke fill; text-shadow:0 8px 0 #000; }
"""
DEFS = DEFS2.replace("</defs>", "") + DEFS_P + depth_defs(cam) + "</defs>"
html = page(words, mouth, scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="BEYAZ SAÇ <b>MİTİ</b>", voice_src=VOICE, extra_css=css, defs=DEFS)
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(ROOT / "reels/beyaz-sac/sfx-v2.json", "w"))
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
