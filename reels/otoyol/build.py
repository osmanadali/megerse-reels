"""Otoyoldaki kesik çizgi kaç metre? (Meğerse finalde + ayrı gönderme çağrısı). LAYOUT_V7, anlatıcı yok, az efekt, outro.

Ses akışı (ses_isle.sh): ElevenLabs "Fatih Yıldırım" → tighten → atempo → align.py --text metin.txt → insert_gap (kancadan sonra intro)
         → reels/otoyol/words.json + hf/assets/otoyol/voice.mp3 → build → sfx miksi → render hf/renders/otoyol.mp4
Ses yokken yerleşim testi: YOL_GECICI=1 (metinden sahte kelime zamanları, sessiz ses).
Sahne sonu kuralı: her sahnenin son görsel olayından sonra ≥1,2 sn kalmalı (build sonunda kontrol yazdırılır).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reels/otoyol"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from reelkit2 import (HF, INTRO_CSS, INTRO_DUR, LAYOUT_V7, OUTRO_CSS, OUTRO_DUR, SHARE_CSS, anchor, flash_js, intro_html, intro_js,  # noqa: E402
                      intro_sfx, outro_html, outro_js, outro_sfx, page, share_cta_html, share_cta_js, share_cta_sfx)
from roadart import YELLOW  # noqa: E402
import sahneler as S  # noqa: E402

D = ROOT / "reels/otoyol"
GECICI = os.environ.get("YOL_GECICI") == "1"
HOOK_END = "metre?"
if GECICI:
    txt = (D / "metin.txt").read_text(encoding="utf-8").split()
    words, t = [], .3
    for w in txt:
        dur = .09 + len(w) * .055
        words.append({"text": w, "startMs": int(t * 1000), "endMs": int((t + dur) * 1000)})
        t += dur + (.22 if w[-1] in ".,;:?" else .04)
        if w == HOOK_END and len(words) < 12:
            t += INTRO_DUR + .15
    VOICE = "assets/otoyol/gecici.mp3"
    a = HF / "assets/otoyol"
    a.mkdir(parents=True, exist_ok=True)
    if not (a / "gecici.mp3").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "120", str(a / "gecici.mp3")], check=True)
else:
    words = json.loads((D / "words.json").read_text(encoding="utf-8"))
    VOICE = "assets/otoyol/mix.mp3"

L = LAYOUT_V7
TOP, LOW = L["top_tag"], L["low_tag"]
HOOK_I = next(i for i, w in enumerate(words) if w["text"] == HOOK_END)
INTRO_T = round(words[HOOK_I]["endMs"] / 1000 + .1, 2)
A = lambda p, after=0.0: anchor(words, p, after)

# J-kesme: yeni sahnenin görüntüsü anlatıcının yeni cümlesinden biraz sonra gelir; önceki sahnenin son anı yarım kalmaz
LAG = {"tahmin": 0, "yolcu": .45, "kgm": .45, "hiz": .45, "ulke": .45, "turler": .45, "sis": .45, "kure": .45, "meg": 0, "cta": .3}
T_CTA = A("Sen de bunu")
T_GO = round(words[-1]["endMs"] / 1000 + .15, 2)
CTA_JS, OUTRO_T, LAND_T = share_cta_js(T_CTA + LAG["cta"] + .2, T_GO)
TOTAL = round(OUTRO_T + OUTRO_DUR, 2)
VOICE_END = round(words[-1]["endMs"] / 1000 + .3, 2)

T = {"hook": 0.0, "intro": INTRO_T, "tahmin": A("Amerika'da üç"), "yolcu": A("Arabada yolcu"), "kgm": A("Karayolları"), "hiz": A("Yani yüz"),
     "ulke": A("Altı metre, Amerika'da"), "turler": A("Çizgi şehir"), "sis": A("Şehir dışı yolların"), "kure": A("Gece parlamayı"),
     "meg": A("Meğerse"), "cta": T_CTA, "outro": OUTRO_T}
R = dict(T)
T = {k: round(v + LAG.get(k, 0), 2) for k, v in T.items()}
keys = list(T)
X = .3
S_ = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
s = lambda k: S_[k][0]
end = lambda k: S_[k][1]


def win(k):
    a, b = S_[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


def scene(k, inner, bg="#0B0E14"):
    a, dd = win(k)
    return (f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{dd}" data-track-index="{1 + keys.index(k) % 2}">'
            f'<div class="fill" style="background:{bg}"></div><div class="fill" id="{k}-in">{inner}</div></div>')


def tag(idn, text, y=TOP, cls="dark", style=""):
    return f'<div class="tag c {cls}" id="{idn}" style="top:{y}px;opacity:0;{style}">{text}</div>'


JS, SFX = [], []
pop = S.pop_js
cam = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#C8D4DE", zfar=16000)
camf = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#E4E8EB", zfar=6000)
camn = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#1A2234", zfar=16000)

# 1) KANCA: 120 km/sa sürücü gözü, "metre?" sözünde kare donar, "? METRE"
sc_h = S.pov_scene(cam, "ph")
hook = S.pov_html(sc_h, "gun", hud='<div class="hud" id="hq" style="top:300px"><b>?</b> METRE</div>')
t_frz = A("sence")
JS.append(S.pov_js(sc_h, "ph", 0, round(t_frz, 2)) + pop("#hq", t_frz, 2.2, .3)
          + f'tl.to("#hq b",{{scale:1.3,duration:.25,yoyo:true,repeat:3,ease:"sine.inOut"}},{t_frz + .3:.2f});')
SFX += [(.05, "whoosh", .3)]

# 2) İNTRO
JS.append(intro_js(s("intro")))
SFX += intro_sfx(s("intro"))

# 3) TAHMİN: ABD, 355 öğrenci, ortanca 61 cm ↔ gerçek 4,57 m
tahmin = S.kiyas_html(457, 61, "4,57 m", "TAHMİN\n61 cm", "ABD · 355 ÖĞRENCİ", idp="ta")
JS.append(S.kiyas_js(s("tahmin"), A("altmış"), A("Oysa"), idp="ta", dur=end("tahmin") - s("tahmin")))
SFX += [(A("Oysa") + .1, "pop", .3)]

# 4) YOLCU: 3,05 m çizgiye 1,19 m; hız 40 → 97, tahmin değişmez
yolcu = S.kiyas_html(305, 119, "3,05 m", "TAHMİN\n1,19 m", "ARABADAKİ YOLCULAR", idp="yo", speed=True)
JS.append(S.kiyas_js(s("yolcu"), A("ortalama", s("yolcu")), A("üç metrelik"), idp="yo", t_speed=(A("hız da"), A("değiştirmedi") + .5), dur=end("yolcu") - s("yolcu")))

# 5) KGM: kuş bakışı, drone iner, 6 m / 9 m bantları, 15 cm
kgm = (S.olcek_html() + tag("ktg", "KARAYOLLARI GENEL MÜDÜRLÜĞÜ STANDARDI", TOP, "dark", "font-size:32px")
       + '<div class="pill" id="k15" style="top:1250px">GENİŞLİK <b>15 cm</b></div>')
JS.append(pop("#ktg", s("kgm") + .1) + S.olcek_js(s("kgm"), A("otoyolda her", R["kgm"]), None, A("altı metre", R["kgm"]), A("dokuz metre", R["kgm"]))
          + pop("#k15", A("on beş", R["kgm"])) + f'tl.to("#k15",{{opacity:0,duration:.2}},{A("dokuz metre", R["kgm"]) - .1:.2f});')
SFX += [(A("altı metre", R["kgm"]), "pop", .3), (A("dokuz metre", R["kgm"]), "pop", .3)]

# 6) HIZ: 120 km/sa, geçen çizgi sayacı, 0,18 sn
sc_v = S.pov_scene(cam, "pv")
hiz = S.pov_html(sc_v, "gun", hud='<div class="hud" id="cntw" style="top:230px">120 km/sa<br><b id="cnt">0</b> çizgi</div>'
                 + '<div class="pill" id="h018" style="top:1250px">her çizgi <b>0,18 sn</b></div>')
h0, h1 = s("hiz"), end("hiz")
JS.append(S.pov_js(sc_v, "pv", h0, round(h1 - h0 + X, 2), counter=("cnt", h0 + .1)) + pop("#h018", A("beşte", R["hiz"])))

# 7) ÜLKELER: Türkiye 6 m, ABD 3,05 m (×2), İngiltere 2 m (×3)
ulke = S.ulke_html()
JS.append(S.ulke_js(s("ulke"), A("Amerika'da önerilen", R["ulke"]) - .2, A("neredeyse iki", R["ulke"])))

# 8) YOL TÜRLERİ: otoyol / şehir dışı / şehir içi (aynı hızda akan şeritler)
turler = S.turler_html()
u0, u1 = s("turler"), end("turler")
JS.append(S.turler_js(u0, round(u1 - u0 + X, 2), (u0 + .1, A("dört buçuk", R["turler"]), A("üç metreye", R["turler"]))))

# 9) SİS: şehir dışı yolların sisli kesimi, 9 m çizgi / 3 m boşluk
sc_f = S.pov_scene(camf, "pf", 900, 300)
sis = S.pov_html(sc_f, "sis", fog=True, hud='<div class="pill dark2" id="sf1" style="top:250px"><b>9 m</b> çizgi · <b>3 m</b> boşluk</div>') + tag("sft", "ŞEHİR DIŞI · SİSLİ KESİM", 1250, "dark")
f0, f1 = s("sis"), end("sis")
JS.append(S.pov_js(sc_f, "pf", f0, round(f1 - f0 + X, 2), speed_kmh=60) + pop("#sft", f0 + .2) + pop("#sf1", A("dokuz metre", R["sis"])))

# 10) CAM KÜRE: kesit, far ışını girer ve geri döner
kure = S.kure_html()
JS.append(S.kure_js(s("kure"), A("farın", R["kure"]), A("geri", R["kure"])))
SFX += [(A("geri", R["kure"]), "ding", .3)]

# 11) MEĞERSE: çizginin yanına bir otomobil, boşluğa iki otomobil
m0 = s("meg")
meg = S.meg_html()
JS.append(flash_js(m0, .9, .35) + S.meg_js(m0, A("otomobilin", m0) - .4, A("aradaki", m0) - .2))
SFX += [(m0 - 1.0, "riser", .5), (m0, "boom", .6)]

# 12) ÇAĞRI: gece sürücü gözü + GÖNDER → uçak outro'ya
sc_n = S.pov_scene(camn, "pn", night=True)
cta = S.pov_html(sc_n, "gece", night=True)
c0 = s("cta")
JS.append(S.pov_js(sc_n, "pn", c0, round(TOTAL - c0, 2), speed_kmh=100) + CTA_JS)
SFX += share_cta_sfx(T_GO, LAND_T)

# OUTRO
JS.append(outro_js(s("outro"), land_t=LAND_T))
SFX += outro_sfx(s("outro"))

HTML = dict(hook=hook, intro=intro_html("08"), tahmin=tahmin, yolcu=yolcu, kgm=kgm, hiz=hiz, ulke=ulke, turler=turler, sis=sis, kure=kure, meg=meg, cta=cta,
            outro=outro_html(label3="GÖNDER", fixed_icons=True))
BG = dict(ulke="radial-gradient(80% 55% at 50% 42%,#1E2A3C,#070A10)", turler="radial-gradient(80% 55% at 50% 42%,#1E2A3C,#070A10)")
scenes_html = "".join(scene(k, HTML[k], BG.get(k, "#0B0E14")) for k in keys) + share_cta_html()

js = ""
for i, k in enumerate(keys):
    a, dd = win(k)
    if k not in ("hook", "intro", "outro"):
        js += f'tl.fromTo("#{k}-in",{{opacity:0,filter:"blur(10px)"}},{{opacity:1,filter:"blur(0px)",duration:.35,ease:"power3.out",immediateRender:false}},{a:.2f});'
    if i + 1 < len(keys) and keys[i + 1] not in ("intro", "outro") and k != "intro":
        js += f'tl.to("#{k}-in",{{opacity:0,duration:{X:.2f},ease:"power2.in"}},{T[keys[i + 1]]:.2f});'
js += f'tl.fromTo("#outro-in",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{s("outro"):.2f});'
js += "".join(JS)

css = """
.tag { position:absolute; padding:14px 26px; border-radius:18px; font-weight:800; font-size:44px; background:#FFD23F; color:#111; box-shadow:0 8px 0 #000; }
.tag.c { left:0; right:0; margin:0 auto; width:fit-content; }
.tag.dark { background:rgba(10,14,22,.88); color:#fff; border:3px solid #fff; box-shadow:none; font-size:38px; }
.pill { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:12px 30px; border-radius:22px; background:#fff; color:#141414; border:5px solid #1B1414;
        box-shadow:0 10px 0 rgba(0,0,0,.5); font-weight:800; font-size:50px; opacity:0; }
.pill b { color:#1E8FE0; } .pill.dark2 { background:rgba(10,14,22,.86); color:#fff; border-color:#fff; } .pill.dark2 b { color:#FFD23F; }
""" + S.POV_CSS + S.TUR_CSS + S.KIYAS_CSS + S.ULKE_CSS + S.KURE_CSS + S.MEG_CSS
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"
html = page(words, [], scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="", voice_src=VOICE, extra_css=css + INTRO_CSS + OUTRO_CSS + SHARE_CSS, defs=DEFS,
            avatar=False, chrome=False, caps="box", cap_top=L["cap_top"])
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(D / "sfx.json", "w"))
print("hf/index.html; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S_.items()})

# sahne sonu kontrolü: son görsel olaydan sonra ≥1,2 sn
ev = re.findall(r'tl\.(?:fromTo|to)\("([^"]+)",.*?\},([\d.]+)\);', js)
for i, k in enumerate(keys[:-2]):
    a, b = T[k], T[keys[i + 1]]
    late = sorted({(sel, round(b - float(t), 2)) for sel, t in ev if a < float(t) < b and b - float(t) < 1.2 and not re.match(r"#\w+-in$|#flash|window", sel)}, key=lambda x: x[1])
    if late:
        print("  ⚠", k, "→", late[:6])
