"""Beyaz saç koparma miti reel'i (v5 tam ekran tema): hf/index.html + hf/assets/beyazsac/mix.mp3 üretir.

python3 reels/beyaz-sac/build.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/beyazsac-v1.mp4)
Olgular ve kaynaklar: reels/beyaz-sac/arastirma.json (doğrulanmış). Sahne kuralları: hf/art/DERINLIK.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import depth  # noqa: E402

depth.W, depth.H = 1080, 1920                      # tam ekran sahne ölçüsü
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, Scene, defs as depth_defs  # noqa: E402
from hairart import bathroom_bg, follicle, hair_strand, lab_mouse, mirror_glass, tweezers  # noqa: E402
from portrait import DEFS_P  # noqa: E402
from reelkit2 import HF, anchor, flash_js, page, punch_js, shake_js  # noqa: E402
from toon import INK, cel, toon_figure  # noqa: E402

words = json.loads((ROOT / "reels/beyaz-sac/words.json").read_text(encoding="utf-8"))
mouth = json.loads((HF / "avatar/mouth-beyazsac.json").read_text())
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.5, 2)
TOTAL = round(VOICE_END + 3.5, 2)
A = lambda p, after=0.0: anchor(words, p, after)

T = {"hook": 0.0, "dive": A("Her folikülden"), "regrow": A("Koparınca"), "why": A("Peki neden"), "clocks": A("Beyaz bulaşıcı"),
     "cost": A("Asıl bedel şu"), "meg": A("Meğerse"), "stuck": A("renk kök"), "pct": A("Sıkışmalı"), "proof": A("Ama bu fare"),
     "cta": A("Sizde kaç"), "sources": VOICE_END}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
X = .12   # sahneler arası örtüşme (hızlı geçiş)


def win(k):
    a, b = S[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


def scene(k, inner, bg="#000"):
    a, d = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{d}" data-track-index="1" style="background:{bg}"><div class="fill" id="{k}-in">{inner}</div></div>'


def svg(inner, idn="", style=""):
    i = f' id="{idn}"' if idn else ""
    return f'<svg class="fill"{i} viewBox="0 0 1080 1920" style="overflow:visible;{style}">{inner}</svg>'


s = lambda k: S[k][0]
d = lambda k: win(k)[1]
JS, SFX = [], []

# ---------------- karakter (aynadaki yansıma) ----------------
HERO = dict(outfit="tee", shirt="#2F5D7C", sleeve="#2F5D7C", hair_style="short", hair="#2A1E18", skin="#E2B48C", shorts=False, pants="#2A2C33")
GREYS = "".join(f'<path d="M{x} {y} q{dx} -3 {dx*1.6} -6" stroke="#F4F4F0" stroke-width="1.1" fill="none" stroke-linecap="round"/>' for x, y, dx in [(6, -174, 2), (11, -171, 2), (-8, -173, -2), (14, -167, 2.4)])


def mirror_scene(idn, expr, pose="pluck", glow=True):
    fig = toon_figure(pose=pose, look=(0, -1), expr=expr, **HERO)
    g = (f'<circle cx="-1" cy="-194" r="7" fill="#FFF6C8" opacity=".9" filter="url(#glow)"/>' if glow else "")
    refl = (f'<defs><clipPath id="{idn}-mc"><rect x="170" y="330" width="740" height="940" rx="10"/></clipPath></defs>'
            f'<g clip-path="url(#{idn}-mc)"><rect x="170" y="330" width="740" height="940" fill="#BFD0D6"/>'
            + "".join(f'<rect x="{170 + (c*120 + (r%2)*60) - 60}" y="{330 + r*60}" width="116" height="56" rx="6" fill="#B2C4CA" stroke="#9AB0B6" stroke-width="3"/>' for r in range(16) for c in range(8))
            + f'<g id="{idn}-fig" transform="translate(560 1620) scale(5.6)">{fig}{GREYS}{g}</g></g>')
    return svg(bathroom_bg() + refl + mirror_glass(), f"{idn}-svg")


# 1) KANCA: ayna, cımbız, tahmin kartları
hook = (mirror_scene("hk", dict(lid=.15, smile=-.3, brow=.7))
        + '<div class="cards" id="cards">' + "".join(f'<div class="card" id="cd{i}">{n}</div>' for i, n in enumerate(["1", "2", "5", "10"])) + "</div>"
        + '<div class="qline" id="qline">YERİNE KAÇ TANE ÇIKAR?</div>'
        + '<div class="stamp" id="stamp">SAHTE</div>')
JS.append(f'''
tl.fromTo("#hk-fig",{{attr:{{transform:"translate(560 1700) scale(6.4)"}}}},{{attr:{{transform:"translate(560 1620) scale(5.6)"}},duration:1.2,ease:"power2.out"}},0);
tl.fromTo("#qline",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"back.out(2)"}},.15);
tl.fromTo(".card",{{y:-160,opacity:0,rotation:-12}},{{y:0,opacity:1,rotation:0,duration:.35,stagger:.12,ease:"back.out(1.8)"}},.35);
tl.to("#cd1,#cd2,#cd3",{{backgroundColor:"#FF4D4D",color:"#fff",duration:.12,stagger:.08}},{A("Doğru")});
tl.to("#cd1,#cd2,#cd3",{{y:220,rotation:24,opacity:0,duration:.45,stagger:.06,ease:"power2.in"}},{A("Doğru")+.35});
tl.to("#cd0",{{backgroundColor:"#22C3A6",color:"#fff",scale:1.25,duration:.25,ease:"back.out(3)"}},{A("Doğru")+.2});
tl.fromTo("#stamp",{{scale:2.6,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:-12,duration:.22,ease:"power3.in"}},{A("Doğru")+.05});
tl.to("#stamp,#qline",{{opacity:0,duration:.25}},{A("Asıl bedel")-.1});
''' + flash_js(A("Doğru") + .27, .7) + shake_js("#hk-svg", A("Doğru") + .27, 16, 6))
SFX += [(0.0, "heartbeat"), (.35, "tick", .6), (.47, "tick", .6), (.59, "tick", .6), (.71, "tick", .6), (A("Doğru") + .27, "boom"), (A("Doğru") + .3, "pluck")]

# açık döngü kilidi (sahnelerin üstünde kalır)
LOCK = ('<div id="lock"><svg viewBox="0 0 120 150" width="120" height="150">'
        '<path id="shackle" d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#1B1414" stroke-width="16" stroke-linecap="round"/>'
        '<path d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#C9CDD2" stroke-width="9" stroke-linecap="round" id="shackle2"/>'
        '<rect x="12" y="62" width="96" height="80" rx="14" fill="#FFD23F" stroke="#1B1414" stroke-width="7"/><circle cx="60" cy="96" r="10" fill="#1B1414"/><rect x="56" y="100" width="8" height="22" fill="#1B1414"/></svg>'
        '<span>ASIL BEDEL</span></div>')
JS.append(f'''
tl.fromTo("#lock",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2.4)"}},{A("sona")});
tl.to("#lock",{{scale:1.08,duration:.5,yoyo:true,repeat:{max(1, int((A("Asıl bedel şu") - A("sona")) / .5) - 1)},ease:"sine.inOut"}},{A("sona")+.4});
tl.to("#shackle,#shackle2",{{y:-18,rotation:-28,transformOrigin:"90px 66px",duration:.3,ease:"back.out(3)"}},{A("Asıl bedel şu")+.2});
tl.to("#lock",{{scale:1.6,opacity:0,duration:.4,ease:"power2.in"}},{A("Asıl bedel şu")+.75});
''')
SFX += [(A("sona"), "heartbeat", .8), (A("Asıl bedel şu") + .2, "tick"), (A("Asıl bedel şu") + .22, "pop")]

# 2) DALIŞ: makro kafa derisi → folikül kesiti
cam = Cam(horizon=760, vpx=540, f=1000, eye=110, sun=(-1, -.4), alt=46, haze="#E2B89A", zfar=4000)
sc = Scene(cam, "sp", ground=("#C98E6C", "#E2B89A"), sky=False)
for i in range(380):
    x = ((i * 137) % 2600) - 1300
    z = 180 + ((i * 71) % 60) * 55
    if abs(x) < 110 and z < 520:
        continue
    sc.add(x, z, hair_strand(white=(i % 17 == 5), h=480 + (i * 53) % 160, bend=((i * 29) % 9 - 4) / 18, seed=i), 640, 230, w=12)
sc.add(0, 330, hair_strand(white=True, h=560, bend=.04, seed=1), 560, 260, w=12)
fol_y = 470
dive = (svg('<rect width="1080" height="1920" fill="url(#scalpsky)"/><defs><linearGradient id="scalpsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1810"/><stop offset=".35" stop-color="#8A5A42"/><stop offset=".42" stop-color="#E2B89A"/></linearGradient></defs>')
        + sc.svg()
        + f'<div class="fill" id="folwrap" style="opacity:0;background:radial-gradient(70% 50% at 50% 35%,#3A2440,#120A16)">{svg(f"<g transform=\"translate(540 {fol_y}) scale(.62)\">{follicle(grey=True, stem_ok=False)}</g>", "folsvg")}</div>'
        + '<div class="tag" id="onefol" style="left:180px;top:150px;opacity:0">1 FOLİKÜL = 1 TEL</div>'
        + f'<div class="lbl" id="lbl1" style="left:640px;top:{fol_y+520}px;opacity:0">← KÖK (folikül)</div>')
JS.append(sc.js() + sc.camera_js(s("dive"), A("tek tel") - s("dive"), dz=270, ease="power3.in"))
JS.append(f'''
tl.set("#folwrap",{{opacity:1}},{A("tek tel")-.05});
tl.fromTo("#folsvg",{{scale:2.4,transformOrigin:"50% 22%"}},{{scale:1,duration:.7,ease:"power3.out"}},{A("tek tel")-.05});
tl.fromTo("#onefol",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)"}},{A("tek tel")+.25});
tl.fromTo("#lbl1",{{x:30,opacity:0}},{{x:0,opacity:1,duration:.3}},{A("tek tel")+.5});
''' + flash_js(A("tek tel") - .05, .9, .3))
SFX += [(s("dive"), "whoosh", 1.2), (A("tek tel") - .05, "swish"), (A("tek tel") + .25, "ding", .7)]

# 3) BÖLÜNMÜŞ EKRAN: mit (2, 5 tel fışkırır) vs gerçek (aynı yerden tek tel, yine beyaz)


def mini_skin(x0, tint):
    return (f'<rect x="{x0}" y="760" width="540" height="420" fill="{tint}"/>'
            + cel(f"M{x0} 1180 L{x0} 900 L{x0+540} 900 L{x0+540} 1180 Z", "#F2C4B0", "#D9A890", -1, 8, 5)
            + cel(f"M{x0} 900 L{x0} 860 L{x0+540} 860 L{x0+540} 900 Z", "#E9B996", "#C99876", -1, 4, 5)
            + f'<ellipse cx="{x0+270}" cy="866" rx="22" ry="8" fill="#6A3A2A" stroke="{INK}" stroke-width="4"/>')


myth_hairs = "".join(f'<g class="mh{grp}" transform="translate({270 + dx} 866) rotate({rot})"><g class="mhi">{hair_strand(white=True, h=300 + (i*37) % 80, bend=0, seed=i)}</g></g>'
                     for i, (grp, dx, rot) in enumerate([(1, -14, -18), (1, 14, 18), (2, -26, -34), (2, 26, 34), (2, 0, -4)]))
regrow = svg('<rect width="1080" height="1920" fill="#120A16"/>'
             + mini_skin(0, "#4A1218") + mini_skin(540, "#0E3A3A")
             + f'<g>{myth_hairs}</g>'
             + f'<g transform="translate(810 866)"><g id="realhair">{hair_strand(white=True, h=330, bend=0, seed=2)}</g></g>'
             + '<g id="mythx" opacity="0"><path d="M120 560 L420 860 M420 560 L120 860" stroke="#FF4D4D" stroke-width="40" stroke-linecap="round"/><path d="M120 560 L420 860 M420 560 L120 860" stroke="#1B1414" stroke-width="8" stroke-linecap="round" opacity=".4"/></g>'
             + '<path d="M540 300 V1300" stroke="#fff" stroke-width="6" stroke-dasharray="18 14"/>', "rgsvg") + \
    ('<div class="half l" id="mythh">MİT</div><div class="half r" id="realh">GERÇEK</div>'
     '<div class="tag red" id="mythn" style="left:150px;top:420px;opacity:0">2 → 5?</div><div class="tag" id="realn" style="left:700px;top:420px;opacity:0;background:#22C3A6;color:#fff">1</div>'
     '<div class="tag dark" id="yinebeyaz" style="left:600px;top:560px;opacity:0">YİNE BEYAZ</div>')
JS.append(f'''
tl.fromTo(".mh1 .mhi",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)"}},{s("regrow")+.25});
tl.fromTo(".mh2 .mhi",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)"}},{s("regrow")+.85});
tl.fromTo("#mythn",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.25,ease:"back.out(2)"}},{s("regrow")+.3});
tl.to("#mythx",{{opacity:1,duration:.1}},{A("aynı yerden")});
tl.fromTo("#realhair",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:{max(.8, A("büyük") - A("aynı yerden"))},ease:"power1.out"}},{A("aynı yerden")});
tl.fromTo("#realn",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.25,ease:"back.out(2)"}},{A("tek tel", s("regrow"))});
tl.fromTo("#yinebeyaz",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"back.out(2)"}},{A("yine beyaz")});
''' + punch_js("#rgsvg", A("yine beyaz"), 1.06))
SFX += [(s("regrow") + .25, "pop"), (s("regrow") + .85, "pop"), (A("aynı yerden"), "boom", .6), (A("yine beyaz"), "ding", .6)]

# 4) PEKİ NEDEN? (desen kırıcı)
why = '<div class="fill" style="background:#0A0A0E"></div><div class="big" id="qmark" style="top:330px;font-size:560px;color:#FFD23F">?</div>'
JS.append(f'tl.fromTo("#qmark",{{scale:0,rotation:-30}},{{scale:1,rotation:0,duration:.45,ease:"back.out(2.5)"}},{s("why")+.08});')
SFX += [(s("why") + .08, "pop")]

# 5) HER FOLİKÜLÜN KENDİ SAATİ + YAŞ
cells = []
for r in range(7):
    for c in range(5):
        i = r * 5 + c
        cx, cy = 150 + c * 195 + (r % 2) * 40, 240 + r * 118
        cells.append(f'<g transform="translate({cx} {cy})"><ellipse cx="0" cy="18" rx="30" ry="10" fill="#B07A5A" stroke="{INK}" stroke-width="3"/>'
                     f'<path class="gh" id="gh{i}" d="M-3 18 C-6 -10 4 -30 10 -46" stroke="#2A1E18" stroke-width="9" stroke-linecap="round" fill="none"/>'
                     f'<g transform="translate(46 -26)"><circle r="20" fill="#F4F1EA" stroke="{INK}" stroke-width="3.5"/><path class="hand" d="M0 0 V-14" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/></g></g>')
order = sorted(range(35), key=lambda i: (i * 7919) % 35)
clocks = svg('<rect width="1080" height="1920" fill="#D9A07E"/><rect width="1080" height="1920" fill="url(#grainy)" opacity=".2"/>' + "".join(cells), "clsvg") + \
    '<div class="tag" id="nocont" style="left:200px;top:120px;opacity:0;background:#22C3A6;color:#fff">BULAŞICI DEĞİL</div><div class="agec" id="agec">YAŞ <b id="agen">30</b></div><div class="tag dark" id="notw" style="left:300px;top:1430px;opacity:0">CIMBIZ DEĞİL, YAŞ</div>'
age_t = A("yaşla")
JS.append(f'''
tl.fromTo(".hand",{{rotation:0,transformOrigin:"0 0"}},{{rotation:"+=720",duration:{d("clocks")},ease:"none",stagger:{{each:.03}}}},{s("clocks")});
tl.fromTo("#nocont",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)"}},{A("bulaşıcı")});
''' + "".join(f'tl.to("#gh{i}",{{attr:{{stroke:"#F2F2EE"}},duration:.15}},{s("clocks") + .4 + n * (d("clocks") - .6) / 35:.2f});' for n, i in enumerate(order[:22]))
           + f'tl.fromTo("#agec",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.3}},{age_t});'
           + f'(function(){{const o={{v:30}};tl.to(o,{{v:50,duration:{max(.6, S["clocks"][1]-age_t-.2):.2f},ease:"power1.in",onUpdate:()=>{{document.getElementById("agen").textContent=Math.round(o.v);}}}},{age_t});}})();'
           + f'tl.fromTo("#notw",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"back.out(2)"}},{A("zaten")});')
SFX += [(s("clocks") + i * .25, "tick", .5) for i in range(int(d("clocks") / .25))] + [(age_t, "riser", .7)]

# 6) ASIL BEDEL: aynı folikül tekrar tekrar koparılıyor → iltihap, iz, kel bölge
cost = (f'<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#40202A,#120A16)"></div>'
        + svg(f'<g transform="translate(540 {fol_y}) scale(.62)"><g id="cfol">{follicle(grey=True, stem_ok=True)}</g>'
              f'<circle id="inflam" cx="0" cy="820" r="40" fill="#FF3A2A" opacity="0" filter="url(#glow)"/>'
              f'<g id="scar" opacity="0"><path d="M-300 520 l60 -30 l40 40 l60 -40 l50 30 M80 560 l60 -40 l50 40 l60 -30" stroke="#F7E7DC" stroke-width="16" fill="none" stroke-linecap="round"/>'
              f'<path d="M-300 520 l60 -30 l40 40 l60 -40 l50 30 M80 560 l60 -40 l50 40 l60 -30" stroke="#B8604A" stroke-width="5" fill="none"/></g></g>', "cssvg")
        + '<div class="tag red" id="tt" style="left:300px;top:1430px;opacity:0">TEKRAR TEKRAR</div>'
        + '<div class="words3"><span id="w1">ENFEKSİYON</span><span id="w2">İZ</span><span id="w3">KEL BÖLGE</span></div>'
        + svg('<rect width="1080" height="1920" fill="#C98E6C"/>' + "".join(
            f'<path d="M{(i*97)%1100-10} {(i*53)%1300+200} l{4+(i%3)*3} -26" stroke="{"#F2F2EE" if i % 9 == 0 else "#2A1E18"}" stroke-width="7" stroke-linecap="round"/>'
            for i in range(900) if ((((i*97)%1100-10)-540)**2 + (((i*53)%1300+200)-760)**2) > 190**2)
            + '<ellipse cx="540" cy="760" rx="190" ry="190" fill="#D99A7E" opacity=".85"/><ellipse cx="540" cy="760" rx="150" ry="150" fill="#E2A88A" opacity=".6"/>', "bald", "opacity:0"))
shaft_t = A("tekrar tekrar")
JS.append("".join(f'tl.to("#cfol .shaft",{{y:-260,duration:.12,ease:"power3.in"}},{shaft_t + k*.32:.2f});tl.set("#cfol .shaft",{{y:0}},{shaft_t + k*.32 + .2:.2f});' for k in range(3))
          + "".join(shake_js("#cssvg", shaft_t + k * .32 + .1, 10, 2) for k in range(3))
          + f'tl.fromTo("#tt",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.25,ease:"back.out(2)"}},{shaft_t});'
          + f'tl.to("#inflam",{{opacity:.85,attr:{{r:170}},duration:.4}},{A("enfeksiyona")});tl.fromTo("#w1",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in"}},{A("enfeksiyona")});'
          + f'tl.to("#scar",{{opacity:1,duration:.2}},{A("iz")});tl.fromTo("#w2",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in"}},{A("iz")});'
          + f'tl.to("#bald",{{opacity:1,duration:.15}},{A("kel")});tl.fromTo("#bald",{{scale:1.6,transformOrigin:"50% 40%"}},{{scale:1,duration:.8,ease:"power3.out"}},{A("kel")});'
          + f'tl.fromTo("#w3",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in"}},{A("kel")});')
SFX += [(shaft_t + k * .32, "pluck") for k in range(3)] + [(A("enfeksiyona"), "boom", .5), (A("iz"), "boom", .5), (A("kel"), "boom", .8)]

# 7) MEĞERSE: fare deneyi
meg = ('<div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#2E3A4A,#0A0E14)"></div>'
       + svg('<g transform="translate(540 820) scale(2.2)"><g id="mouse">' + lab_mouse() + '</g></g>'
             + '<g transform="translate(560 640) scale(2.4)"><g id="mtw">' + tweezers(.3) + '</g></g>', "mgsvg")
       + '<div class="megt" id="megt">MEĞERSE</div><div class="tag" id="ftag" style="left:300px;top:1430px;opacity:0">FARE DENEYİ · NATURE 2023</div>')
JS.append(f'''
tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out"}},{s("meg")});
tl.to("#megt",{{y:-640,scale:.55,duration:.5,ease:"power2.inOut"}},{s("meg")+.9});
tl.fromTo("#mouse",{{x:-500}},{{x:0,duration:.5,ease:"power3.out"}},{s("meg")+.6});
tl.fromTo("#ftag",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.3}},{A("farede")});
''' + "".join(f'tl.to("#mtw",{{y:40,duration:.1}},{A("tekrar", s("meg")) + k*.3:.2f});tl.to("#mtw",{{y:0,duration:.14}},{A("tekrar", s("meg")) + k*.3 + .12:.2f});' for k in range(3))
           + flash_js(s("meg"), .9, .35) + punch_js("#mgsvg", s("meg") + .6, 1.1))
SFX += [(s("meg") - .9, "riser", .8), (s("meg"), "boom", 1.0)] + [(A("tekrar", s("meg")) + k * .3, "pluck", .7) for k in range(3)]

# 8) SIKIŞAN KÖK HÜCRELER (trafik)
stuck = ('<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#203040,#0A0E14)"></div>'
         + svg(f'<g transform="translate(540 {fol_y}) scale(.62)">{follicle(grey=False)}'
               + "".join(f'<circle class="mv" cx="{-62 if i % 2 else 62}" cy="380" r="13" fill="#7FC6E8" stroke="{INK}" stroke-width="3"/>' for i in range(4))
               + '<g id="jam" opacity="0"><rect x="-150" y="300" width="300" height="140" rx="26" fill="none" stroke="#FF4D4D" stroke-width="10" stroke-dasharray="26 16"/></g></g>', "stsvg")
         + '<div class="tag" id="sctag" style="left:150px;top:150px;opacity:0;background:#7FC6E8">RENK KÖK HÜCRELERİ</div><div class="tag red" id="jamt" style="left:560px;top:620px;opacity:0">SIKIŞTI</div>')
JS.append(f'''
tl.fromTo(".mv",{{y:0}},{{y:420,duration:.7,stagger:.18,yoyo:true,repeat:3,ease:"sine.inOut"}},{s("stuck")});
tl.fromTo("#sctag",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)"}},{s("stuck")+.1});
tl.to(".mv",{{y:0,attr:{{fill:"#FF4D4D"}},duration:.3,overwrite:true}},{A("sıkışıyor")});
tl.to("#jam",{{opacity:1,duration:.2}},{A("sıkışıyor")});
tl.fromTo("#jamt",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.in"}},{A("sıkışıyor")});
''' + shake_js("#stsvg", A("sıkışıyor"), 8, 4))
SFX += [(A("sıkışıyor"), "boom", .7)]

# 9) %15 → neredeyse yarısı
grid = "".join(f'<circle class="{"g0" if i in (2, 9, 15) else ("g1" if i in (0, 4, 6, 11, 13, 17, 19) else "gx")}" cx="{180 + (i % 5) * 180}" cy="{530 + (i // 5) * 140}" r="56" fill="#3A4A5A" stroke="#fff" stroke-width="6"/>' for i in range(20))
pct = (svg('<rect width="1080" height="1920" fill="#0E1218"/>' + grid, "pcsvg")
       + '<div class="pctn" id="pctn"><b id="pcv">%15</b><span>kök hücresi sıkışan folikül</span></div><div class="tag" id="half" style="left:300px;top:1430px;opacity:0">≈ NEREDEYSE YARISI</div>')
JS.append(f'''
tl.to(".g0",{{attr:{{fill:"#FF4D4D"}},duration:.2,stagger:.1}},{s("pct")+.3});
(function(){{const o={{v:15}};tl.to(o,{{v:50,duration:1.4,ease:"power2.inOut",onUpdate:()=>{{document.getElementById("pcv").textContent=(o.v>=49.5?"≈%50":"%"+Math.round(o.v));}}}},{A("yarıya")-1.2});}})();
tl.to(".g1",{{attr:{{fill:"#FF4D4D"}},duration:.15,stagger:.12}},{A("yarıya")-1.1});
tl.fromTo("#half",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{A("yarıya")+.2});
''')
SFX += [(A("yarıya") - 1.2 + i * .12, "tick", .5) for i in range(11)] + [(A("yarıya") + .2, "ding", .8)]

# 10) FARE ≠ İNSAN
proof = ('<div class="fill" style="background:#14181E"></div>'
         + svg('<g transform="translate(270 820) scale(1.3)">' + lab_mouse(grey=.5) + '</g>'
               + f'<g transform="translate(780 1240) scale(4.6)">{toon_figure(look=(-1, 0), expr=dict(lid=.3, smile=-.2, brow=.4), flip=True, **HERO)}</g>', "prsvg")
         + '<div class="big" id="neq" style="top:520px;font-size:260px;color:#FFD23F">≠</div>'
         + '<div class="tape" id="tape">HENÜZ İNSANDA KANITLANMADI · HENÜZ İNSANDA KANITLANMADI</div>'
         + '<div class="srcn" id="srcn">Sun ve ark., Nature (2023) · fare çalışması</div>')
JS.append(f'''
tl.fromTo("#neq",{{scale:0}},{{scale:1,duration:.35,ease:"back.out(3)"}},{s("proof")+.15});
tl.fromTo("#tape",{{x:-1400}},{{x:0,duration:.4,ease:"power3.out"}},{A("kanıtlanmadı")-.3});
tl.fromTo("#srcn",{{opacity:0}},{{opacity:1,duration:.3}},{s("proof")+.3});
''')
SFX += [(s("proof") + .15, "pop"), (A("kanıtlanmadı") - .3, "whoosh", .8)]

# 11) CTA: aynaya dönüş (döngü)
cta = (mirror_scene("ct", dict(lid=.25, smile=.6, brow=.3))
       + '<div class="ctaq" id="ctaq">SİZDE KAÇ TANE<br>ÇIKAR DENİRDİ?</div><div class="tag" id="ctaw" style="left:250px;top:420px;opacity:0;font-size:64px">RAKAMI YAZ ↓</div>'
       + '<div class="tag dark" id="ctas" style="left:300px;top:1440px;opacity:0;font-size:36px">Cımbızcı arkadaşına gönder</div>')
JS.append(f'''
tl.fromTo("#ctaq",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"back.out(2)"}},{s("cta")+.1});
tl.fromTo("#ctaw",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)"}},{A("Rakamı")});
tl.to("#ctaw",{{y:16,duration:.35,yoyo:true,repeat:5,ease:"sine.inOut"}},{A("Rakamı")+.4});
tl.fromTo("#ctas",{{opacity:0}},{{opacity:1,duration:.3}},{A("Rakamı")+.4});
''')
SFX += [(s("cta"), "swish"), (A("Rakamı"), "pop")]

sources = ('<div class="fill" style="background:#0B0E14"></div><div style="position:absolute;left:70px;right:70px;top:260px" class="src"><b style="color:#FFD23F;font-size:48px">KAYNAKLAR</b><br>'
           'UAMS Health · Medical Myths (2019)<br>Cleveland Clinic · Gray Hair<br>Healthline · Hair follicle pulled out (2021)<br>'
           'Sun ve ark., Nature (2023) · fare çalışması<br><br>Tıbbi tavsiye değildir.</div>')

HTML = dict(hook=hook, dive=dive, regrow=regrow, why=why, clocks=clocks, cost=cost, meg=meg, stuck=stuck, pct=pct, proof=proof, cta=cta, sources=sources)
scenes_html = "".join(scene(k, HTML[k]) for k in keys) + LOCK
# sahne geçişleri: kısa zoom-in + whoosh
js = "".join(f'tl.fromTo("#{k}-in",{{scale:1.12,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.out"}},{s(k)});' for k in keys if k != "hook")
js += "".join(JS)
SFX += [(s(k) - .05, "swish", .6) for k in keys if k not in ("hook", "dive", "meg", "why")]

css = """
.cards { position:absolute; left:0; right:0; top:180px; display:flex; justify-content:center; gap:28px; }
.card { width:170px; height:170px; border-radius:28px; background:#FFF8E6; color:#111; border:7px solid #111; box-shadow:0 10px 0 #111; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:92px; }
.qline { position:absolute; left:0; right:0; top:390px; text-align:center; font-weight:800; font-size:58px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; text-shadow:0 6px 0 #000; }
.stamp { position:absolute; left:250px; top:620px; padding:16px 44px; border:14px solid #FF4D4D; border-radius:24px; color:#FF4D4D; background:rgba(255,248,230,.92); font-weight:800; font-size:150px; letter-spacing:.06em; opacity:0; }
#lock { position:absolute; right:40px; top:150px; width:150px; text-align:center; opacity:0; z-index:60; }
#lock span { display:block; font-weight:800; font-size:26px; color:#FFD23F; -webkit-text-stroke:2px #000; paint-order:stroke fill; }
.lbl { position:absolute; font-weight:800; font-size:40px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; }
.half { position:absolute; top:480px; width:540px; text-align:center; font-weight:800; font-size:76px; color:#fff; -webkit-text-stroke:4px #000; paint-order:stroke fill; }
.half.l { left:0; color:#FF7A7A; } .half.r { left:540px; color:#5EF0D2; }
.agec { position:absolute; right:60px; top:380px; padding:14px 26px; border-radius:20px; background:rgba(10,10,14,.85); border:3px solid #fff; font-weight:800; font-size:44px; opacity:0; }
.agec b { color:#FFD23F; font-size:64px; }
.words3 { position:absolute; left:0; right:0; top:150px; display:flex; flex-direction:column; align-items:center; gap:10px; }
.words3 span { font-weight:800; font-size:78px; color:#FF4D4D; -webkit-text-stroke:4px #000; paint-order:stroke fill; text-shadow:0 6px 0 #000; opacity:0; }
.megt { position:absolute; left:0; right:0; top:760px; text-align:center; font-weight:800; font-size:190px; color:#FFD23F; -webkit-text-stroke:6px #000; paint-order:stroke fill; text-shadow:0 10px 0 #000; opacity:0; }
.pctn { position:absolute; left:0; right:0; top:170px; text-align:center; }
.pctn b { display:block; font-weight:800; font-size:220px; line-height:1; color:#FF4D4D; -webkit-text-stroke:6px #000; paint-order:stroke fill; }
.pctn span { font-weight:600; font-size:40px; color:#D9DEE8; }
.tape { position:absolute; left:-200px; width:1500px; top:1000px; padding:18px 0; background:repeating-linear-gradient(45deg,#FFD23F 0 40px,#111 40px 80px); transform:rotate(-8deg); text-align:center; font-weight:800; font-size:46px; color:#111; }
.tape { background:#FFD23F; border-top:14px solid #111; border-bottom:14px solid #111; }
.srcn { position:absolute; left:0; right:0; top:330px; text-align:center; font-weight:600; font-size:32px; color:#B9C2D0; opacity:0; }
.ctaq { position:absolute; left:0; right:0; top:170px; text-align:center; font-weight:800; font-size:88px; line-height:1.05; color:#fff; -webkit-text-stroke:5px #000; paint-order:stroke fill; text-shadow:0 8px 0 #000; }
"""
DEFS = DEFS2.replace("</defs>", "") + DEFS_P + depth_defs(cam) + "</defs>"
html = page(words, mouth, scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="BEYAZ SAÇ <b>MİTİ</b>",
            voice_src="assets/beyazsac/mix.mp3", extra_css=css, defs=DEFS)
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(ROOT / "reels/beyaz-sac/sfx.json", "w"))
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
