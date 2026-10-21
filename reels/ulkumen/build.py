"""Selahattin Ülkümen reel'i (2D çizgi film karakterleri + derinlik sistemi): hf/index.html üretir.

python3 reels/ulkumen/build.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/ulkumen-v1.mp4)
Kurallar: hf/art/DERINLIK.md (perspektif, gölge, pus, kamera; karakterler toon.py, konuşan birbirine döner).
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, Scene, defs as depth_defs, tree_simple  # noqa: E402
from portrait import DEFS_P, chiaroscuro, light_shafts  # noqa: E402
from reelkit import HF, anchor, page  # noqa: E402
from toon import TOON_H, cel, line, toon_figure  # noqa: E402

words = json.loads((ROOT / "reels/ulkumen/words.json").read_text(encoding="utf-8"))
mouth = json.loads((HF / "avatar/mouth-ulkumen.json").read_text())
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.6, 2)
TOTAL = round(VOICE_END + 4, 2)
FADE = 0.45
A = lambda p, after=0.0: anchor(words, p, after)

T = {
    "hook": 0.0, "island": A("1944,"), "consul": A("Türkiye'nin"), "bomb": A("Şubat"), "roundup": A("Temmuz."),
    "dest": A("Gerçek varış"), "confront": A("Ülkümen, Alman"), "cmd": A("Komutan itiraz"), "reply": A("Ülkümen'in cevabı"),
    "list": A("Ve listesini"), "release": A("Almanlar onları"), "meg": A("Meğerse"), "toll": A("Adadan"),
    "yad": A("1989'da"), "end": A("Bir konsolos"), "sources": VOICE_END,
}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}


def win(k):
    a, b = S[k]
    return a, round((b + FADE if b < TOTAL else b) - a, 2)


def scene(k, inner):
    a, d = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{d}" data-track-index="1"><div class="fill" id="{k}-in">{inner}</div></div>'


def svg(inner, idn="", style=""):
    i = f' id="{idn}"' if idn else ""
    return f'<svg class="fill"{i} viewBox="0 0 960 1080" style="overflow:visible;{style}">{inner}</svg>'


# ---------------- karakterler ----------------
ULK = dict(outfit="suit", jacket="#252B38", hair_style="quiff", hair="#1E1612", skin="#E2B48C", tie="#7A1E22")
KLE = dict(outfit="uniform", jacket="#646A55", hat="officer", hair_style="short", hair="#B8A27A", skin="#EFC9A8")
CIV = [dict(outfit="suit", jacket="#4A3E34", hat="fedora", prop="suitcase"),
       dict(outfit="dress", female=True, shirt="#5A6E8A", shoes="#5A2A1A", skin="#E9C2A0", hair="#3A2418", prop="suitcase"),
       dict(outfit="suit", jacket="#3A4048", hair_style="balding", hair="#8A8480", prop="suitcase"),
       dict(outfit="dress", female=True, shirt="#7A4A3A", hair_style="bob", hair="#2A1A12", shoes="#3A2418", prop="suitcase"),
       dict(outfit="suit", jacket="#2E3A30", hair_style="short", hair="#3A2A1E", prop="suitcase"),
       dict(outfit="dress", female=True, shirt="#4A5A3E", hair="#6A4A2E", shoes="#2A1A12", skin="#F0C8A6", prop="suitcase")]


# ---------------- ortak çizimler ----------------
def flag(x, y, s=1.0):
    """Türk bayrağı direkte (dalgalı)."""
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-3" y="0" width="6" height="260" fill="#D9D2C2" stroke="#1B1414" stroke-width="2"/>'
            f'<circle cx="0" cy="-4" r="6" fill="#D9B14A" stroke="#1B1414" stroke-width="2"/>'
            f'<g id="flagw"><path d="M3 6 C40 -4 70 16 110 6 C130 2 145 6 150 8 L150 92 C140 88 125 86 110 90 C70 100 40 80 3 90 Z" fill="#E30A17" stroke="#1B1414" stroke-width="2.5"/>'
            f'<circle cx="58" cy="48" r="22" fill="#fff"/><circle cx="64" cy="48" r="17.6" fill="#E30A17"/>'
            f'<path d="M84 48 L97.5 43.6 L89.2 55.1 L89.2 40.9 L97.5 52.4 Z" fill="#fff"/>'
            f'<path d="M3 30 C40 22 70 40 110 30" stroke="#000" stroke-opacity=".15" stroke-width="10" fill="none"/></g></g>')


def windmill(i=0):
    """Mandraki yel değirmeni, taban (0,0), 520 birim."""
    sails = "".join(f'<g transform="rotate({a})"><path d="M0 0 L-8 -190 L22 -190 L10 0 Z" fill="#F2EBDD" stroke="#1B1414" stroke-width="5"/>'
                    f'<path d="M-4 -40 H14 M-6 -80 H16 M-7 -120 H19 M-8 -160 H21" stroke="#1B1414" stroke-width="2.5"/></g>' for a in range(0, 360, 45))
    return (cel("M-70 0 L-58 -360 L58 -360 L70 0 Z", "#E9DFC8", "#BFB399", -1, 26, 5)
            + cel("M-66 -350 L0 -440 L66 -350 Z", "#8A5A3A", "#5A3A22", -1, 14, 5)
            + '<rect x="-20" y="-110" width="40" height="110" fill="#5A3A22" stroke="#1B1414" stroke-width="5"/>'
            + f'<g class="sails" transform="translate(0 -360)">{sails}<circle r="14" fill="#5A3A22" stroke="#1B1414" stroke-width="5"/></g>')


def stone_wall(w=900, h=260):
    """Rodos sur duvarı + mazgal, taban (0,0)."""
    crenel = "".join(f'<rect x="{-w/2 + i*60}" y="{-h-40}" width="36" height="44" fill="#D9C9A4" stroke="#1B1414" stroke-width="4"/>' for i in range(int(w / 60)))
    blocks = "".join(f'<path d="M{-w/2} {-h + j*40} H{w/2}" stroke="#A8966E" stroke-width="3"/>' for j in range(1, int(h / 40)))
    return f'{crenel}{cel(f"M{-w/2} 0 L{-w/2} {-h} L{w/2} {-h} L{w/2} 0 Z", "#D9C9A4", "#B5A27C", -1, 40, 5)}{blocks}'


def consulate():
    """İki katlı taş konsolosluk binası, taban (0,0), 620 birim."""
    wins = "".join(f'<g transform="translate({x} {y})">' + cel("M-34 -70 L34 -70 L34 40 L-34 40 Z", "#3E5A6E", "#2A3E4E", -1, 8, 4)
                   + '<path d="M0 -70 V40 M-34 -15 H34" stroke="#F2EBDD" stroke-width="6"/><path d="M-42 44 H42" stroke="#1B1414" stroke-width="8"/></g>'
                   for x in (-200, -70, 70, 200) for y in (-420, -230))
    return (cel("M-300 0 L-300 -560 L300 -560 L300 0 Z", "#E2D4B4", "#BCAA86", -1, 40, 6)
            + cel("M-330 -560 L0 -640 L330 -560 Z", "#A8553A", "#7A3A26", -1, 30, 6)
            + '<rect x="-300" y="-330" width="600" height="14" fill="#C8B892" stroke="#1B1414" stroke-width="4"/>' + wins
            + cel("M-60 0 L-60 -150 Q0 -200 60 -150 L60 0 Z", "#5A3A22", "#3A2414", -1, 10, 5)
            + '<rect x="-120" y="-200" width="240" height="40" rx="6" fill="#F2EBDD" stroke="#1B1414" stroke-width="4"/>'
            + '<text x="0" y="-172" text-anchor="middle" font-family="Mont" font-weight="800" font-size="24" fill="#1B1414">TÜRKİYE BAŞKONSOLOSLUĞU</text>')


def plane(s=1.0):
    return (f'<g transform="scale({s})"><path d="M-120 0 C-80 -14 60 -16 120 -4 C130 0 130 6 120 8 C60 14 -80 12 -120 6 Z" fill="#3A3E44" stroke="#1B1414" stroke-width="4"/>'
            f'<path d="M-20 -6 L-70 -80 L-40 -80 L30 -6 Z M-20 8 L-60 70 L-34 70 L30 8 Z M-100 -2 L-128 -40 L-112 -40 L-84 -2 Z" fill="#2E3238" stroke="#1B1414" stroke-width="4"/>'
            f'<circle cx="96" cy="-2" r="7" fill="#9AB6C8" stroke="#1B1414" stroke-width="3"/></g>')


def office_bg():
    """1944 makam odası: duvar, pencere (anahtar ışık soldan), dosya dolabı, harita."""
    return (f'<rect width="960" height="1080" fill="#B9A988"/><rect width="960" height="1080" fill="url(#wallpaper)" opacity=".35"/>'
            f'<rect y="0" width="960" height="1080" fill="#2A1A10" opacity=".25"/>'
            + cel("M60 140 L330 140 L330 560 L60 560 Z", "#F7E9C4", "#E2CFA0", -1, 6, 6)
            + '<path d="M195 140 V560 M60 350 H330" stroke="#5A3A22" stroke-width="12"/>'
            + cel("M560 180 L860 180 L860 420 L560 420 Z", "#D9CDB0", "#B8AA8A", -1, 10, 5)
            + '<path d="M600 230 Q680 260 700 330 T820 380 M620 330 L700 300 L780 340" stroke="#8A6A4A" stroke-width="5" fill="none"/><circle cx="740" cy="300" r="10" fill="#B23A2E"/>'
            + cel("M640 520 L860 520 L860 840 L640 840 Z", "#6A6A5E", "#4A4A40", -1, 14, 5)
            + "".join(f'<path d="M650 {y} H850" stroke="#1B1414" stroke-width="4"/><rect x="730" y="{y+30}" width="40" height="10" rx="3" fill="#B9B4A8" stroke="#1B1414" stroke-width="2"/>' for y in (600, 680, 760))
            + '<rect y="820" width="960" height="260" fill="#5A3A22"/><path d="M0 820 H960" stroke="#1B1414" stroke-width="6"/>')


def desk():
    return (cel("M-260 0 L-260 -150 L260 -150 L260 0 Z", "#6A4024", "#4A2A14", -1, 20, 6)
            + cel("M-290 -150 L290 -150 L280 -175 L-280 -175 Z", "#8A5A34", "#6A4024", -1, 6, 6)
            + cel("M-60 -175 L60 -175 L56 -180 L-56 -180 Z", "#F7F2E2", "#D9D0B8", -1, 2, 3)
            + '<rect x="120" y="-215" width="20" height="40" fill="#2A2420" stroke="#1B1414" stroke-width="3"/><path d="M130 -215 L170 -250" stroke="#1B1414" stroke-width="6"/>'
            + cel("M150 -255 L210 -245 L200 -232 L146 -244 Z", "#2A2420", "#121010", -1, 4, 3))


# ---------------- sahneler ----------------
cam = Cam(horizon=470, vpx=480, f=900, eye=160, sun=(-1, -.6), alt=40, haze="#E9D9B8")
DEFS = DEFS2.replace("</defs>", "") + DEFS_P + depth_defs(cam) + "</defs>"
JS = []

# 1) kanca: makam odası, Ülkümen listeyi uzatıyor, komutan karşısında
sc1 = Scene(cam, "hk", ground=("#4A2E1A", "#6A4630"), sky=False)
sc1.add_toon(-80, 430, look_at=(90, 450), h=176, **ULK, pose="offer", prop="paper", expr=dict(lid=.3, smile=-.2, brow=-.2))
sc1.add_toon(90, 450, look_at=(-80, 430), h=180, **KLE, expr=dict(lid=.4, smile=-.5, brow=-.7))
hook = (svg(office_bg(), "hkbg") + sc1.svg()
        + svg(light_shafts(40, 120, angle=-30, n=4, length=1100, spread=70, op=.35) + chiaroscuro(480, 520, 760, .62))
        + '<div class="chip red">GERÇEK OLAY · RODOS 1944</div>')
JS.append(sc1.js() + sc1.camera_js(0, win("hook")[1], dx=0, dz=90, dy=-6, ease="power1.inOut"))

# 2) Rodos limanı: deniz, yel değirmenleri (eşit aralık → sıkışma), sur
cam2 = Cam(horizon=430, vpx=420, f=900, eye=260, sun=(-1, -.6), alt=40, haze="#E9D9B8")
sc2 = Scene(cam2, "is", ground=("#2E6E8E", "#8CB8C8"))
sc2.add_ground([(120, 200), (2000, 200), (2000, 12000), (120, 12000)], 'fill="#C9B48A"')          # rıhtım
sc2.row(700, 2600, 800, 3, lambda i: windmill(i), 520, 900, w=200)
sc2.add(1500, 7000, stone_wall(2200, 300), 340, 1400, w=2000, shadow=False)
sc2.add(-900, 9000, stone_wall(3000, 260), 300, 1100, w=2000, shadow=False)
for i, c in enumerate(CIV[:2]):
    sc2.add_toon(260 + i * 120, 1200 + i * 200, look_at=(900, 2400), h=172, **{**c, "prop": None})
island = (sc2.svg()
          + '<div class="datecard" id="isdate"><b>1944</b><span>RODOS ADASI</span></div><div class="chip" id="ischip">ALMAN İŞGALİNDE</div>')
JS.append(sc2.js() + sc2.camera_js(win("island")[0], win("island")[1], dx=260, dz=200, ease="sine.inOut"))

# 3) konsolosluk + Ülkümen
cam3 = Cam(horizon=520, vpx=480, f=900, eye=160, sun=(-1, -.6), alt=40, haze="#E9D9B8")
sc3 = Scene(cam3, "cs", ground=("#B5A27C", "#D9C9A4"))
sc3.add(0, 2600, consulate(), 640, 1500, w=1300, shadow=False)
sc3.add(-430, 2400, flag(0, -560, 1.0) + '<rect x="-3" y="-300" width="6" height="300" fill="#D9D2C2"/>', 560, 900, w=40, shadow=False)
sc3.add(-1200, 2000, tree_simple(2), 700, 700, w=140)
sc3.add_toon(-40, 760, look_at=(0, 0), h=176, **ULK, pose="stand", expr=dict(lid=.3, smile=.25))
consul = sc3.svg() + '<div class="namecard" id="ncard"><b>SELAHATTİN ÜLKÜMEN</b><span>Türkiye'"'"'nin Rodos Başkonsolosu · 30 yaşında</span></div>'
JS.append(sc3.js() + sc3.camera_js(win("consul")[0], win("consul")[1], dx=-60, dz=220))

# 4) bombalama: aynı bina, uçaklar, patlama, duman
bomb = (svg(f'<rect width="960" height="1080" fill="#8A9AA8"/><rect y="520" width="960" height="560" fill="#9A8A6A"/>'
            f'<g transform="translate(480 900) scale(.75)"><g id="bbld">{consulate()}</g></g>'
            f'<g id="bflash" opacity="0"><circle cx="600" cy="520" r="260" fill="url(#fire2)"/></g>'
            f'<g id="bsmoke" opacity="0">' + "".join(f'<circle cx="{560+(i*53)%160}" cy="{460-(i*37)%220}" r="{70+(i*29)%60}" fill="#3A3634" opacity=".85"/>' for i in range(10)) + '</g>'
            + "".join(f'<g transform="translate(-300 {150+i*90})"><g class="pl" id="pl{i}">{plane(.7 - i*.12)}</g></g>' for i in range(3)))
        + '<div class="datecard" id="bdate"><b>18 ŞUBAT 1944</b><span>KONSOLOSLUK BOMBALANDI</span></div>'
        + '<div class="tagcard" id="btag">2 çalışan öldü · eşi ağır yaralandı</div><div class="chip" id="bchip">ANILARINA GÖRE: ALMAN UÇAKLARI</div>')

# 5) toplama: sokak, valizli insanlar uzağa (limana) yürüyor, nöbetçi
cam5 = Cam(horizon=440, vpx=560, f=900, eye=170, sun=(1, -.4), alt=24, haze="#E9C8A0")
sc5 = Scene(cam5, "ru", ground=("#7A6A54", "#C9B494"))
sc5.add_road(40, 900, 60, 12000, color="#9A8A70", line="#9A8A70")
sc5.row(-700, 900, 700, 8, lambda i: stone_wall(400, 520), 560, 700, w=300)
sc5.row(800, 1100, 700, 8, lambda i: stone_wall(400, 560), 600, 700, w=300)
for i in range(6):
    sc5.add_toon(-160 + (i % 3) * 140, 760 + i * 300, look_at=(-160 + (i % 3) * 140 + 60, 6000), h=170, **CIV[i], pose="walk")
sc5.add_toon(420, 1000, look_at=(0, 1600), h=180, **{**KLE, "hat": "officer"}, expr=dict(lid=.5, smile=-.4, brow=-.5))
roundup = (sc5.svg() + svg(chiaroscuro(560, 420, 900, .45))
           + '<div class="datecard" id="rdate"><b>19 TEMMUZ 1944</b><span>GESTAPO TOPLUYOR</span></div>'
           + '<div class="bubble" id="rlie" style="top:200px">"Yakındaki bir adaya götürülüyorsunuz."</div>')
JS.append(sc5.js() + sc5.camera_js(win("roundup")[0], win("roundup")[1], dz=500, ease="sine.inOut"))

# 6) gerçek varış: rota
pins = [("RODOS", 330, 900), ("PİRE (ATİNA)", 230, 640), ("AUŞVİÇ", 520, 170)]
dest = svg('<rect width="960" height="1080" fill="#14181E"/>'
           + "".join(f'<path d="M0 {y} H960" stroke="#1E2430" stroke-width="2"/>' for y in range(60, 1080, 80)) + "".join(f'<path d="M{x} 0 V1080" stroke="#1E2430" stroke-width="2"/>' for x in range(40, 960, 80))
           + '<path id="route" d="M330 900 C260 820 220 740 230 640 C260 480 430 320 520 170" fill="none" stroke="#E8524A" stroke-width="10" stroke-dasharray="26 18" pathLength="1"/>'
           + "".join(f'<g class="pin" id="pin{i}" transform="translate({x} {y})"><circle r="18" fill="{"#E8524A" if i == 2 else "#F4F1EA"}" stroke="#1B1414" stroke-width="5"/>'
                     f'<text x="34" y="12" font-family="Mont" font-weight="800" font-size="{54 if i == 2 else 40}" fill="{"#E8524A" if i == 2 else "#F4F1EA"}">{n}</text></g>' for i, (n, x, y) in enumerate(pins))
           + '<text x="480" y="1020" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#8A96A8">deniz yoluyla Pire, oradan trenle</text>')

# 7) yüzleşme: omuz üstü — komutan ön planda (bulanık), Ülkümen ona dönük
conf = (svg(office_bg(), "cfbg", "filter:blur(4px)")
        + svg(f'<g transform="translate(320 1230) scale(4.4)">{toon_figure(**ULK, pose="talk", look=(1, -.15), expr=dict(lid=.25, smile=-.1, brow=-.3, talk=.5))}</g>', "cfu")
        + svg(f'<g transform="translate(700 1600) scale(6.2)" style="filter:blur(6px)">{toon_figure(**KLE, flip=True, expr=dict(lid=.5, smile=-.5))}</g>', "cfk")
        + svg(chiaroscuro(400, 480, 760, .55))
        + '<div class="bubble left" id="cfq">"Aralarında Türk vatandaşları var.<br><b>Onları bırakın.</b>"</div>')

# 8) komutan: yakın, sert
cmd = (svg('<rect width="960" height="1080" fill="#3A3A30"/>' + f'<g style="filter:blur(3px)">{office_bg()}</g>', "cmbg")
       + svg(f'<g transform="translate(560 1500) scale(6.4)">{toon_figure(**KLE, flip=True, look=(1, .05), expr=dict(lid=.55, smile=-.6, brow=-.8, talk=.45))}</g>', "cmk")
       + svg(chiaroscuro(560, 420, 640, .7))
       + '<div class="bubble right dark" id="cmq">"Bizim kanunumuza göre<br><b>Yahudi, Yahudidir.</b>"</div>')

# 9) cevap: Ülkümen yakın
reply = (svg('<rect width="960" height="1080" fill="#2A2E36"/>' + f'<g style="filter:blur(3px)">{office_bg()}</g>', "rpbg")
         + svg(f'<g transform="translate(400 1500) scale(6.4)">{toon_figure(**ULK, look=(1, -.05), expr=dict(lid=.2, smile=0, brow=.1, talk=.55))}</g>', "rpu")
         + svg(light_shafts(-40, 60, angle=-28, n=4, length=1100, spread=80, op=.4) + chiaroscuro(400, 420, 700, .55))
         + '<div class="bubble left" id="rpq1">"Bizim kanunumuzda Yahudi, Hristiyan, Müslüman ayrımı yok."</div>'
         + '<div class="bigquote" id="rpq2">HEPSİ EŞİT<br>VATANDAŞTIR.</div>')

# 10) liste: isimler yazılıyor
rows = "".join(f'<g class="lrow"><path d="M150 {200+i*30} H{430+((i*53)%300)}" stroke="#2A2420" stroke-width="5" stroke-linecap="round"/><text x="120" y="{208+i*30}" font-family="Mont" font-size="20" fill="#6A5A48" text-anchor="end">{i+1}</text></g>' for i in range(26))
lst = (svg('<rect width="960" height="1080" fill="#3A2A1C"/>'
           + f'<g id="paper" transform="translate(40 0)">' + cel("M60 120 L860 100 L880 1000 L80 1020 Z", "#F7F0DC", "#E2D6B4", -1, 14, 5)
           + '<text x="460" y="170" text-anchor="middle" font-family="Mont" font-weight="800" font-size="34" fill="#1B1414">TÜRK VATANDAŞLARI LİSTESİ</text>' + rows + '</g>')
       + '<div class="counter" id="lcount">≈ 50 İSİM</div>')

# 11) bırakılış: imza defteri
release = (svg('<rect width="960" height="1080" fill="#5A4632"/>'
               + cel("M120 300 L840 260 L860 900 L100 940 Z", "#EFE6CC", "#D2C6A4", -1, 14, 5)
               + "".join(f'<path class="sig" d="M200 {380+i*90} c30 -30 50 20 80 -6 s40 -30 70 4 s50 10 90 -16" stroke="#2A3A6A" stroke-width="5" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                         f'<text x="560" y="{388+i*90}" font-family="Mont" font-weight="600" font-size="28" fill="#5A4A38">{["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi"][i]}</text>' for i in range(6)))
           + '<div class="stamp" id="rstamp">HER GÜN<br>GESTAPO\'YA İMZA</div>')

# 12) meğerse: 50 isimden 13'ü
cells = "".join(f'<rect class="{"cz" if i < 13 else "cx"}" x="{110+(i%5)*150}" y="{110+(i//5)*56}" width="130" height="42" rx="10" fill="#E9E2D0" stroke="#1B1414" stroke-width="3"/>' for i in range(50))
meg = (svg('<rect width="960" height="1080" fill="#14181E"/>' + cells)
       + '<div class="megbig" id="m13">13 <span>/ 50</span></div>'
       + '<div class="legend" id="mleg"><i class="g"></i>gerçekten Türk vatandaşı<br><i class="o"></i>eş, akraba, süresi dolmuş kâğıt</div>')

# 13) bedel: 1.673 nokta → ~151
dots = "".join(f'<circle class="{"dl" if (i * 7919) % 1673 < 151 else "dd"}" cx="{58+(i%52)*16.5:.1f}" cy="{80+(i//52)*18:.1f}" r="6" fill="{"#F5B82E" if (i * 7919) % 1673 < 151 else "#F4F1EA"}"/>' for i in range(1673))
toll = (svg('<rect width="960" height="1080" fill="#0E1116"/>' + dots)
        + '<div class="tollnum" id="tn1">1.673 <span>götürüldü</span></div><div class="tollnum" id="tn2" style="opacity:0">≈ 151 <span>döndü</span></div>')

# 14) Yad Vaşem: ağaç ve plaket
cam14 = Cam(horizon=600, vpx=480, f=900, eye=150, sun=(-1, -.6), alt=48, haze="#E2DCC8")
sc14 = Scene(cam14, "yd", ground=("#8A7A50", "#C9BC8E"))
sc14.add(-60, 820, tree_simple(1), 700, 360, w=160)
sc14.add(160, 760, cel("M-60 0 L-60 -90 L60 -90 L60 0 Z", "#D9D2C2", "#B5AC98", -1, 10, 4)
         + '<text x="0" y="-58" text-anchor="middle" font-family="Mont" font-weight="800" font-size="13" fill="#1B1414">SELAHATTİN</text>'
         + '<text x="0" y="-40" text-anchor="middle" font-family="Mont" font-weight="800" font-size="13" fill="#1B1414">ÜLKÜMEN</text>'
         + '<text x="0" y="-20" text-anchor="middle" font-family="Mont" font-weight="600" font-size="11" fill="#3A3A3A">TÜRKİYE</text>', 90, 90, w=120)
sc14.row(-900, 1600, 500, 6, lambda i: tree_simple(i + 2), 700, 500, w=120)
yad = sc14.svg() + '<div class="datecard" id="ydate"><b>13 ARALIK 1989</b><span>YAD VAŞEM · ULUSLAR ARASINDA DÜRÜST İNSAN</span></div>'
JS.append(sc14.js() + sc14.camera_js(win("yad")[0], win("yad")[1], dz=260, dx=40))

# 15) kapanış: limanda gün batımı
cam15 = Cam(horizon=560, vpx=480, f=900, eye=170, sun=(1, 1), alt=12, haze="#F2B878")
sc15 = Scene(cam15, "en", ground=("#2A4A6A", "#E89A5A"), sky=False)
sc15.add_ground([(-2000, 120), (60, 120), (60, 1600), (-2000, 1600)], 'fill="#8A7254"')
sc15.add_toon(-160, 760, look_at=(800, 4000), h=176, **ULK, expr=dict(lid=.35, smile=.15), light_from_left=False)
sc15.row(-600, 3000, 1800, 2, lambda i: windmill(i), 520, 900, w=200)
end = (svg('<defs><linearGradient id="sunsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3A6A"/><stop offset=".6" stop-color="#E88A5A"/><stop offset="1" stop-color="#F7C88A"/></linearGradient></defs>'
           '<rect width="960" height="562" fill="url(#sunsky)"/><circle cx="720" cy="540" r="70" fill="#FFE2A0"/>')
       + sc15.svg().replace('<svg class="fill" id="en"', '<svg class="fill" id="en" style="overflow:visible"', 1)
       + '<div class="endq" id="eq">BİR KONSOLOS.<br>BİR LİSTE.<br><b>"HEPSİ EŞİT VATANDAŞTIR."</b></div>')
JS.append(sc15.js() + sc15.camera_js(win("end")[0], win("end")[1], dz=-200, dy=40))

sources = ('<div class="fill" style="background:#0B1220"></div><div class="srcbox"><b>KAYNAKLAR</b><br>'
           'Yad Vashem · Righteous Among the Nations (Ülkümen)<br>USHMM · Selahattin Ülkümen<br>Wikipedia · Selahattin Ülkümen<br>'
           'Univ. of Washington · Holocaust memory, Rhodes<br>Sayılar kaynağa göre değişir (≈150-151).</div>')

HTML = dict(hook=hook, island=island, consul=consul, bomb=bomb, roundup=roundup, dest=dest, confront=conf, cmd=cmd, reply=reply,
            list=lst, release=release, meg=meg, toll=toll, yad=yad, end=end, sources=sources)
scenes_html = "".join(scene(k, HTML[k]) for k in keys)

s = lambda k: S[k][0]
d = lambda k: win(k)[1]
js = "".join(f'tl.fromTo("#{k}-in",{{opacity:0}},{{opacity:1,duration:{FADE},ease:"power1.out"}},{s(k)});' for k in keys if k != "hook")
js += "".join(JS)
js += f"""
tl.fromTo("#hkbg",{{scale:1.04,x:10}},{{scale:1.1,x:-16,duration:{d('hook')},ease:"power1.inOut",transformOrigin:"50% 45%"}},0);
tl.fromTo("#isdate",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('island')+.2});
tl.fromTo("#ischip",{{opacity:0}},{{opacity:1,duration:.3}},{A('Alman işgalinde')});
tl.to("#s-island .sails",{{rotation:"+=70",duration:{d('island')},ease:"none"}},{s('island')});
tl.fromTo("#ncard",{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"power3.out"}},{A('Selahattin')});
tl.fromTo("#flagw",{{skewY:0}},{{skewY:3,duration:.6,yoyo:true,repeat:{int(d('consul')/.6)},ease:"sine.inOut",transformOrigin:"0% 50%"}},{s('consul')});
tl.fromTo("#bdate",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('bomb')+.1});
tl.fromTo(".pl",{{x:0}},{{x:1600,duration:2.2,stagger:.25,ease:"none"}},{s('bomb')+.2});
tl.set("#bflash",{{opacity:1}},{A('bombalanıyor')+.2});tl.to("#bflash",{{opacity:0,duration:.8}},{A('bombalanıyor')+.3});
tl.to("#bsmoke",{{opacity:1,duration:.6}},{A('bombalanıyor')+.3});tl.fromTo("#bsmoke",{{y:0,scale:.8,transformOrigin:"60% 60%"}},{{y:-60,scale:1.2,duration:5,ease:"power1.out"}},{A('bombalanıyor')+.3});
tl.fromTo("#bbld",{{x:0}},{{x:10,duration:.05,repeat:9,yoyo:true}},{A('bombalanıyor')+.2});
tl.fromTo("#btag",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.4}},{A('İki çalışanı')});
tl.fromTo("#bchip",{{opacity:0}},{{opacity:1,duration:.3}},{A('Anılarına')});
tl.fromTo("#rdate",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('roundup')+.2});
tl.fromTo("#rlie",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Yakındaki')});
tl.fromTo("#route",{{attr:{{"stroke-dashoffset":1,"stroke-dasharray":"0 1"}}}},{{attr:{{"stroke-dashoffset":0,"stroke-dasharray":"1 0"}},duration:2.4,ease:"power1.inOut"}},{s('dest')+.2});
tl.fromTo("#pin0",{{scale:0,transformOrigin:"0 0"}},{{scale:1,duration:.3,ease:"back.out(2)"}},{s('dest')+.1});
tl.fromTo("#pin1",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},{s('dest')+1.1});
tl.fromTo("#pin2",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},{A('Auşviç',s('dest'))});
tl.fromTo("#cfbg",{{scale:1.05}},{{scale:1.12,duration:{d('confront')}}},{s('confront')});
tl.fromTo("#cfu",{{x:-20,scale:1}},{{x:10,scale:1.05,duration:{d('confront')},ease:"sine.inOut",transformOrigin:"35% 60%"}},{s('confront')});
tl.fromTo("#cfk",{{x:60}},{{x:-30,duration:{d('confront')},ease:"sine.inOut"}},{s('confront')});
tl.fromTo("#cfq",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Aralarında')});
tl.fromTo("#cmk",{{scale:1.08,transformOrigin:"58% 30%"}},{{scale:1.0,duration:{d('cmd')},ease:"power2.out"}},{s('cmd')});
tl.fromTo("#cmq",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Bizim kanunumuza')});
tl.fromTo("#rpu",{{scale:1.0,transformOrigin:"40% 30%"}},{{scale:1.08,duration:{d('reply')},ease:"sine.inOut"}},{s('reply')});
tl.fromTo("#rpq1",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Bizim kanunumuzda')});
tl.to("#rpq1",{{opacity:0,duration:.3}},{A('Hepsi eşit')-.2});
tl.fromTo("#rpq2",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"power3.out"}},{A('Hepsi eşit')});
tl.fromTo(".lrow",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.2,stagger:.09}},{s('list')+.1});
tl.fromTo("#paper",{{rotation:-3,transformOrigin:"50% 50%"}},{{rotation:1,duration:{d('list')}}},{s('list')});
tl.fromTo("#lcount",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},{A('Yaklaşık elli')});
tl.to(".sig",{{attr:{{"stroke-dashoffset":0}},duration:.35,stagger:.4}},{s('release')+.3});
tl.fromTo("#rstamp",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.in"}},{A('imza')});
tl.fromTo("#m13",{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},{A('on üçü')});
tl.to(".cz",{{attr:{{fill:"#4CAF6A"}},duration:.2,stagger:.04}},{A('on üçü')});
tl.to(".cx",{{attr:{{fill:"#F0A040"}},duration:.15,stagger:.02}},{A('Gerisini')});
tl.fromTo("#mleg",{{opacity:0}},{{opacity:1,duration:.4}},{A('Gerisini')});
tl.fromTo("#tn1",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.4}},{s('toll')+.2});
tl.to(".dd",{{opacity:.08,duration:1.6,ease:"power2.in"}},{A('yüz elli')});
tl.to("#tn1",{{opacity:0,duration:.3}},{A('yüz elli')});
tl.to("#tn2",{{opacity:1,duration:.4}},{A('yüz elli')+.2});
tl.fromTo("#ydate",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('yad')+.2});
tl.fromTo("#eq",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.6}},{s('end')+.3});
"""

css = """
.datecard { position:absolute; left:40px; top:40px; padding:20px 28px; border-radius:22px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA; }
.datecard b { display:block; font-weight:800; font-size:58px; color:#F5B82E; }
.datecard span { display:block; font-weight:600; font-size:28px; color:#C9D6E4; margin-top:6px; max-width:700px; }
.namecard { position:absolute; left:40px; bottom:40px; padding:18px 26px; border-radius:20px; background:#F4F1EA; color:#0B1220; box-shadow:0 8px 0 #E30A17; }
.namecard b { display:block; font-weight:800; font-size:44px; } .namecard span { font-weight:600; font-size:26px; }
.tagcard { position:absolute; right:40px; top:240px; padding:16px 22px; border-radius:16px; background:#E8524A; color:#fff; font-weight:800; font-size:32px; }
.bubble { position:absolute; left:60px; right:60px; top:60px; padding:26px 32px; border-radius:30px; background:#F4F1EA; color:#0B1220; border:5px solid #1B1414; font-weight:800; font-size:42px; line-height:1.18; }
.bubble b { color:#B2241E; } .bubble.dark { background:#2A2C24; color:#F4F1EA; } .bubble.dark b { color:#F5B82E; }
.bigquote { position:absolute; left:0; right:0; top:90px; text-align:center; font-weight:800; font-size:92px; line-height:1.02; color:#F5B82E; text-shadow:0 6px 0 #1B1414; }
.counter { position:absolute; right:60px; bottom:60px; padding:16px 26px; border-radius:20px; background:#E8524A; color:#fff; font-weight:800; font-size:56px; }
.stamp { position:absolute; left:200px; top:420px; padding:20px 30px; border:8px solid #B2241E; border-radius:16px; color:#B2241E; background:rgba(244,241,234,.9); font-weight:800; font-size:54px; text-align:center; transform:rotate(-10deg); }
.megbig { position:absolute; left:0; right:0; bottom:120px; text-align:center; font-weight:800; font-size:180px; color:#4CAF6A; line-height:1; }
.megbig span { font-size:90px; color:#F4F1EA; }
.legend { position:absolute; left:110px; bottom:40px; font-weight:600; font-size:30px; line-height:1.5; color:#F4F1EA; }
.legend i { display:inline-block; width:26px; height:26px; border-radius:6px; margin-right:12px; vertical-align:-4px; } .legend .g { background:#4CAF6A; } .legend .o { background:#F0A040; }
.tollnum { position:absolute; left:0; right:0; bottom:60px; text-align:center; font-weight:800; font-size:140px; color:#F4F1EA; text-shadow:0 6px 18px #000; }
.tollnum span { display:block; font-size:44px; color:#E8524A; }
.endq { position:absolute; left:40px; right:40px; top:60px; text-align:center; font-weight:800; font-size:58px; line-height:1.15; color:#F4F1EA; text-shadow:0 4px 0 #1B1414; }
.endq b { color:#F5B82E; }
.srcbox { position:absolute; left:60px; right:60px; top:200px; font-weight:600; font-size:34px; line-height:1.6; color:#C9D6E4; }
.srcbox b { color:#F5B82E; font-size:44px; }
"""
html = page(words, mouth, scenes_html, js, total=TOTAL, voice_end=VOICE_END, kicker="MEĞERSE DOSYASI <b>|</b> VAKA 05 · RODOS",
            title="ELLİ İSİMLİK LİSTE", voice_src="assets/ulkumen/voice.mp3", extra_css=css, glow="#2A1A14", fx=True, defs=DEFS)
(HF / "index.html").write_text(html, encoding="utf-8")
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
