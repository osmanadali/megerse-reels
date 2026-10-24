"""Beyaz saç koparma miti reel'i v2: tam metin (Meğerse sonda, iki fare deneyi), ElevenLabs "Fatih Yıldırım" sesi.

v2 tasarım: anlatıcı (avatar) yok, ekran tamamen sahneye; altyazı v6 (etkin kelime sarı kutuda) 1250-1500 bandında;
görsel alan 120-1220. Her sahnede aynı anda en fazla bir üst etiket (TOP) ve bir alt etiket (LOW), sırayla değişir.
Ses akışı (ses_isle.sh): ElevenLabs mp3 → scripts/tighten.py → scripts/align.py --text metin-v2.txt
         → scripts/insert_gap.py (kancadan sonra intro boşluğu) → reels/beyaz-sac/words-v2.json + hf/assets/beyazsac/voice-v2.mp3
Ses yokken geçici zamanlarla yerleşim testi: BEYAZSAC_GECICI=1
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
from reelkit2 import HF, INTRO_CSS, INTRO_DUR, anchor, flash_js, intro_html, intro_js, intro_sfx, page, punch_js, shake_js  # noqa: E402
from toon import INK, cel, toon_figure  # noqa: E402

GECICI = os.environ.get("BEYAZSAC_GECICI") == "1"
words = json.loads((ROOT / ("reels/beyaz-sac/words-gecici.json" if GECICI else "reels/beyaz-sac/words-v2.json")).read_text(encoding="utf-8"))
VOICE = "assets/beyazsac/gecici.mp3" if GECICI else "assets/beyazsac/mix-v2.mp3"
HOOK_I = next(i for i, w in enumerate(words) if w["text"].lower().startswith("tuhaf"))
if GECICI:   # gerçek seste boşluk insert_gap.py ile eklenir; geçici zamanlarda burada kaydırılır
    for w in words[HOOK_I + 1:]:
        w["startMs"] += int(INTRO_DUR * 1000) + 150
        w["endMs"] += int(INTRO_DUR * 1000) + 150
INTRO_T = round(words[HOOK_I]["endMs"] / 1000 + .1, 2)
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.4, 2)
TOTAL = round(VOICE_END + 3.2, 2)
A = lambda p, after=0.0: anchor(words, p, after)

T = {"hook": 0.0, "intro": INTRO_T, "fol": A("Her saç teli"), "regrow": A("Yani bir teli"), "root": A("Çünkü rengin"), "why": A("Peki neden"),
     "clocks": A("Çünkü beyaz"), "lab": A("Ama işin"), "exp1": A("İlkinde"), "exp2": A("İkincisinde"), "pct": A("Kök hücresi sıkışan"),
     "warn": A("Ama bunlar"), "risk": A("İnsanda bilinen"), "meg": A("Meğerse"), "loop": VOICE_END}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
X = .12
TOP, LOW = 140, 1100          # etiket yuvaları (üst / alt); altyazı 1250-1500
FY, FS = 420, .8              # folikül kesiti: deri yüzeyi y, ölçek


def win(k):
    a, b = S[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


def scene(k, inner, bg="#000"):
    a, d = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{d}" data-track-index="1" style="background:{bg}"><div class="fill" id="{k}-in">{inner}</div></div>'


def svg(inner, idn="", style=""):
    i = f' id="{idn}"' if idn else ""
    return f'<svg class="fill"{i} viewBox="0 0 1080 1920" style="overflow:visible;{style}">{inner}</svg>'


def tag(idn, text, y, cls="", style="", x=None):
    """x verilmezse yatayda ortalı."""
    pos = f"left:{x}px;" if x is not None else ""
    return f'<div class="tag {cls}{"" if x is not None else " c"}" id="{idn}" style="{pos}top:{y}px;opacity:0;{style}">{text}</div>'


def pop_js(sel, t, s0=.4):
    return f'tl.fromTo("{sel}",{{scale:{s0},opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)",immediateRender:false}},{t:.2f});tl.set("{sel}",{{opacity:0}},0);'


def seq_js(items):
    """aynı yuvada sırayla: [(seçici, t), ...]; her biri bir sonrakinin başında kaybolur."""
    out = []
    for i, (sel, t) in enumerate(items):
        out.append(pop_js(sel, t))
        if i + 1 < len(items):
            out.append(f'tl.to("{sel}",{{opacity:0,scale:.9,duration:.15}},{items[i+1][1]-.15:.2f});')
    return "".join(out)


def fol_svg(inner, idn, extra="", fy=FY, fs=FS):
    return svg(f'<g transform="translate(540 {fy}) scale({fs})">{inner}</g>{extra}', idn)


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


# 1) KANCA: ayna + tahmin kartları; "cevap sonda" kilidi kartların yerine gelir
hook = (mirror_scene("hk", dict(lid=.15, smile=-.3, brow=.7))
        + '<div class="cards" id="cards">' + "".join(f'<div class="card" id="cd{i}">{n}</div>' for i, n in enumerate(["1", "2", "5", "10"])) + "</div>"
        + '<div class="qline" id="qline">YERİNE KAÇ TANE ÇIKAR?</div>')
JS.append(f'''
tl.fromTo("#hk-fig",{{attr:{{transform:"translate(560 1700) scale(6.4)"}}}},{{attr:{{transform:"translate(560 1620) scale(5.6)"}},duration:1.4,ease:"power2.out"}},0);
tl.fromTo("#qline",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.3,ease:"back.out(2)"}},{A("Beyaz saçı")});
tl.fromTo(".card",{{y:-160,opacity:0,rotation:-12}},{{y:0,opacity:1,rotation:0,duration:.35,stagger:.12,ease:"back.out(1.8)"}},{A("Beyaz saçı")+.2});
tl.to(".card",{{rotation:8,duration:.06,repeat:7,yoyo:true,ease:"none"}},{A("doğru mu")});
tl.to(".card,#qline",{{y:-260,opacity:0,duration:.3,stagger:.04,ease:"power2.in"}},{A("sandığından")-.2});
''' + punch_js("#hk-svg", A("Beyaz saçı"), 1.07))
SFX += [(0.0, "heartbeat"), (A("Beyaz saçı"), "pop")] + [(A("Beyaz saçı") + .2 + i * .12, "tick", .6) for i in range(4)] + [(A("doğru mu"), "tick")]

LOCK = ('<div id="lock"><svg viewBox="0 0 120 150" width="130" height="162">'
        '<path id="shackle" d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#1B1414" stroke-width="16" stroke-linecap="round"/>'
        '<path d="M30 66 V44 a30 30 0 0 1 60 0 V66" fill="none" stroke="#C9CDD2" stroke-width="9" stroke-linecap="round" id="shackle2"/>'
        '<rect x="12" y="62" width="96" height="80" rx="14" fill="#FFD23F" stroke="#1B1414" stroke-width="7"/><circle cx="60" cy="96" r="10" fill="#1B1414"/><rect x="56" y="100" width="8" height="22" fill="#1B1414"/></svg>'
        '<span>CEVAP SONDA</span></div>')
m0 = A("Meğerse")
JS.append(f'''
tl.fromTo("#lock",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2.4)",immediateRender:false}},{A("sandığından")});tl.set("#lock",{{opacity:0}},0);
tl.to("#lock",{{scale:1.08,duration:.35,yoyo:true,repeat:1,ease:"sine.inOut"}},{A("sandığından")+.4});
tl.to("#lock",{{opacity:0,scale:.6,duration:.2}},{INTRO_T});
tl.fromTo("#lock",{{scale:0,opacity:0}},{{scale:1.15,opacity:1,duration:.3,ease:"back.out(2.4)",immediateRender:false}},{m0-.75});
tl.to("#shackle,#shackle2",{{y:-18,rotation:-28,transformOrigin:"90px 66px",duration:.3,ease:"back.out(3)"}},{m0});
tl.to("#lock",{{scale:2,opacity:0,duration:.35,ease:"power2.in"}},{m0+.3});
''')
SFX += [(A("sandığından"), "heartbeat", .8), (m0 - .75, "pop", .8)]

# 2) FOLİKÜL: kılların arasından ileri kayan kamera → ortada beyaz tel çıkar → kesite geçiş
cam = Cam(horizon=760, vpx=540, f=1000, eye=110, sun=(-1, -.4), alt=46, haze="#E2B89A", zfar=4500)
sc = Scene(cam, "sp", ground=("#C98E6C", "#E2B89A"), sky=False)
for i in range(240):          # deri gözenekleri: zeminde akan doku → hareket hissi
    x, z = ((i * 211) % 2400) - 1200, 120 + ((i * 97) % 80) * 46
    sc.add_ground([(x - 16, z - 9), (x + 16, z - 9), (x + 16, z + 9), (x - 16, z + 9)], 'fill="#A8704F" opacity=".5"')
for i in range(460):
    x, z = ((i * 137) % 2600) - 1300, 150 + (i % 70) * 52
    if abs(x) < 90 and z < 2250:    # kameranın geçeceği koridor; kenardaki teller kadrajdan süzülür
        continue
    hs = hair_strand(white=(i % 19 == 5), h=480 + (i * 53) % 160, bend=((i * 29) % 9 - 4) / 18, seed=i)
    sc.add(x, z, f'<g transform="scale(1.7 1)">{hs}</g>', 640, 420, shadow=False)   # gölge yok: kameraya yakın gölge şeritleri bozuyordu
hero = f'<g transform="scale(2.4 1)">{hair_strand(white=True, h=600, bend=.04, seed=1)}</g>'
sc.add(0, 2080, f'<g id="herogrow"><g filter="url(#glow)" opacity=".8">{hero}</g>{hero}</g>', 640, 330, shadow=False)
fol = (svg('<defs><linearGradient id="scalpsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1810"/><stop offset=".35" stop-color="#8A5A42"/><stop offset=".42" stop-color="#E2B89A"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#scalpsky)"/>')
       + sc.svg()
       + f'<div class="fill" id="folwrap" style="opacity:0;background:{DARK}">{fol_svg(follicle(grey=True, stem_ok=False), "folsvg")}</div>'
       + tag("onefol", "1 FOLİKÜL<br>= 1 TEL", 190, "", "text-align:center", x=60) + f'<div class="lbl" id="lbl1" style="left:610px;top:{FY + FS*480:.0f}px;opacity:0">← FOLİKÜL (yuva)</div>')
y_t, cut = A("yuvadan"), A("folikül.")
JS.append(sc.js() + sc.camera_js(s("fol"), round(y_t - s("fol"), 2), dz=1560, ease="power2.inOut") + sc.camera_js(y_t, round(cut - y_t, 2), dz=140, ease="power1.out"))
JS.append(f'''
tl.fromTo("#herogrow",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:1.0,ease:"power2.out",immediateRender:false}},{y_t-.1});tl.set("#herogrow",{{scaleY:0,transformOrigin:"50% 100%"}},0);
tl.set("#folwrap",{{opacity:1}},{cut-.05});
tl.fromTo("#folsvg",{{scale:2.4,transformOrigin:"50% 22%"}},{{scale:1,duration:.7,ease:"power3.out",immediateRender:false}},{cut-.05});
''' + pop_js("#onefol", A("tek bir tel")) + f'tl.fromTo("#lbl1",{{x:30,opacity:0}},{{x:0,opacity:1,duration:.3,immediateRender:false}},{cut+.3});tl.set("#lbl1",{{opacity:0}},0);' + flash_js(cut - .05, .9, .3))
SFX += [(s("fol"), "whoosh", 1.2), (s("fol") + .9, "whoosh", .7), (y_t - .1, "riser", .5), (y_t + .85, "ding", .6), (cut - .05, "swish"), (A("tek bir tel"), "ding", .7)]


# 3) BÖLÜNMÜŞ EKRAN: mit (yeni yuva, çok tel) vs gerçek (aynı yerden tek tel, yine beyaz)
def mini_skin(x0, tint):
    return (f'<rect x="{x0}" y="760" width="540" height="420" fill="{tint}"/>'
            + cel(f"M{x0} 1180 L{x0} 900 L{x0+540} 900 L{x0+540} 1180 Z", "#F2C4B0", "#D9A890", -1, 8, 5)
            + cel(f"M{x0} 900 L{x0} 860 L{x0+540} 860 L{x0+540} 900 Z", "#E9B996", "#C99876", -1, 4, 5)
            + f'<ellipse cx="{x0+270}" cy="866" rx="22" ry="8" fill="#6A3A2A" stroke="{INK}" stroke-width="4"/>')


myth_hairs = "".join(f'<g transform="translate({270 + dx} 866) rotate({rot})"><g class="mh{grp}">{hair_strand(white=True, h=320 + (i*37) % 80, bend=0, seed=i)}</g></g>'
                     for i, (grp, dx, rot) in enumerate([(1, -14, -18), (1, 14, 18), (2, -26, -34), (2, 26, 34), (2, 0, -4)]))
regrow = svg('<rect width="1080" height="1920" fill="#120A16"/><g transform="translate(0 -110)">' + mini_skin(0, "#4A1218") + mini_skin(540, "#0E3A3A") + f'<g>{myth_hairs}</g>'
             + f'<g transform="translate(810 866)"><g id="realhair">{hair_strand(white=True, h=360, bend=0, seed=2)}</g></g>'
             + '<g id="mythx" opacity="0"><path d="M120 520 L420 820 M420 520 L120 820" stroke="#FF4D4D" stroke-width="40" stroke-linecap="round"/></g></g>'
             + '<path d="M540 150 V1210" stroke="#fff" stroke-width="6" stroke-dasharray="18 14"/>', "rgsvg") + \
    ('<div class="half l">MİT</div><div class="half r">GERÇEK</div>'
     + tag("mythn", "YENİ YUVA? ✗", LOW - 10, "red", x=95) + tag("realn", "AYNI YUVA · 1 TEL", LOW - 10, "", "background:#22C3A6;color:#fff;font-size:38px", x=585)
     + tag("yinebeyaz", "YİNE BEYAZ", LOW - 10, "dark", x=655))
JS.append(f'''
tl.fromTo(".mh1",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)",immediateRender:false}},{s("regrow")+.2});
tl.fromTo(".mh2",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,stagger:.08,ease:"back.out(3)",immediateRender:false}},{s("regrow")+.6});
tl.set(".mh1,.mh2",{{scale:0}},0);
tl.to("#mythx",{{opacity:1,duration:.1}},{A("açılmaz")});
tl.fromTo("#realhair",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:1.2,ease:"power1.out"}},{A("Aynı yerden")});
''' + pop_js("#mythn", A("açılmaz")) + seq_js([("#realn", A("tek bir tel", s("regrow"))), ("#yinebeyaz", A("yine beyaz"))]) + punch_js("#rgsvg", A("yine beyaz"), 1.06))
SFX += [(s("regrow") + .2, "pop"), (s("regrow") + .6, "pop"), (A("açılmaz"), "boom", .6), (A("yine beyaz"), "ding", .6)]

# 4) KÖK: rengin kararı kökte; pigment hücresi yok → kamera soğana iner
BULB_Y = FY + FS * 880
root = (f'<div class="fill" style="background:{DARK}"></div>'
        + fol_svg(f'<g id="rtfol">{follicle(grey=True, stem_ok=False)}</g>', "rtsvg",
                  f'<circle id="rtring" cx="540" cy="{BULB_Y:.0f}" r="100" fill="none" stroke="#FFD23F" stroke-width="9" stroke-dasharray="20 12" opacity="0"/>')
        + tag("rt1", "RENK KÖKTE VERİLİR", TOP) + tag("rt2", "PİGMENT YOK → BEYAZ", TOP, "dark"))
JS.append(f'tl.fromTo("#rtsvg",{{scale:1,y:0,transformOrigin:"540px {BULB_Y:.0f}px"}},{{scale:1.55,y:-300,duration:{d("root")},ease:"power1.inOut"}},{s("root")});'
          f'tl.to("#rtring",{{opacity:1,duration:.2}},{A("kökte")});' + seq_js([("#rt1", A("kökte")), ("#rt2", A("pigment"))]))
SFX += [(A("kökte"), "ding", .5)]

# 5) PEKİ NEDEN?
why = '<div class="fill" style="background:#0A0A0E"></div><div class="big" id="qmark" style="top:300px;font-size:600px;color:#FFD23F">?</div>'
JS.append(f'tl.fromTo("#qmark",{{scale:0,rotation:-30}},{{scale:1,rotation:0,duration:.45,ease:"back.out(2.5)",immediateRender:false}},{s("why")+.08});')
SFX += [(s("why") + .08, "pop")]

# 6) HER FOLİKÜLÜN KENDİ SAATİ + YAŞ
cells = []
for r in range(7):
    for c in range(5):
        i = r * 5 + c
        cx, cy = 150 + c * 195 + (r % 2) * 40, 330 + r * 118
        cells.append(f'<g transform="translate({cx} {cy})"><ellipse cx="0" cy="18" rx="30" ry="10" fill="#B07A5A" stroke="{INK}" stroke-width="3"/>'
                     f'<path id="gh{i}" d="M-3 18 C-6 -10 4 -30 10 -46" stroke="#2A1E18" stroke-width="9" stroke-linecap="round" fill="none"/>'
                     f'<g transform="translate(46 -26)"><circle r="20" fill="#F4F1EA" stroke="{INK}" stroke-width="3.5"/><path class="hand" d="M0 0 V-14" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/></g></g>')
order = sorted(range(35), key=lambda i: (i * 7919) % 35)
clocks = svg('<rect width="1080" height="1920" fill="#D9A07E"/>' + "".join(cells), "clsvg") + \
    tag("nocont", "BULAŞICI DEĞİL", TOP, "", "background:#22C3A6;color:#fff") + tag("notw", "CIMBIZ DEĞİL · ZAMAN", TOP, "dark") + '<div class="agec" id="agec">YAŞ <b id="agen">30</b></div>'
age_t = A("Yaşla")
JS.append(f'tl.fromTo(".hand",{{rotation:0,transformOrigin:"0 0"}},{{rotation:"+=720",duration:{d("clocks")},ease:"none",stagger:{{each:.03}}}},{s("clocks")});'
          + seq_js([("#nocont", A("bulaşıcı")), ("#notw", A("Sen kopardığın"))])
          + "".join(f'tl.to("#gh{i}",{{attr:{{stroke:"#F2F2EE"}},duration:.15}},{s("clocks") + .4 + n * (d("clocks") - .6) / 35:.2f});' for n, i in enumerate(order[:24]))
          + f'tl.fromTo("#agec",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.3,immediateRender:false}},{age_t});tl.set("#agec",{{opacity:0}},0);'
          + f'(function(){{const o={{v:30}};tl.to(o,{{v:55,duration:{max(.6, S["clocks"][1]-age_t-.3):.2f},ease:"power1.in",onUpdate:()=>{{document.getElementById("agen").textContent=Math.round(o.v);}}}},{age_t});}})();')
SFX += [(s("clocks") + i * .3, "tick", .45) for i in range(int(d("clocks") / .3))] + [(age_t, "riser", .6)]

# 7) LABORATUVAR: iki deney
lab_bg = ('<rect width="1080" height="1920" fill="#1C2A36"/>' + light_shafts(80, 0, angle=-18, n=4, length=1500, spread=170, col="#CFE8FF", op=.18)
          + '<rect y="1180" width="1080" height="740" fill="#2E3E4C"/>' + cel("M0 1150 L1080 1150 L1080 1210 L0 1210 Z", "#C9D2D8", "#9AA6AE", -1, 8, 6)
          + "".join(f'<g transform="translate({x} 1150) scale(1.35)">' + cel("M-150 0 L-150 -300 L150 -300 L150 0 Z", "#9FC3D6", "#6E96AA", -1, 10, 6)
                    + "".join(f'<path d="M{-150+k*30} -300 V0" stroke="#5A7A8A" stroke-width="5"/>' for k in range(11))
                    + f'<g transform="translate(0 -20) scale(.9)">{lab_mouse()}</g>'
                    + f'<rect x="-120" y="-380" width="240" height="64" rx="14" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/><text x="0" y="-336" text-anchor="middle" font-family="Mont" font-weight="800" font-size="38" fill="#1B1414">DENEY {n}</text></g>'
                    for n, x in ((1, 290), (2, 790))))
lab = svg(lab_bg, "labsvg") + tag("labt", "LABORATUVAR", TOP, "dark")
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
            + '<circle id="wave1" cx="540" cy="700" r="130" fill="none" stroke="#5EF0D2" stroke-width="10" opacity="0"/>'
            + '<g id="zzz" opacity="0">' + "".join(f'<text x="{x}" y="{y}" font-family="Mont" font-weight="800" font-size="{fs}" fill="#9FC3D6" stroke="#000" stroke-width="5" paint-order="stroke">z</text>' for x, y, fs in [(300, 560, 50), (330, 520, 64), (370, 470, 80), (740, 900, 50), (770, 860, 64)]) + '</g>'
            + '<g id="alarm" opacity="0" transform="translate(870 470)"><circle r="70" fill="#FF4D4D" stroke="#1B1414" stroke-width="8"/><circle r="52" fill="#FFF8E6"/><path d="M0 0 V-34 M0 0 L22 14" stroke="#1B1414" stroke-width="7" stroke-linecap="round"/><circle cx="-56" cy="-60" r="22" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/><circle cx="56" cy="-60" r="22" fill="#FFD23F" stroke="#1B1414" stroke-width="6"/></g>', "e1svg")
        + tag("e1t", "DENEY 1 · CELL 2015 · FARE", TOP) + '<div class="cnt" id="c200"><b id="n200">0</b> kıl koparıldı</div><div class="cnt" id="c1300"><b id="n1300">0</b> kıl yeniden büyüdü</div>'
        + tag("e1w", "YENİ YUVA YOK · UYKUDAKİLER UYANDI", LOW - 50, "dark", "font-size:32px"))
t200, t1300 = A("iki yüz"), A("bin üç")
JS.append(pop_js("#e1t", s("exp1") + .1)
          + f'tl.to(".pk",{{y:-140,opacity:0,duration:.35,stagger:{{each:.004,from:"center"}},ease:"power2.in"}},{t200});'
          + f'tl.fromTo("#c200",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{t200});tl.set("#c200",{{opacity:0}},0);'
          + f'(function(){{const o={{v:0}};tl.to(o,{{v:200,duration:.6,ease:"power1.out",onUpdate:()=>{{document.getElementById("n200").textContent=Math.round(o.v);}}}},{t200});}})();'
          + f'tl.to("#c200",{{opacity:0,duration:.2}},{t1300-.1});'
          + f'tl.fromTo("#wave1",{{attr:{{r:130}},opacity:.9}},{{attr:{{r:300}},opacity:0,duration:.9,ease:"power2.out",immediateRender:false}},{t1300});'
          + f'tl.fromTo(".sp",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:.5,stagger:{{each:.0025,from:"center"}},ease:"back.out(2)",immediateRender:false}},{t1300});tl.set(".sp",{{scaleY:0}},0);'
          + f'tl.fromTo("#c1300",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{t1300});tl.set("#c1300",{{opacity:0}},0);'
          + f'(function(){{const o={{v:0}};tl.to(o,{{v:1300,duration:1.3,ease:"power2.out",onUpdate:()=>{{document.getElementById("n1300").textContent=(o.v>=1295?"≈1300":Math.round(o.v));}}}},{t1300});}})();'
          + f'tl.to("#zzz",{{opacity:1,duration:.2}},{A("Uykudaki")});tl.to("#zzz",{{opacity:0,duration:.2}},{A("alarm")+.2});'
          + f'tl.to("#alarm",{{opacity:1,duration:.1}},{A("alarm")});tl.fromTo("#alarm",{{rotation:-12}},{{rotation:12,duration:.05,repeat:15,yoyo:true,ease:"none",immediateRender:false}},{A("alarm")});'
          + pop_js("#e1w", A("topluca")) + punch_js("#e1svg", t1300, 1.06))
SFX += [(t200, "pluck"), (t200 + .15, "pluck", .7), (t1300, "riser", .5), (t1300 + .5, "boom", .7)] + [(A("alarm") + i * .1, "tick", .7) for i in range(8)]

# 9) DENEY 2 (Nature 2023, fare): renk kök hücreleri gidip gelir; yaşlanınca sıkışır; tekrarlı koparma
exp2 = (f'<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#203040,#0A0E14)"></div>'
        + fol_svg(f'<g id="e2fol">{follicle(grey=False)}</g>'
                  + "".join(f'<circle class="mv" cx="{-62 if i % 2 else 62}" cy="380" r="22" fill="#7FC6E8" stroke="{INK}" stroke-width="4"/>' for i in range(4))
                  + '<g id="jam" opacity="0"><rect x="-160" y="290" width="320" height="160" rx="28" fill="none" stroke="#FF4D4D" stroke-width="11" stroke-dasharray="26 16"/></g>', "e2svg",
                  '<g transform="translate(556 250) scale(2.2)"><g id="e2tw" opacity="0">' + tweezers(.3) + '</g></g>', fy=330, fs=.7)
        + tag("e2t", "DENEY 2 · NATURE 2023 · FARE", TOP, "", "background:#7FC6E8")
        + tag("e2a", "RENK KÖK HÜCRELERİ", LOW, "dark") + tag("e2b", "SIKIŞTI → RENK YOK", LOW, "red") + tag("e2c", "TEKRAR TEKRAR KOPARMA", LOW, "dark"))
tk = A("tekrar tekrar koparıp")
JS.append(pop_js("#e2t", s("exp2") + .1) + f'tl.to("#e2t",{{opacity:0,duration:.2}},{tk-.4:.2f});tl.to("#e2tw",{{opacity:1,duration:.2}},{tk-.35:.2f});'
          + f'tl.fromTo(".mv",{{y:0}},{{y:420,duration:.7,stagger:.18,yoyo:true,repeat:5,ease:"sine.inOut",immediateRender:false}},{A("aşağı yukarı")-.3});'
          + f'tl.to(".mv",{{y:0,attr:{{fill:"#FF4D4D"}},duration:.3,overwrite:true}},{A("sıkışıp")});tl.to("#jam",{{opacity:1,duration:.2}},{A("sıkışıp")});'
          + seq_js([("#e2a", A("kök hücreleri")), ("#e2b", A("sıkışıp")), ("#e2c", tk)]) + shake_js("#e2svg", A("sıkışıp"), 8, 4)
          + "".join(f'tl.to("#e2fol .shaft",{{y:-260,duration:.12,ease:"power3.in"}},{tk + k*.32:.2f});tl.set("#e2fol .shaft",{{y:0}},{tk + k*.32 + .2:.2f});'
                    f'tl.to("#e2tw",{{y:-50,duration:.12,ease:"power3.in"}},{tk + k*.32:.2f});tl.to("#e2tw",{{y:0,duration:.14}},{tk + k*.32 + .14:.2f});' for k in range(3)))
SFX += [(A("sıkışıp"), "boom", .7)] + [(tk + k * .32, "pluck") for k in range(3)]

# 10) %15 → NEREDEYSE YARISI: iki cam tüp; sıvı seviyesi yükselir (dalgalı yüzey + kabarcık)
P_TOP, P_BOT, P_W = 390, 1030, 230
PH = P_BOT - P_TOP
C1, C2 = 300, 780


def tube(cx, idn, g1, g2, L, n_rep):
    x0, x1, r = cx - P_W / 2, cx + P_W / 2, P_W / 2
    inner = f"M{x0} {P_TOP} V{P_BOT-r} A{r} {r} 0 0 0 {x1} {P_BOT-r} V{P_TOP} Z"
    p, a, xs = P_W / 2, 11, x0 - P_W
    wave = f"M{xs} {P_BOT} q{p/4} {-a} {p/2} 0" + "".join(f" t{p/2} 0" for _ in range(9)) + f" V{P_BOT+800} H{xs} Z"
    bb = "".join(f'<circle class="{idn}-bb" cx="{x0+30+(k*47) % (P_W-60):.0f}" cy="{P_BOT+PH*L-24-(k*13) % 30:.0f}" r="{5+(k % 3)*3}" fill="#fff" fill-opacity=".6"/>' for k in range(8))
    ticks = "".join(f'<path d="M{x0+6} {P_BOT - PH*k/10:.0f} h{40 if k == 5 else 22}" stroke="#fff" stroke-opacity=".6" stroke-width="4"/>' for k in range(1, 10))
    defs_ = (f'<clipPath id="{idn}-cl"><path d="{inner}"/></clipPath>'
             f'<linearGradient id="{idn}-lg" gradientUnits="userSpaceOnUse" x1="0" y1="{P_BOT}" x2="0" y2="{P_BOT+360}"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient>')
    art = (f'<defs>{defs_}</defs><ellipse cx="{cx}" cy="{P_BOT+14}" rx="{r+30}" ry="22" fill="#000" opacity=".45"/>'
           f'<path d="{inner}" fill="#9FC3D6" fill-opacity=".10"/>'
           f'<g clip-path="url(#{idn}-cl)"><g id="{idn}-lv"><g id="{idn}-wv"><path d="{wave}" fill="url(#{idn}-lg)"/></g>{bb}</g></g>'
           f'<path d="M{x0} {P_TOP-12} V{P_BOT-r} A{r} {r} 0 0 0 {x1} {P_BOT-r} V{P_TOP-12}" fill="none" stroke="#E6F0F6" stroke-width="9" stroke-linecap="round"/>'
           f'<rect x="{x0+26}" y="{P_TOP+24}" width="18" height="{PH-r-50}" rx="9" fill="#fff" opacity=".24"/>'
           f'<ellipse cx="{cx}" cy="{P_TOP-12}" rx="{r+12}" ry="16" fill="none" stroke="#E6F0F6" stroke-width="8"/>' + ticks)
    js = (f'tl.fromTo("#{idn}-wv",{{x:0}},{{x:{p},duration:.9,ease:"none",repeat:{n_rep},immediateRender:false}},{s("pct")});'
          f'tl.fromTo(".{idn}-bb",{{y:0,opacity:0}},{{y:{-(PH*L-50):.0f},opacity:1,duration:1.0,ease:"power1.in",stagger:{{each:.17,repeat:{n_rep}}},immediateRender:false}},{s("pct")+.3});')
    return f'<g id="{idn}">{art}</g>', js


nrep = int(d("pct") / .9) + 2
tb1, tj1 = tube(C1, "tb1", "#FFE27A", "#E8A21A", .15, nrep)
tb2, tj2 = tube(C2, "tb2", "#FF7A6A", "#B8231A", .5, nrep)
y50 = P_BOT - PH * .5
pct = (svg('<rect width="1080" height="1920" fill="#0B121A"/>' + light_shafts(540, 0, angle=0, n=3, length=1300, spread=260, col="#CFE8FF", op=.12)
           + cel("M0 1040 L1080 1040 L1080 1230 L0 1230 Z", "#22303C", "#18222C", -1, 8, 6) + tb1 + tb2
           + f'<g id="l50" opacity="0"><path d="M120 {y50:.0f} H960" stroke="#FFD23F" stroke-width="6" stroke-dasharray="22 14"/>'
           + f'<text x="540" y="{y50-16:.0f}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="40" fill="#FFD23F" stroke="#000" stroke-width="6" paint-order="stroke">YARI</text></g>', "pcsvg")
       + tag("pch", "SIKIŞAN KÖK HÜCRELİ FOLİKÜL · FARE", TOP - 10, "dark", "font-size:32px")
       + f'<div class="tnum" id="tn1" style="left:{C1-220}px">%15</div><div class="tnum" id="tn2" style="left:{C2-220}px"><span id="tn2v">%15</span></div>'
       + f'<div class="tlab" style="left:{C1-220}px">KOPARMADAN<br>ÖNCE</div><div class="tlab" style="left:{C2-220}px">TEKRAR TEKRAR<br>KOPARINCA</div>')
t15, tn = A("yüzde"), A("neredeyse")
JS.append(tj1 + tj2 + pop_js("#pch", s("pct") + .1)
          + f'tl.fromTo("#tb1,#tb2",{{y:500,opacity:0}},{{y:0,opacity:1,duration:.45,stagger:.12,ease:"back.out(1.4)",immediateRender:false}},{s("pct")+.05});'
          + f'tl.fromTo(".tlab",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{s("pct")+.4});tl.set(".tlab",{{opacity:0}},0);'
          + f'tl.fromTo("#tb1-lv,#tb2-lv",{{y:0}},{{y:{-PH*.15:.0f},duration:.7,ease:"power2.out",immediateRender:false}},{t15});'
          + pop_js("#tn1", t15 + .2) + pop_js("#tn2", t15 + .2)
          + f'tl.to("#tb2-lv",{{y:{-PH*.5:.0f},duration:1.3,ease:"power2.inOut"}},{tn-.2});'
          + f'(function(){{const o={{v:15}};tl.to(o,{{v:50,duration:1.3,ease:"power2.inOut",onUpdate:()=>{{document.getElementById("tn2v").textContent=(o.v>=49.5?"≈%50":"%"+Math.round(o.v));}}}},{tn-.2});}})();'
          + f'tl.to("#tn2",{{color:"#FF4D4D",scale:1.2,duration:.25,ease:"back.out(3)"}},{A("yarıya")});tl.to("#tn2",{{scale:1,duration:.3}},{A("yarıya")+.25});'
          + f'tl.fromTo("#l50",{{opacity:0,scaleX:0,transformOrigin:"0 50%"}},{{opacity:1,scaleX:1,duration:.4,ease:"power2.out",immediateRender:false}},{A("yarıya")});'
          + punch_js("#pcsvg", A("yarıya"), 1.05))
SFX += [(s("pct") + .05, "whoosh", .8), (t15, "pop", .7)] + [(tn - .2 + i * .12, "tick", .5) for i in range(11)] + [(A("yarıya"), "ding", .8)]

# 11) FARE ≠ İNSAN
warn = ('<div class="fill" style="background:#14181E"></div>'
        + svg('<g transform="translate(270 820) scale(1.3)">' + lab_mouse(grey=.5) + '</g>'
              + f'<g transform="translate(780 1210) scale(4.5)">{toon_figure(look=(-1, 0), expr=dict(lid=.3, smile=-.2, brow=.4), flip=True, **HERO)}</g>', "prsvg")
        + '<div class="big" id="neq" style="top:480px;font-size:260px;color:#FFD23F">≠</div>'
        + '<div class="tape" id="tape">HENÜZ İNSANDA KANITLANMADI · HENÜZ İNSANDA KANITLANMADI</div>')
JS.append(f'tl.fromTo("#neq",{{scale:0}},{{scale:1,duration:.35,ease:"back.out(3)",immediateRender:false}},{s("warn")+.15});'
          f'tl.fromTo("#tape",{{x:-1400}},{{x:0,duration:.4,ease:"power3.out",immediateRender:false}},{A("kanıtlanmadı")-.3});tl.set("#tape",{{x:-1400}},0);')
SFX += [(s("warn") + .15, "pop"), (A("kanıtlanmadı") - .3, "whoosh", .8)]

# 12) İNSANDAKİ RİSK: tekrar tekrar koparma → enfeksiyon, iz, kel bölge (kelimeler tek tek, aynı yuvada)
risk = (f'<div class="fill" style="background:radial-gradient(70% 50% at 50% 35%,#40202A,#120A16)"></div>'
        + fol_svg(f'<g id="cfol">{follicle(grey=True, stem_ok=True)}</g>'
                  f'<circle id="inflam" cx="0" cy="820" r="40" fill="#FF3A2A" opacity="0" filter="url(#glow)"/>'
                  f'<g id="scar" opacity="0"><path d="M-300 520 l60 -30 l40 40 l60 -40 l50 30 M80 560 l60 -40 l50 40 l60 -30" stroke="#F7E7DC" stroke-width="16" fill="none" stroke-linecap="round"/></g>', "cssvg")
        + svg('<rect width="1080" height="1920" fill="#C98E6C"/>' + "".join(
            f'<path d="M{(i*97)%1100-10} {(i*53)%1100+130} l{4+(i%3)*3} -26" stroke="{"#F2F2EE" if i % 9 == 0 else "#2A1E18"}" stroke-width="7" stroke-linecap="round"/>'
            for i in range(900) if ((((i*97)%1100-10)-540)**2 + (((i*53)%1100+130)-680)**2) > 190**2)
            + '<ellipse cx="540" cy="680" rx="190" ry="190" fill="#D99A7E" opacity=".85"/>', "bald", "opacity:0")
        + tag("tt", "TEKRAR TEKRAR", TOP, "red") + tag("w1", "ENFEKSİYON", TOP, "red", "font-size:60px") + tag("w2", "İZ", TOP, "red", "font-size:60px") + tag("w3", "KEL BÖLGE", TOP, "red", "font-size:60px"))
sh_t = A("tekrar tekrar koparmak")
JS.append("".join(f'tl.to("#cfol .shaft",{{y:-260,duration:.12,ease:"power3.in"}},{sh_t + k*.32:.2f});tl.set("#cfol .shaft",{{y:0}},{sh_t + k*.32 + .2:.2f});' + shake_js("#cssvg", sh_t + k * .32 + .1, 10, 2) for k in range(3))
          + seq_js([("#tt", sh_t), ("#w1", A("enfeksiyona")), ("#w2", A("iz kalmasına")), ("#w3", A("kel"))])
          + f'tl.to("#w3",{{opacity:0,duration:.15}},{m0-.9});'
          + f'tl.to("#inflam",{{opacity:.85,attr:{{r:170}},duration:.4}},{A("enfeksiyona")});tl.to("#scar",{{opacity:1,duration:.2}},{A("iz kalmasına")});'
          + f'tl.to("#bald",{{opacity:1,duration:.15}},{A("kel")});tl.fromTo("#bald",{{scale:1.6,transformOrigin:"50% 35%"}},{{scale:1,duration:.8,ease:"power3.out",immediateRender:false}},{A("kel")});')
SFX += [(sh_t + k * .32, "pluck") for k in range(3)] + [(A("enfeksiyona"), "boom", .5), (A("iz kalmasına"), "boom", .5), (A("kel"), "boom", .8)]

# 13) MEĞERSE (final): kilit ortada açılır, büyük cevap, sonra uyarı
meg = ('<div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#3A2A10,#0A0806)"></div>'
       + '<div class="megt" id="megt">MEĞERSE</div>'
       + '<div class="ans" id="ans1"><i>✓</i>KOPARINCA BEYAZ<br>ÇOĞALMIYOR</div>'
       + svg('<rect width="1080" height="1920" fill="#C98E6C"/>' + "".join(
           f'<path d="M{(i*97)%1100-10} {(i*53)%1100+130} l{4+(i%3)*3} -26" stroke="{"#F2F2EE" if i % 7 == 0 else "#2A1E18"}" stroke-width="7" stroke-linecap="round"/>'
           for i in range(900) if ((((i*97)%1100-10)-540)**2 + (((i*53)%1100+130)-700)**2) > 150**2)
           + '<circle id="spot" cx="540" cy="700" r="150" fill="#D99A7E"/>', "megbald", "opacity:0")
       + tag("ans2", "KOPARMAYA DEVAM EDERSEN…", LOW - 40, "red", "font-size:38px"))
JS.append(flash_js(m0, .95, .4) + shake_js("#meg-in", m0, 14, 6)
          + f'tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out",immediateRender:false}},{m0+.1});tl.set("#megt",{{opacity:0}},0);'
          + f'tl.to("#megt",{{y:-540,scale:.6,duration:.5,ease:"power2.inOut"}},{A("yıllardır")});'
          + f'tl.fromTo("#ans1",{{scale:.4,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2.4)",immediateRender:false}},{A("koparınca beyaz")});tl.set("#ans1",{{opacity:0}},0);'
          + f'tl.to("#ans1",{{opacity:0,y:-60,duration:.3}},{A("Ama koparmaya")});'
          + f'tl.to("#megbald",{{opacity:1,duration:.3}},{A("Ama koparmaya")});tl.fromTo("#megbald",{{scale:1.8,transformOrigin:"50% 36%"}},{{scale:1,duration:1.2,ease:"power2.out",immediateRender:false}},{A("Ama koparmaya")});'
          + pop_js("#ans2", A("Ama koparmaya")) + f'tl.to("#megt",{{opacity:0,duration:.3}},{A("Ama koparmaya"):.2f});'
          + f'tl.fromTo("#spot",{{attr:{{r:20}}}},{{attr:{{r:150}},duration:1.6,ease:"power2.inOut",immediateRender:false}},{A("hiç saç")-.6});')
SFX += [(m0 - 1.2, "riser", 1.0), (m0, "boom", 1.0), (A("koparınca beyaz"), "ding"), (A("hiç saç"), "heartbeat", .9)]

# 14) DÖNGÜ KARTI (sessiz): aynaya dönüş + ekranda yorum sorusu (sözlü çağrı yok)
loop = (mirror_scene("ct", dict(lid=.15, smile=-.3, brow=.7))
        + '<div class="ctaq" id="ctaq">SİZDE KAÇ TANE<br>ÇIKAR DENİRDİ? 👇</div>')
JS.append(f'tl.fromTo("#ctaq",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{s("loop")+.2});tl.set("#ctaq",{{opacity:0}},0);'
          f'tl.fromTo("#ct-fig",{{attr:{{transform:"translate(560 1620) scale(5.6)"}}}},{{attr:{{transform:"translate(560 1700) scale(6.4)"}},duration:{d("loop")},ease:"power1.in",immediateRender:false}},{s("loop")});')
SFX += [(s("loop"), "swish"), (s("loop") + .2, "pop", .7), (0.0, "heartbeat")]

# İNTRO
intro = intro_html("05")
JS.append(intro_js(s("intro")))
SFX += intro_sfx(s("intro"))

HTML = dict(hook=hook, intro=intro, fol=fol, regrow=regrow, root=root, why=why, clocks=clocks, lab=lab, exp1=exp1, exp2=exp2, pct=pct, warn=warn, risk=risk, meg=meg, loop=loop)
scenes_html = "".join(scene(k, HTML[k]) for k in keys) + LOCK
js = "".join(f'tl.fromTo("#{k}-in",{{scale:1.12,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.out",immediateRender:false}},{s(k)});' for k in keys if k not in ("hook", "intro"))
js += "".join(JS)
SFX += [(s(k) - .05, "swish", .6) for k in keys if k not in ("hook", "intro", "fol", "meg", "why", "loop")]

css = """
.tag.c { left:0; right:0; margin:0 auto; width:fit-content; }
.cards { position:absolute; left:0; right:0; top:150px; display:flex; justify-content:center; gap:28px; }
.card { width:170px; height:170px; border-radius:28px; background:#FFF8E6; color:#111; border:7px solid #111; box-shadow:0 10px 0 #111; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:92px; }
.qline { position:absolute; left:0; right:0; top:350px; text-align:center; font-weight:800; font-size:58px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; text-shadow:0 6px 0 #000; }
#lock { position:absolute; left:0; right:0; margin:0 auto; top:150px; width:320px; text-align:center; opacity:0; z-index:60; }
#lock span { display:block; margin-top:6px; font-weight:800; font-size:40px; color:#FFD23F; -webkit-text-stroke:3px #000; paint-order:stroke fill; text-shadow:0 5px 0 #000; }
.lbl { position:absolute; font-weight:800; font-size:40px; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; }
.half { position:absolute; top:170px; width:540px; text-align:center; font-weight:800; font-size:84px; -webkit-text-stroke:4px #000; paint-order:stroke fill; }
.half.l { left:0; color:#FF7A7A; } .half.r { left:540px; color:#5EF0D2; }
.agec { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:1100px; padding:12px 30px; border-radius:20px; background:rgba(10,10,14,.85); border:3px solid #fff; font-weight:800; font-size:46px; opacity:0; }
.agec b { color:#FFD23F; font-size:66px; }
.cnt { position:absolute; left:0; right:0; top:240px; text-align:center; font-weight:600; font-size:40px; color:#fff; opacity:0; -webkit-text-stroke:2px #000; paint-order:stroke fill; }
.cnt b { font-weight:800; font-size:110px; color:#FFD23F; -webkit-text-stroke:5px #000; }
#c200 b { color:#FF4D4D; }
.megt { position:absolute; left:0; right:0; top:680px; text-align:center; font-weight:800; font-size:200px; color:#FFD23F; -webkit-text-stroke:7px #000; paint-order:stroke fill; text-shadow:0 12px 0 #000; opacity:0; z-index:5; }
.ans { position:absolute; left:60px; right:60px; top:540px; padding:36px 30px; border-radius:36px; background:#22C3A6; border:8px solid #111; box-shadow:0 14px 0 #111; text-align:center; font-weight:800; font-size:86px; line-height:1.05; color:#fff; -webkit-text-stroke:3px #000; paint-order:stroke fill; opacity:0; }
.ans i { display:block; font-style:normal; font-size:120px; }
.tnum { position:absolute; top:215px; width:440px; text-align:center; font-weight:800; font-size:130px; line-height:1; color:#FFD23F; -webkit-text-stroke:5px #000; paint-order:stroke fill; text-shadow:0 8px 0 #000; opacity:0; }
.tlab { position:absolute; top:1062px; width:440px; text-align:center; font-weight:800; font-size:34px; line-height:1.15; color:#DDE6EE; opacity:0; }
.tape { position:absolute; left:-200px; width:1500px; top:1000px; padding:18px 0; background:#FFD23F; border-top:14px solid #111; border-bottom:14px solid #111; transform:rotate(-8deg); text-align:center; font-weight:800; font-size:46px; color:#111; }
.ctaq { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; top:150px; padding:26px 44px; border-radius:34px; background:rgba(12,12,18,.88); border:5px solid #FFD23F; text-align:center; font-weight:800; font-size:70px; line-height:1.08; color:#fff; }
"""
DEFS = DEFS2.replace("</defs>", "") + DEFS_P + depth_defs(cam) + "</defs>"
html = page(words, [], scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="", voice_src=VOICE, extra_css=css + INTRO_CSS, defs=DEFS,
            avatar=False, chrome=False, caps="box")
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(ROOT / "reels/beyaz-sac/sfx-v2.json", "w"))
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
