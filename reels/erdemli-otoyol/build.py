"""Çeşmeli-Kızkalesi (Erdemli) otoyolu reel'i: hf/index.html üretir.

python3 reels/erdemli-otoyol/build.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/erdemli-v1.mp4)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, Scene, defs as depth_defs, tree_simple  # noqa: E402
from portrait import DEFS_P, chiaroscuro  # noqa: E402
from reelkit import HF, anchor, page  # noqa: E402
from toon import cel, line, toon_figure  # noqa: E402
from toonprops import CAR_H, car_rear, heat_shimmer, toll_booth, tunnel_portal, viaduct  # noqa: E402

words = json.loads((ROOT / "reels/erdemli-otoyol/words.json").read_text(encoding="utf-8"))
mouth = json.loads((HF / "avatar/mouth-erdemli.json").read_text())
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.6, 2)
TOTAL = round(VOICE_END + 4, 2)
FADE = 0.4
A = lambda p, after=0.0: anchor(words, p, after)

T = {"hook": 0.0, "d400": A("D400."), "slow": A("Yetkililere"), "open": A("19 Ekim"), "stats": A("Elli iki"),
     "target": A("Hedef:"), "first": A("İlk gün"), "q": A("Peki"), "meg": A("Meğerse"), "cost": A("Proje ikiye"),
     "eight": A("İlk ihaleden"), "end": A("Şimdi soru"), "sources": VOICE_END}
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


CARS = ["#C8402F", "#E9E4DA", "#2E5A9A", "#3A3A3A", "#B9B4A8", "#7A1E22", "#2E6A4A", "#D9A03A", "#5A6E8A"]
DRV = dict(outfit="tee", shirt="#2E6A9A", sleeve="#2E6A9A", hair_style="fade", hair="#1E1612", skin="#C98B63", shorts=False, pants="#3A4048")
JS = []


def road_sign(text_top, text_bot, col="#2A5AB0"):
    """Yol tabelası, taban (0,0), 520 birim."""
    return (f'<rect x="-10" y="-520" width="20" height="520" fill="#9A9A9A" stroke="#1B1414" stroke-width="5"/>'
            + cel("M-200 -520 L200 -520 L200 -330 L-200 -330 Z", col, "#1A3A80", -1, 10, 6)
            + f'<rect x="-186" y="-506" width="372" height="162" rx="10" fill="none" stroke="#fff" stroke-width="6"/>'
            + f'<text x="0" y="-450" text-anchor="middle" font-family="Mont" font-weight="800" font-size="58" fill="#fff">{text_top}</text>'
            + f'<text x="0" y="-372" text-anchor="middle" font-family="Mont" font-weight="800" font-size="46" fill="#fff">{text_bot}</text>')


def jam_scene(sid, sun_hot=True):
    cam = Cam(horizon=430, vpx=470, f=900, eye=150, sun=(-.6, -1), alt=58, haze="#F2DDB0")
    sc = Scene(cam, sid, ground=("#B8A472", "#E2D2A2"))
    sc.add_road(-60, 820, 60, 14000, color="#5E5B57", line="#F2EBDD")
    sc.add_ground([(400, 60), (3000, 60), (3000, 14000), (400, 14000)], 'fill="#3E86A8"')       # deniz (sağda)
    sc.add_ground([(340, 60), (400, 60), (400, 14000), (340, 14000)], 'fill="#E2D2A2"')
    for i in range(18):
        for j, lx in enumerate((-250, 130)):
            z = 380 + i * 520 + j * 160
            sc.add(lx, z, car_rear(CARS[(i * 2 + j) % len(CARS)], brake=(i + j) % 3 != 1, seed=i + j), CAR_H, 150, w=190)
    sc.row(-900, 900, 900, 12, lambda i: tree_simple(i), 700, 650, w=140)
    sc.add(-470, 1700, road_sign("D-400", "ERDEMLİ  →"), 520, 520, w=60)
    return cam, sc


# 1) kanca: yaz kuyruğu
cam1, sc1 = jam_scene("hk")
hook = (svg('<circle cx="760" cy="150" r="70" fill="#FFF0B0"/><circle cx="760" cy="150" r="120" fill="#FFE080" opacity=".35" filter="url(#glow)"/>', "hksun")
        + sc1.svg() + svg(heat_shimmer(560) + heat_shimmer(720))
        + '<div class="chip red">MERSİN · ERDEMLİ YOLU</div>')
JS.append(sc1.js() + sc1.camera_js(0, win("hook")[1], dz=260, ease="none"))

# 2) D400: aynı kuyruk, kamera kuyruk boyunca ilerler
cam2, sc2 = jam_scene("dq")
d400 = (sc2.svg() + svg(heat_shimmer(600))
        + '<div class="datecard" id="dcard"><b>D-400</b><span>tatil trafiği · kilometrelerce kuyruk</span></div>')
JS.append(sc2.js() + sc2.camera_js(win("d400")[0], win("d400")[1], dz=700, dx=-40, ease="sine.inOut"))

# 3) 2,5 saate kadar: saat + mini rota
ticks = "".join(f'<rect x="-5" y="-250" width="10" height="34" rx="3" fill="#1B1414" transform="rotate({a})"/>' for a in range(0, 360, 30))
slow = svg('<rect width="960" height="1080" fill="#F2E6C8"/>'
           + f'<g transform="translate(480 600) scale(.85)">' + cel("M-280 0 A280 280 0 1 0 280 0 A280 280 0 1 0 -280 0 Z", "#F7F2E6", "#D9CFB8", -1, 16, 10) + ticks
           + '<path id="slowarc" d="M0 -230 A230 230 0 1 1 -199 115" fill="none" stroke="#E8524A" stroke-width="28" opacity=".35" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
           + '<g id="hhand"><rect x="-9" y="-150" width="18" height="160" rx="8" fill="#1B1414"/></g><g id="mhand"><rect x="-6" y="-215" width="12" height="225" rx="6" fill="#1B1414"/></g><circle r="18" fill="#E8524A" stroke="#1B1414" stroke-width="5"/></g>'
           + '<text x="480" y="960" text-anchor="middle" font-family="Mont" font-weight="800" font-size="40" fill="#1B1414">MERSİN → KIZKALESİ</text>') \
    + '<div class="bignum" id="snum">2,5 SAAT<span>yazın, D-400\'de (yetkililere göre)</span></div>'

# 4) 19 Ekim gecesi: gişeler açılıyor
cam4 = Cam(horizon=470, vpx=480, f=900, eye=160, sun=(-.2, -1), alt=70, haze="#1A2440")
sc4 = Scene(cam4, "op", ground=("#1E2228", "#2A3040"))
sc4.add_road(0, 2600, 60, 14000, color="#2E3036", line="#F2EBDD")
sc4.add(0, 2400, toll_booth(6), 620, 620, w=2400, shadow=False)
for i in range(6):
    sc4.add(-650 + (i % 3) * 650, 900 + i * 380, car_rear(CARS[i], brake=True, seed=i), CAR_H, 150, w=190)
opn = (svg('<rect width="960" height="472" fill="#0E1426"/>' + "".join(f'<circle cx="{(i*137)%960}" cy="{(i*71)%400}" r="{1+(i%3)*.6}" fill="#fff" opacity=".7"/>' for i in range(60)))
       + sc4.svg().replace('<svg class="fill" id="op"', '<svg class="fill" id="op" style="overflow:visible"', 1)
       + '<div class="datecard" id="ocard"><b>19 EKİM 2026</b><span>saat 00.01 · Çeşmeli-Kızkalesi otoyolu açıldı</span></div>')
JS.append(sc4.js() + sc4.camera_js(win("open")[0], win("open")[1], dz=1500, ease="power1.in"))

# 5) sayılar: otoyolda tünele doğru
cam5 = Cam(horizon=460, vpx=480, f=900, eye=200, sun=(-.6, -1), alt=50, haze="#D9E6EE")
sc5 = Scene(cam5, "st", ground=("#6A8A4A", "#A8BC88"))
sc5.add_road(-330, 1100, 60, 9600, color="#4A4A4E", line="#F2EBDD")
sc5.add_road(330, 1100, 60, 9600, color="#4A4A4E", line="#F2EBDD")
sc5.add(0, 9800, tunnel_portal(1400, 900), 900 * 2, 2600, w=3000, shadow=False)
sc5.add(-330, 2600, car_rear("#2E5A9A", seed=1), CAR_H, 150, w=190)
sc5.add(330, 4600, car_rear("#E9E4DA", seed=2), CAR_H, 150, w=190)
sc5.row(-1300, 900, 900, 9, lambda i: tree_simple(i), 700, 700, w=140)
sc5.row(1300, 1300, 900, 9, lambda i: tree_simple(i + 3), 700, 700, w=140)
stats = (sc5.svg()
         + '<div class="stat" id="st1" style="top:40px">52 <i>KM</i></div><div class="stat" id="st2" style="top:170px">7 <i>TÜNEL</i></div>'
         + '<div class="stat" id="st3" style="top:300px">5 <i>VİYADÜK</i></div><div class="stat" id="st4" style="top:430px">10 <i>KÖPRÜLÜ KAVŞAK</i></div>')
JS.append(sc5.js() + sc5.camera_js(win("stats")[0], win("stats")[1], dz=2600, ease="power1.inOut"))

# 6) hedef: 2,5 saat → 18 dk
target = svg('<rect width="960" height="1080" fill="#14181E"/>'
             + '<text x="90" y="300" font-family="Mont" font-weight="800" font-size="40" fill="#C9D6E4">ESKİ YOL · YAZIN</text>'
             + '<rect x="90" y="330" width="780" height="110" rx="20" fill="#2A2E36"/><rect id="barold" x="90" y="330" width="780" height="110" rx="20" fill="#E8524A"/>'
             + '<text x="840" y="405" text-anchor="end" font-family="Mont" font-weight="800" font-size="56" fill="#fff">2,5 SAAT</text>'
             + '<text x="90" y="600" font-family="Mont" font-weight="800" font-size="40" fill="#C9D6E4">OTOYOL · HEDEF</text>'
             + '<rect x="90" y="630" width="780" height="110" rx="20" fill="#2A2E36"/><rect id="barnew" x="90" y="630" width="94" height="110" rx="20" fill="#4CAF6A"/>'
             + '<text id="t18" x="210" y="705" font-family="Mont" font-weight="800" font-size="56" fill="#4CAF6A">18 DK</text>'
             + '<text x="480" y="880" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#8A96A8">Mersin merkez → Kızkalesi</text>')

# 7) ilk gün: sayaç + sürücü
first = (svg('<rect width="960" height="1080" fill="#E9F0F4"/><rect y="760" width="960" height="320" fill="#4A4A4E"/>'
             + f'<g id="drv" transform="translate(300 1520) scale(6.4)">{toon_figure(**DRV, pose="talk", look=(1, -.1), expr=dict(lid=.2, smile=.9, talk=.5, brow=.4))}</g>')
         + '<div class="counter" id="fc"><b id="fcn">0</b><span>araç · ilk gün</span></div>'
         + '<div class="bubble right" id="fq">Çeşmeli\'den Erdemli\'ye<br><b>8 dakika!</b></div>')

# 8) soru
q = svg('<rect width="960" height="1080" fill="#F2E6C8"/>'
        + "".join(f'<g transform="translate({330+i*40} {330+i*34})"><g class="cal">' + cel("M-160 -180 L160 -180 L160 200 L-160 200 Z", "#F7F2E6", "#D9CFB8", -1, 10, 6)
                  + cel("M-160 -180 L160 -180 L160 -100 L-160 -100 Z", "#E8524A", "#B2241E", -1, 6, 6)
                  + f'<text x="0" y="90" text-anchor="middle" font-family="Mont" font-weight="800" font-size="130" fill="#1B1414">{y}</text></g></g>' for i, y in enumerate(["2018", "2021", "2022", "2026"]))) \
    + '<div class="bigq" id="qq">NE ZAMANDIR<br>BEKLENİYORDU?</div>'

# 9) meğerse: 2018 ihalesi, boş teklif kutusu, görevli kutuya bakıyor
cam9 = Cam(horizon=520, vpx=480, f=900, eye=150, sun=(-1, -.5), alt=40, haze="#C8B898")
sc9 = Scene(cam9, "mg", ground=("#6A4A30", "#8A6A48"), sky=False)
box = (cel("M-120 0 L-120 -160 L120 -160 L120 0 Z", "#B8864A", "#8A5A2A", -1, 14, 5) + cel("M-130 -160 L130 -160 L120 -190 L-120 -190 Z", "#C8965A", "#9A6A3A", -1, 6, 5)
       + '<rect x="-60" y="-184" width="120" height="14" rx="4" fill="#1B1414"/><text x="0" y="-70" text-anchor="middle" font-family="Mont" font-weight="800" font-size="40" fill="#1B1414">TEKLİF</text>')
sc9.add(110, 440, box, 200, 70, w=110)
sc9.add_toon(-110, 480, look_at=(110, 440), h=176, outfit="suit", jacket="#3A4048", hair_style="balding", hair="#8A8480", pose="hands_pockets", expr=dict(lid=.5, smile=-.5, brow=.6))
meg = (svg('<rect width="960" height="1080" fill="#C8B898"/><rect width="960" height="1080" fill="url(#wallpaper)" opacity=".25"/>' + chiaroscuro(560, 620, 640, .6).replace("chiG", "chiM"))
       + sc9.svg() + '<div class="datecard" id="mcard"><b>2018 İHALESİ</b><span>yap-işlet-devret</span></div><div class="zero" id="mzero">0 TEKLİF</div>')
JS.append(sc9.js() + sc9.camera_js(win("meg")[0], win("meg")[1], dz=260, dx=60))

# 10) bedel: proje ikiye, 2,1 → 5,6 milyar
cost = (svg('<rect width="960" height="1080" fill="#14181E"/>'
            + '<g id="rdL"><rect x="80" y="180" width="380" height="60" rx="12" fill="#4A4A4E" stroke="#F2EBDD" stroke-width="4"/><text x="270" y="222" text-anchor="middle" font-family="Mont" font-weight="800" font-size="28" fill="#F2EBDD">ÇEŞMELİ-KIZKALESİ</text></g>'
            + '<g id="rdR"><rect x="500" y="180" width="380" height="60" rx="12" fill="#4A4A4E" stroke="#8A96A8" stroke-width="4" stroke-dasharray="10 8"/><text x="690" y="222" text-anchor="middle" font-family="Mont" font-weight="800" font-size="28" fill="#8A96A8">KIZKALESİ-TAŞUCU</text></g>'
            + '<path d="M200 880 V420" stroke="#2A2E36" stroke-width="150"/><rect id="b21" x="125" y="772" width="150" height="108" fill="#F5B82E"/>'
            + '<path d="M700 880 V420" stroke="#2A2E36" stroke-width="150"/><rect id="b56" x="625" y="880" width="150" height="0" fill="#E8524A"/>'
            + '<text x="200" y="740" text-anchor="middle" font-family="Mont" font-weight="800" font-size="48" fill="#F5B82E">2,1</text><text id="t56" x="700" y="390" text-anchor="middle" font-family="Mont" font-weight="800" font-size="64" fill="#E8524A" opacity="0">5,6</text>'
            + '<text x="200" y="940" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#C9D6E4">Şubat 2021</text><text x="700" y="940" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#C9D6E4">Haziran 2022</text>'
            + '<text x="480" y="1020" text-anchor="middle" font-family="Mont" font-weight="600" font-size="28" fill="#8A96A8">ihale bedeli · milyar TL</text>'))

# 11) sekiz yıl: zaman çizelgesi
years = [(2018, "ihale · teklif yok"), (2021, "ikiye bölündü"), (2022, "ihale tamam"), (2026, "açıldı")]
eight = svg('<rect width="960" height="1080" fill="#F2E6C8"/><path id="tl" d="M120 560 H840" stroke="#1B1414" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
            + "".join(f'<g transform="translate({ {2018: 120, 2021: 400, 2022: 580, 2026: 840}[y]} 560)"><g class="ty"><circle r="26" fill="{"#4CAF6A" if y == 2026 else "#E8524A"}" stroke="#1B1414" stroke-width="6"/>'
                      f'<text y="{-84 if i % 2 == 0 else 90}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="44" fill="#1B1414">{y}</text>'
                      f'<text y="{-46 if i % 2 == 0 else 128}" text-anchor="middle" font-family="Mont" font-weight="600" font-size="24" fill="#5A4A38">{t}</text></g></g>' for i, (y, t) in enumerate(years))) \
    + '<div class="bignum dark" id="e8" style="top:auto;bottom:120px">8 YIL</div>'

# 12) kapanış: gün batımında sahil otoyolu, akan trafik
cam12 = Cam(horizon=500, vpx=420, f=900, eye=420, sun=(1, 1), alt=14, haze="#F2B878")
sc12 = Scene(cam12, "en", ground=("#3E5A3A", "#C8A070"), sky=False)
sc12.add_ground([(500, 60), (4000, 60), (4000, 14000), (500, 14000)], 'fill="#2A5A80"')
sc12.add_road(-150, 1100, 60, 14000, color="#4A4A4E", line="#F2EBDD")
for i in range(6):
    sc12.add(-150 + (i % 2) * 260 - 130, 1400 + i * 1500, car_rear(CARS[i + 2], seed=i), CAR_H, 150, w=190)
sc12.add(-150, 7000, viaduct(1200, 3, 600), 700, 1000, w=1, shadow=False)
end = (svg('<defs><linearGradient id="sunsky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3A6A"/><stop offset=".6" stop-color="#E88A5A"/><stop offset="1" stop-color="#F7C88A"/></linearGradient></defs>'
           '<rect width="960" height="502" fill="url(#sunsky2)"/><circle cx="760" cy="480" r="66" fill="#FFE2A0"/>')
       + sc12.svg() + '<div class="endq" id="eq">ÖNÜMÜZDEKİ YAZ<br>KUYRUK BİTECEK Mİ?<br><b>YORUMLARA YAZ</b></div>')
JS.append(sc12.js() + sc12.camera_js(win("end")[0], win("end")[1], dz=1400, ease="none"))

sources = ('<div class="fill" style="background:#0B1220"></div><div class="srcbox"><b>KAYNAKLAR</b><br>'
           'AA · CNN Türk · Vatan (19.10.2026)<br>Aksiyon · Memurlar.net (ilk gün 17.681 araç)<br>Habertürk (2018 ihalesi)<br>'
           'Resmî Gazete ihale ilanı (2021)<br>"18 dk" bakanlık hedefidir; "8 dk" bir sürücünün anlatımı.</div>')

HTML = dict(hook=hook, d400=d400, slow=slow, open=opn, stats=stats, target=target, first=first, q=q, meg=meg, cost=cost, eight=eight, end=end, sources=sources)
scenes_html = "".join(scene(k, HTML[k]) for k in keys)
s = lambda k: S[k][0]
d = lambda k: win(k)[1]
js = "".join(f'tl.fromTo("#{k}-in",{{opacity:0}},{{opacity:1,duration:{FADE},ease:"power1.out"}},{s(k)});' for k in keys if k != "hook")
js += "".join(JS)
js += f"""
tl.fromTo(".heat",{{x:0}},{{x:-120,duration:{s('slow')},ease:"none"}},0);
tl.fromTo("#hksun",{{y:0}},{{y:20,duration:{d('hook')}}},0);
tl.fromTo("#dcard",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('d400')+.1});
tl.fromTo("#mhand",{{rotation:0,transformOrigin:"50% 95%"}},{{rotation:900,duration:{d('slow')},ease:"power1.in"}},{s('slow')});
tl.fromTo("#hhand",{{rotation:0,transformOrigin:"50% 94%"}},{{rotation:75,duration:{d('slow')},ease:"power1.in"}},{s('slow')});
tl.to("#slowarc",{{attr:{{"stroke-dashoffset":0}},duration:{d('slow')-.5}}},{s('slow')+.2});
tl.fromTo("#snum",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},{A('iki buçuk')});
tl.fromTo("#ocard",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('open')+.2});
tl.fromTo("#st1",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.35,ease:"power3.out"}},{A('Elli iki')});
tl.fromTo("#st2",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.35,ease:"power3.out"}},{A('Yedi')});
tl.fromTo("#st3",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.35,ease:"power3.out"}},{A('beş viyadük')});
tl.fromTo("#st4",{{x:-80,opacity:0}},{{x:0,opacity:1,duration:.35,ease:"power3.out"}},{A('on köprülü')});
tl.fromTo("#barnew",{{attr:{{width:780}}}},{{attr:{{width:94}},duration:.9,ease:"power3.inOut"}},{A('on sekiz')-.3});
tl.fromTo("#t18",{{opacity:0}},{{opacity:1,duration:.3}},{A('on sekiz')+.4});
tl.fromTo("#drv",{{y:60}},{{y:0,duration:.6,ease:"power2.out"}},{s('first')});
(function(){{const o={{v:0}};tl.to(o,{{v:17681,duration:2.4,ease:"power2.out",onUpdate:()=>{{document.getElementById("fcn").textContent=Math.round(o.v).toLocaleString("tr-TR");}}}},{A('on yedi')});}})();
tl.fromTo("#fc",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('on yedi')-.2});
tl.fromTo("#fq",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Bir sürücüye')});
tl.fromTo(".cal",{{y:-600,opacity:0}},{{y:0,opacity:1,duration:.45,stagger:.18,ease:"bounce.out"}},{s('q')});
tl.fromTo("#qq",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{s('q')+.3});
tl.fromTo("#mcard",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{A('2018')});
tl.fromTo("#mzero",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.in"}},{A('tek bir')});
tl.fromTo("#rdR",{{x:-60}},{{x:0,duration:.5,ease:"back.out(2)"}},{A('ikiye')});
tl.to("#b56",{{attr:{{y:470,height:410}},duration:1,ease:"power2.out"}},{A('beş buçuk')-.2});
tl.to("#t56",{{opacity:1,duration:.3}},{A('beş buçuk')+.6});
tl.to("#tl",{{attr:{{"stroke-dashoffset":0}},duration:1.4,ease:"power1.inOut"}},{s('eight')+.1});
tl.fromTo(".ty",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.3,stagger:.35,ease:"back.out(2)"}},{s('eight')+.1});
tl.fromTo("#e8",{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"power3.out"}},{A('sekiz yıl')});
tl.fromTo("#eq",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5}},{s('end')+.2});
"""
css = """
.datecard { position:absolute; left:40px; top:40px; padding:20px 28px; border-radius:22px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA; }
.datecard b { display:block; font-weight:800; font-size:58px; color:#F5B82E; } .datecard span { display:block; font-weight:600; font-size:28px; color:#C9D6E4; margin-top:6px; max-width:760px; }
.bignum { position:absolute; left:0; right:0; top:40px; text-align:center; font-weight:800; font-size:110px; color:#E8524A; line-height:1; text-shadow:0 6px 0 #1B1414; }
.bignum span { display:block; font-size:32px; color:#1B1414; text-shadow:none; margin-top:10px; } .bignum.dark { color:#1B1414; text-shadow:0 6px 0 #F5B82E; font-size:150px; }
.stat { position:absolute; left:40px; padding:14px 26px; border-radius:20px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA; font-weight:800; font-size:72px; color:#F5B82E; line-height:1; }
.stat i { font-style:normal; font-size:36px; color:#F4F1EA; }
.counter { position:absolute; right:40px; top:40px; padding:18px 28px; border-radius:22px; background:#0B1220; border:3px solid #F4F1EA; text-align:right; }
.counter b { display:block; font-weight:800; font-size:96px; color:#F5B82E; line-height:1; } .counter span { font-weight:600; font-size:30px; color:#C9D6E4; }
.bubble { position:absolute; left:420px; right:40px; top:330px; padding:24px 30px; border-radius:30px; background:#F4F1EA; color:#0B1220; border:5px solid #1B1414; font-weight:800; font-size:44px; line-height:1.15; }
.bubble b { color:#2E8A4A; font-size:64px; }
.bigq { position:absolute; left:0; right:0; bottom:110px; text-align:center; font-weight:800; font-size:88px; line-height:1.05; color:#1B1414; text-shadow:0 6px 0 #F5B82E; }
.zero { position:absolute; right:60px; top:300px; padding:18px 30px; border:8px solid #E8524A; border-radius:18px; color:#E8524A; background:rgba(244,241,234,.92); font-weight:800; font-size:72px; transform:rotate(-8deg); }
.endq { position:absolute; left:40px; right:40px; top:60px; text-align:center; font-weight:800; font-size:64px; line-height:1.12; color:#F4F1EA; text-shadow:0 4px 0 #1B1414; }
.endq b { display:inline-block; margin-top:14px; padding:10px 26px; border-radius:18px; background:#F5B82E; color:#0B1220; text-shadow:none; font-size:52px; }
.srcbox { position:absolute; left:60px; right:60px; top:200px; font-weight:600; font-size:34px; line-height:1.6; color:#C9D6E4; } .srcbox b { color:#F5B82E; font-size:44px; }
"""
DEFS = DEFS2.replace("</defs>", "") + DEFS_P + depth_defs(cam1) + "</defs>"
html = page(words, mouth, scenes_html, js, total=TOTAL, voice_end=VOICE_END, kicker="MEĞERSE DOSYASI <b>|</b> GÜNDEM · MERSİN",
            title="ERDEMLİ KUYRUĞU BİTTİ Mİ?", voice_src="assets/erdemli/voice.mp3", extra_css=css, glow="#3A2A14", fx=True, defs=DEFS)
(HF / "index.html").write_text(html, encoding="utf-8")
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
