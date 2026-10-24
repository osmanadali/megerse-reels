"""Arsa değerleri nasıl hesaplanıyor? (Meğerse finalde). Yerleşim LAYOUT_V7, anlatıcı yok, az ve kısık efekt, sonda soru yok, outro.

Ses akışı (ses_isle.sh): ElevenLabs "Fatih Yıldırım" mp3 → tighten.py → align.py --text metin.txt → insert_gap.py (kancadan sonra intro)
         → reels/arsa-degeri/words.json + hf/assets/arsa/voice.mp3 → build → sfx miksi → render hf/renders/arsa-degeri.mp4
Ses yokken yerleşim testi: ARSA_GECICI=1 (metinden sahte kelime zamanları, sessiz ses).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from isoart import Iso  # noqa: E402
from reelkit2 import (HF, INTRO_CSS, INTRO_DUR, LAYOUT_V7, OUTRO_CSS, OUTRO_DUR, anchor, flash_js, intro_html, intro_js,  # noqa: E402
                      intro_sfx, outro_html, outro_js, outro_sfx, page, punch_js, shake_js)

D = ROOT / "reels/arsa-degeri"
GECICI = os.environ.get("ARSA_GECICI") == "1"
HOOK_END = "olabilir."
if GECICI:
    txt = (D / "metin.txt").read_text(encoding="utf-8").split()
    words, t = [], .3
    for w in txt:
        dur = .09 + len(w) * .055
        words.append({"text": w, "startMs": int(t * 1000), "endMs": int((t + dur) * 1000)})
        t += dur + (.22 if w[-1] in ".,;:?" else .04)
        if w == HOOK_END:
            t += INTRO_DUR + .15
    VOICE = "assets/arsa/gecici.mp3"
    a = HF / "assets/arsa"
    a.mkdir(parents=True, exist_ok=True)
    if not (a / "gecici.mp3").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "120", str(a / "gecici.mp3")], check=True)
else:
    words = json.loads((D / "words.json").read_text(encoding="utf-8"))
    VOICE = "assets/arsa/mix.mp3"

L = LAYOUT_V7
TOP, LOW = L["top_tag"], L["low_tag"]
HOOK_I = next(i for i, w in enumerate(words) if w["text"] == HOOK_END)
INTRO_T = round(words[HOOK_I]["endMs"] / 1000 + .1, 2)
VOICE_END = round(words[-1]["endMs"] / 1000 + .5, 2)
TOTAL = round(VOICE_END + OUTRO_DUR, 2)
A = lambda p, after=0.0: anchor(words, p, after)

T = {"hook": 0.0, "intro": INTRO_T, "rayic": A("Resmi"), "yollar": A("Uzman değerlemede"), "emsal": A("Yakındaki satış"),
     "imar": A("Farkı çoğu"), "kaks": A("Kilit sayı"), "dop": A("Tarlaysa"), "gelir": A("Gelir yolu"), "urla": A("Urla'da"),
     "meg": A("Meğerse"), "outro": VOICE_END}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
X = .12
s = lambda k: S[k][0]


def win(k):
    a, b = S[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


d = lambda k: win(k)[1]


def scene(k, inner):
    a, dd = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{dd}" data-track-index="1"><div class="fill" id="{k}-in">{inner}</div></div>'


def svg(inner, idn="", style=""):
    i = f' id="{idn}"' if idn else ""
    return f'<svg class="fill"{i} viewBox="0 0 1080 1920" style="overflow:visible;{style}">{inner}</svg>'


def tag(idn, text, y, cls="", style=""):
    return f'<div class="tag c {cls}" id="{idn}" style="top:{y}px;opacity:0;{style}">{text}</div>'


def lab(idn, text, x, y, cls="lab", style=""):
    """konumlu küçük etiket (x merkez)."""
    return f'<div class="{cls}" id="{idn}" style="left:{x - 300}px;top:{y}px;opacity:0;{style}">{text}</div>'


def pop_js(sel, t, s0=.4):
    return f'tl.fromTo("{sel}",{{scale:{s0},opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2.4)",immediateRender:false}},{t:.2f});tl.set("{sel}",{{opacity:0}},0);'


def seq_js(items):
    out = []
    for i, (sel, t) in enumerate(items):
        out.append(pop_js(sel, t))
        if i + 1 < len(items):
            out.append(f'tl.to("{sel}",{{opacity:0,scale:.9,duration:.15}},{items[i+1][1]-.15:.2f});')
    return "".join(out)


def grow_js(sel, t, dur=.6, ease="back.out(1.6)"):
    """SVG grubunu tabanından yukarı büyüt (fiyat sütunu, bina)."""
    return f'tl.fromTo("{sel}",{{scaleY:0,transformOrigin:"50% 100%"}},{{scaleY:1,duration:{dur},ease:"{ease}",immediateRender:false}},{t:.2f});tl.set("{sel}",{{scaleY:0,transformOrigin:"50% 100%"}},0);'


def count_js(idn, t, v0, v1, dur, fmt="tr"):
    f = 'Math.round(o.v).toLocaleString("tr-TR")' if fmt == "tr" else fmt
    return f'(function(){{const o={{v:{v0}}};tl.to(o,{{v:{v1},duration:{dur},ease:"power2.out",onUpdate:()=>{{document.getElementById("{idn}").textContent={f};}}}},{t:.2f});}})();'


JS, SFX = [], []
BG = '<rect width="1080" height="1920" fill="url(#bpbg)"/><rect width="1080" height="1920" fill="url(#grid)"/>'
GOLD, GREEN, RED, BLUE = "#FFD23F", "#3FCB8E", "#FF5A4E", "#5AB8FF"


def diorama(iso, idp, ghosts=False, cols=None):
    """iki komşu 500 m² arsa + önde yol (kanca ve final)."""
    p = [iso.slab(-80, -70, 560, 450, 30, "#7FA65A"), iso.road(-80, 330, 560, 50)]
    for k, x0 in enumerate((0, 240)):
        p.append(f'<g id="{idp}-p{k}">' + iso.tile(x0, 0, 200, 300, "#C9A46A") + iso.grass(x0, 0, 200, 300, 50, "#8A7A44", k * 13) + '</g>')
        p += [iso.stake(x, y) for x, y in ((x0, 0), (x0 + 200, 0), (x0, 300), (x0 + 200, 300))]
    p += [iso.tree(-50, -30, 1.1), iso.tree(470, -20), iso.house(-60, 120, 50, 60, 40)]
    if cols:
        for k, (x0, h) in enumerate(zip((70, 310), cols)):
            p.append(f'<g id="{idp}-c{k}" opacity=".92">' + iso.box(x0, 120, 0, 60, 60, h, GOLD) + '</g>')
    if ghosts:
        p.append(f'<g id="{idp}-g0">' + iso.building(50, 75, 100, 150, 1, 40, "#E9E2D3", cls=f"{idp}g0") + '</g>')
        p.append(f'<g id="{idp}-g1">' + iso.building(290, 75, 100, 150, 3, 40, "#E9E2D3", cls=f"{idp}g1") + '</g>')
    return "".join(p)


# 1) KANCA: aynı iki arsa, fiyat sütunları kat kat ayrışır
iso1 = Iso(493, 590, 1.2)
c0, c1 = iso1.label_pt(100, 150, 70), iso1.label_pt(340, 150, 300)
hook = (svg(BG + f'<g id="hk-d">{diorama(iso1, "hk", cols=(70, 300))}</g>', "hksvg")
        + lab("hkm0", "500 m²", *iso1.label_pt(100, 150), "lab", "") + lab("hkm1", "500 m²", *iso1.label_pt(340, 150), "lab", "")
        + lab("hkt0", "₺", c0[0], c0[1] - 70, "lab big") + lab("hkt1", "₺ ₺ ₺", c1[0], c1[1] - 70, "lab big")
        + '<div class="htitle" id="htitle">ARSA DEĞERİ<br><span>NASIL HESAPLANIR?</span></div>')
t_ayni, t_kat = A("aynı büyüklükte"), A("çok daha")
JS.append(f'tl.fromTo("#hk-d",{{scale:1.18,transformOrigin:"540px 800px"}},{{scale:1,duration:2.2,ease:"power2.out"}},0);'
          + f'tl.fromTo("#htitle",{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"back.out(2)"}},.05);tl.to("#htitle",{{y:-40,opacity:0,duration:.25}},{t_ayni-.25:.2f});'
          + pop_js("#hkm0", t_ayni) + pop_js("#hkm1", t_ayni + .12)
          + f'tl.to("#hkm0,#hkm1",{{opacity:0,duration:.2}},{A("biri")-.1:.2f});'
          + grow_js("#hk-c0", A("biri"), .5) + grow_js("#hk-c1", t_kat, .9, "back.out(1.3)")
          + pop_js("#hkt0", A("biri") + .4) + pop_js("#hkt1", t_kat + .8) + punch_js("#hksvg", t_kat + .8, 1.05))
SFX += [(t_kat + .1, "riser", .35), (t_kat + .85, "pop", .45)]

# 2) RAYİÇ: sokaktaki en düşük fiyat esas → asgari vergi değeri ≠ piyasa değeri
iso2 = Iso(300, 600, 1.25)
PR = ["9.200", "12.400", "7.800", "15.000"]
street = [iso2.slab(-40, -40, 660, 330, 24, "#7FA65A"), iso2.road(-40, 230, 660, 50)]
pins = []
for k in range(4):
    x0 = k * 150
    street.append(iso2.tile(x0, 0, 136, 210, "#C9A46A"))
    if k in (1, 3):
        street.append(iso2.house(x0 + 30, 50, 70, 90, 46))
    px, py = iso2.label_pt(x0 + 68, 105, 0)
    pins.append(f'<div class="pin" id="pin{k}" style="left:{px - 80}px;top:{py - 170}px;opacity:0"><b>{PR[k]}</b><i>₺/m²</i></div>')
rayic = (svg(BG + "".join(street), "rysvg") + "".join(pins)
         + tag("ryt", "RESMİ RAYİÇ", TOP) + '<div class="note" id="rynote" style="top:1080px;opacity:0">örnek fiyatlar</div>'
         + '<div class="doc" id="rydoc" style="top:1060px;opacity:0"><small>EMLAK VERGİSİ · TAKDİR KOMİSYONU</small>ASGARİ m² DEĞERİ<div class="stamp" id="rystamp">PİYASA DEĞERİ DEĞİL</div></div>')
t_low, t_asg, t_deg = A("en düşük"), A("asgari"), A("piyasa değeri değil")
JS.append(pop_js("#ryt", s("rayic") + .1)
          + f'tl.fromTo(".pin",{{y:-60,opacity:0}},{{y:0,opacity:1,duration:.3,stagger:.08,ease:"back.out(2)",immediateRender:false}},{s("rayic")+.15:.2f});tl.set(".pin",{{opacity:0}},0);'
          + pop_js("#rynote", s("rayic") + .5) + f'tl.to("#rynote",{{opacity:0,duration:.2}},{t_asg-.2:.2f});'
          + f'tl.to("#pin0,#pin1,#pin3",{{opacity:.3,duration:.25}},{t_low:.2f});tl.to("#pin2",{{scale:1.25,backgroundColor:"{GOLD}",duration:.25,ease:"back.out(3)"}},{t_low:.2f});'
          + f'tl.fromTo("#rydoc",{{y:120,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"back.out(1.8)",immediateRender:false}},{t_asg:.2f});tl.set("#rydoc",{{opacity:0}},0);'
          + f'tl.fromTo("#rystamp",{{scale:2.6,opacity:0}},{{scale:1,opacity:1,duration:.18,ease:"power4.in",immediateRender:false}},{t_deg:.2f});tl.set("#rystamp",{{opacity:0}},0);'
          + shake_js("#rydoc", t_deg + .18, 8, 4))
SFX += [(t_deg + .18, "boom", .4)]

# 3) ÜÇ YOL: benzer satışlar, gelir, maliyet → arsada genellikle ilki
ICON = {
    "pin": '<svg viewBox="0 0 100 100" width="130" height="130"><circle cx="30" cy="70" r="9" fill="#1B1414"/><path d="M50 8 C34 8 24 20 24 34 C24 52 50 78 50 78 C50 78 76 52 76 34 C76 20 66 8 50 8 Z" fill="#FF5A4E" stroke="#1B1414" stroke-width="5"/><circle cx="50" cy="34" r="10" fill="#fff"/><path d="M68 86 L84 62 L94 70" stroke="#1B1414" stroke-width="5" fill="none"/></svg>',
    "coin": '<svg viewBox="0 0 100 100" width="130" height="130"><rect x="14" y="30" width="36" height="58" fill="#E9E2D3" stroke="#1B1414" stroke-width="5"/><path d="M22 42h8M36 42h6M22 56h8M36 56h6M22 70h8M36 70h6" stroke="#5AB8FF" stroke-width="6"/><circle cx="70" cy="48" r="20" fill="#FFD23F" stroke="#1B1414" stroke-width="5"/><text x="70" y="57" text-anchor="middle" font-family="Mont" font-weight="800" font-size="26" fill="#1B1414">₺</text><circle cx="72" cy="78" r="14" fill="#FFD23F" stroke="#1B1414" stroke-width="5"/></svg>',
    "crane": '<svg viewBox="0 0 100 100" width="130" height="130"><path d="M28 92 V18 M28 18 H88 M28 30 L44 18 M60 18 V44" stroke="#FFB020" stroke-width="7" fill="none"/><rect x="52" y="44" width="16" height="12" fill="#1B1414"/><rect x="8" y="78" width="40" height="14" fill="#C2563A" stroke="#1B1414" stroke-width="4"/><rect x="18" y="64" width="24" height="14" fill="#C2563A" stroke="#1B1414" stroke-width="4"/></svg>',
}
cards = "".join(f'<div class="mcard" id="mc{i}" style="left:{40 + i * 340}px">{ICON[ic]}<b>{t1}</b><span>{t2}</span></div>'
                for i, (ic, t1, t2) in enumerate([("pin", "PAZAR", "satış ve ilanlar"), ("coin", "GELİR", "proje / kira"), ("crane", "MALİYET", "yapılar için")]))
yollar = svg(BG, "ylsvg") + tag("ylt", "UZMAN DEĞERLEMESİ · 3 YOL", TOP) + cards + tag("yllow", "ARSADA GENELLİKLE PAZAR YOLU", LOW - 80, "dark")
t_ilk = A("arsada genellikle")
JS.append(pop_js("#ylt", s("yollar") + .1) + pop_js("#mc0", A("pazar", s("yollar"))) + pop_js("#mc1", A("gelir", s("yollar"))) + pop_js("#mc2", A("maliyet"))
          + f'tl.to("#mc1,#mc2",{{opacity:.28,scale:.92,duration:.3}},{t_ilk:.2f});tl.to("#mc0",{{scale:1.1,borderColor:"{GOLD}",boxShadow:"0 0 60px rgba(255,210,63,.55)",duration:.3,ease:"back.out(2)"}},{t_ilk:.2f});'
          + pop_js("#yllow", t_ilk + .2))
SFX += [(t_ilk, "ding", .35)]

# 4) BENZER SATIŞLAR: m²'ye çevir, yüzdeyle düzelt
EM = [("SATIŞ", "2.400.000 ₺", "300 m²", 8000, "KONUM", "+%10", 8800), ("İLAN", "3.800.000 ₺", "400 m²", 9500, "İMAR", "−%10", 8550), ("SATIŞ", "3.600.000 ₺", "500 m²", 7200, "TARİH", "+%15", 8280)]
ecards = "".join(f'<div class="ecard" id="ec{i}" style="left:{45 + i * 340}px"><small>{n}</small><div class="ep" id="ep{i}">{p}<br><i>{a}</i></div><div class="em" id="em{i}" style="opacity:0"><b id="ev{i}">{v:,}</b><i>₺/m²</i></div>'
                 f'<div class="chip" id="ch{i}">{cn} <b>{cv}</b></div></div>'.replace(",", ".") for i, (n, p, a, v, cn, cv, v2) in enumerate(EM))
emsal = (svg(BG + Iso(540, 1010, 1.0).slab(-90, -90, 180, 180, 20, "#C9A46A") + Iso(540, 1010, 1.0).tile(-90, -90, 180, 180, "#D9B47A"), "emsvg")
         + tag("emt", "PAZAR YOLU · örnek", TOP) + ecards
         + '<div class="res" id="emres" style="opacity:0">≈ <b>8.540</b> ₺/m²<small>senin arsan · örnek</small></div>')
t_m2 = A("metrekareye")
JS.append(pop_js("#emt", s("emsal") + .1)
          + f'tl.fromTo(".ecard",{{y:80,opacity:0}},{{y:0,opacity:1,duration:.35,stagger:.1,ease:"back.out(1.8)",immediateRender:false}},{s("emsal")+.1:.2f});tl.set(".ecard",{{opacity:0}},0);'
          + f'tl.to(".ep",{{opacity:0,y:-20,duration:.2}},{t_m2:.2f});tl.fromTo(".em",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.25,immediateRender:false}},{t_m2+.15:.2f});'
          + "".join(pop_js(f"#ch{i}", A(aw, s("emsal"))) + count_js(f"ev{i}", A(aw, s("emsal")) + .1, v, v2, .5)
                    for i, ((_, _, _, v, _, _, v2), aw) in enumerate(zip(EM, ("konum", "imar", "tarih"))))
          + f'tl.fromTo("#emres",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{A("yüzdeyle")+.3:.2f});tl.set("#emres",{{opacity:0}},0);')
SFX += [(A("yüzdeyle") + .3, "pop", .35)]

# 5) İMAR: tapudaki "arsa" yetmez → imar durum belgesi
ROWS = [("Kullanım", "Konut"), ("Emsal (KAKS)", "1,50"), ("Kat adedi", "plana göre"), ("Çekme mesafesi", "plana göre")]
imar = (svg(BG, "imsvg") + tag("imt", "İMAR DURUMU", TOP)
        + '<div class="tapu" id="tapu" style="opacity:0"><small>TAPU</small>Cinsi: <b>ARSA</b><div class="nx" id="tapux">≠ imarlı</div></div>'
        + '<div class="idb" id="idb" style="opacity:0"><h3>İMAR DURUM BELGESİ</h3>' + "".join(f'<div class="row" id="ir{i}"><span>{a}</span><b>{b}</b></div>' for i, (a, b) in enumerate(ROWS)) + '</div>')
t_tapu, t_idb = A("Tapuda"), A("imar durum")
JS.append(pop_js("#imt", s("imar") + .1)
          + f'tl.fromTo("#tapu",{{x:-200,opacity:0,rotation:-10}},{{x:0,opacity:1,rotation:-5,duration:.35,ease:"back.out(1.6)",immediateRender:false}},{t_tapu:.2f});tl.set("#tapu",{{opacity:0}},0);'
          + pop_js("#tapux", A("yetmez"))
          + f'tl.to("#tapu",{{x:-120,y:-40,scale:.75,opacity:.55,duration:.35}},{t_idb-.1:.2f});'
          + f'tl.fromTo("#idb",{{y:200,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"back.out(1.5)",immediateRender:false}},{t_idb:.2f});tl.set("#idb",{{opacity:0}},0);'
          + f'tl.fromTo(".row",{{x:-40,opacity:0}},{{x:0,opacity:1,duration:.22,stagger:.2,immediateRender:false}},{t_idb+.4:.2f});tl.set(".row",{{opacity:0}},0);'
          + f'tl.to("#ir1",{{backgroundColor:"rgba(255,210,63,.35)",duration:.25}},{s("kaks")-.5:.2f});')
SFX += [(t_idb, "swish", .3)]

# 6) EMSAL (KAKS): aynı 500 m², 1,50 → 750 m², 0,50 → 250 m²
iso6 = Iso(493, 620, 1.2)
kp = [iso6.slab(-80, -70, 560, 420, 26, "#7FA65A"), iso6.road(-80, 310, 560, 50)]
for k, x0 in enumerate((0, 240)):
    kp.append(iso6.tile(x0, 0, 200, 300, "#C9A46A"))
kp.append('<g id="kb0">' + iso6.building(50, 75, 100, 150, 1, 44, "#E9E2D3", cls="ka") + '</g>')
kp.append('<g id="kb1">' + iso6.building(290, 75, 100, 150, 3, 44, "#E9E2D3", cls="kb") + '</g>')
kaks = (svg(BG + "".join(kp), "kksvg") + tag("kkt", "EMSAL = KAKS", TOP)
        + lab("kk0", "emsal 0,50", *iso6.label_pt(100, 300, -10), "lab") + lab("kk1", "emsal 1,50", *iso6.label_pt(340, 300, -10), "lab")
        + lab("kv0", '<b id="kv0n">0</b> m²', *iso6.label_pt(60, 200, 60), "lab big")
        + lab("kv1", '<b id="kv1n">0</b> m²', *iso6.label_pt(360, 120, 200), "lab big")
        + tag("kf1", "500 m² × 1,50 = 750 m²", LOW, "dark") + tag("kf0", "500 m² × 0,50 = 250 m²", LOW, "dark"))
t_15, t_yari = A("bir buçuksa"), A("yarımsa")
JS.append(pop_js("#kkt", s("kaks") + .1)
          + f'tl.fromTo("#kb1 .kb",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.25,stagger:.28,ease:"back.out(2)",immediateRender:false}},{t_15:.2f});tl.set("#kb1 .kb",{{opacity:0}},0);'
          + pop_js("#kk1", t_15) + pop_js("#kv1", t_15 + .1) + count_js("kv1n", t_15 + .1, 0, 750, 1.1)
          + f'tl.fromTo("#kb0 .ka",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.25,stagger:.28,ease:"back.out(2)",immediateRender:false}},{t_yari:.2f});tl.set("#kb0 .ka",{{opacity:0}},0);'
          + pop_js("#kk0", t_yari) + pop_js("#kv0", t_yari + .1) + count_js("kv0n", t_yari + .1, 0, 250, .7)
          + seq_js([("#kf1", t_15 + .2), ("#kf0", t_yari + .2)]))
SFX += [(t_15, "riser", .3)]

# 7) TARLA: imara girerken yol, park, okul için %45'e kadar bedelsiz kesinti (DOP)
iso7 = Iso(540, 640, 1.25)
rows = "".join(f'<path d="{iso7.d([(0, y, 0), (460, y, 0)])}" stroke="#5E8A3A" stroke-width="5" fill="none"/>' for y in range(20, 420, 34))
dop = (svg(BG + iso7.slab(0, 0, 460, 440, 26, "#8FB46A") + rows
           + '<g id="dpr">' + iso7.tile(0, 0, 460, 70, "#4A4C52") + iso7.road(0, 0, 460, 70) + '</g>'
           + '<g id="dpp">' + iso7.tile(0, 70, 150, 130, "#5E9A46") + iso7.tree(40, 110, .9) + iso7.tree(100, 160, .8) + '</g>'
           + '<g id="dpo">' + iso7.tile(0, 200, 150, 240, "#D9C9A8") + iso7.box(25, 260, 0, 100, 110, 44, "#E8B04A") + '</g>'
           + '<g id="dpk">' + iso7.tile(150, 70, 310, 370, "#C9A46A") + '</g>', "dpsvg")
       + tag("dpt", "TARLA → PARSELASYON", TOP)
       + lab("dpl0", "YOL", *iso7.label_pt(230, 35, 10)) + lab("dpl1", "PARK", *iso7.label_pt(75, 135, 30)) + lab("dpl2", "OKUL", *iso7.label_pt(75, 315, 70))
       + lab("dpl3", "KALAN PARSEL", *iso7.label_pt(305, 255, 10), "lab big")
       + tag("dpf", "≤ %45 BEDELSİZ KESİNTİ · DOP", LOW, "red"))
t_yol = A("yol, park")
JS.append(pop_js("#dpt", s("dop") + .1)
          + "".join(f'tl.fromTo("#{g}",{{opacity:0,y:-40}},{{opacity:1,y:0,duration:.3,ease:"back.out(2)",immediateRender:false}},{t:.2f});tl.set("#{g}",{{opacity:0}},0);' + pop_js(f"#dpl{i}", t + .1)
                    for i, (g, t) in enumerate([("dpr", t_yol), ("dpp", A("park")), ("dpo", A("okul"))]))
          + f'tl.fromTo("#dpk",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{A("yüzde kırk")-.1:.2f});tl.set("#dpk",{{opacity:0}},0);'
          + pop_js("#dpl3", A("yüzde kırk")) + pop_js("#dpf", A("bedelsiz")))
SFX += [(A("bedelsiz"), "pop", .35)]

# 8) GELİR YOLU: satış değeri − inşaat maliyeti − müteahhit kârı = arsa değeri (şelale)
BX, BY, BW = [165, 395, 625, 855], 1180, 160
H = 640


def bar(i, y0, y1, col, idn, txt):
    return (f'<g id="{idn}"><rect x="{BX[i] - BW/2 + 14}" y="{y0 + 14}" width="{BW}" height="{y1 - y0}" fill="#000" opacity=".3"/>'
            f'<rect x="{BX[i] - BW/2}" y="{y0}" width="{BW}" height="{y1 - y0}" rx="10" fill="{col}" stroke="#1B1414" stroke-width="5"/></g>'
            f'<text class="bt" x="{BX[i]}" y="{y1 + 52}" text-anchor="middle">{txt}</text>')


y_top, y_c, y_k = BY - H, BY - H + 220, BY - H + 220 + 160
gelir = (svg(BG + f'<line x1="70" y1="{BY}" x2="1010" y2="{BY}" stroke="#9FB4C8" stroke-width="4"/>'
             + bar(0, y_top, BY, GREEN, "wb0", "SATIŞ") + bar(1, y_top, y_c, RED, "wb1", "MALİYET")
             + bar(2, y_c, y_k, "#FF9A3C", "wb2", "KÂR") + bar(3, y_k, BY, GOLD, "wb3", "ARSAYA")
             + '<g id="gbld">' + Iso(BX[0] + 17, y_top - 100, .8).building(0, 0, 100, 150, 3, 34, "#E9E2D3", cls="gk") + '</g>'
             + "".join(f'<path class="gcn" id="gcn{i}" d="M{x0} {y} H{x1}" stroke="#9FB4C8" stroke-width="4" stroke-dasharray="10 8" opacity="0"/>' for i, (x0, y, x1) in enumerate([(BX[0]+BW/2, y_top, BX[1]-BW/2), (BX[1]+BW/2, y_c, BX[2]-BW/2), (BX[2]+BW/2, y_k, BX[3]-BW/2)])), "gsvg")
         + tag("gt", "PROJE HESABI (GELİR YOLU)", TOP)
         + '<div class="note" id="gnote" style="top:1300px;opacity:0">tutarlar bugüne indirgenmiş · örnek</div>'
         + f'<div class="op" id="gop1" style="left:{(BX[0]+BX[1])/2-30:.0f}px;top:{(y_top+y_c)/2-60:.0f}px;opacity:0">−</div><div class="op" id="gop2" style="left:{(BX[1]+BX[2])/2-30:.0f}px;top:{(y_c+y_k)/2-60:.0f}px;opacity:0">−</div><div class="op" id="gop3" style="left:{(BX[2]+BX[3])/2-30:.0f}px;top:{(y_k+BY)/2-60:.0f}px;opacity:0">=</div>')
t_sat, t_ins, t_kar, t_kal = A("projenin bugüne"), A("eksi maliyet"), A("yüklenici kârı"), A("kalan, arsaya")
JS.append(pop_js("#gt", s("gelir") + .1) + pop_js("#gnote", s("gelir") + .6) + grow_js("#wb0", s("gelir") + .35, .9, "power2.out") + "".join(f'tl.to("#gcn{i}",{{opacity:1,duration:.2}},{t:.2f});' for i, t in enumerate([t_ins, t_kar, t_kal]))
          + f'tl.fromTo("#wb1",{{y:-120,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"bounce.out",immediateRender:false}},{t_ins:.2f});tl.set("#wb1",{{opacity:0}},0);' + pop_js("#gop1", t_ins)
          + f'tl.fromTo("#wb2",{{y:-120,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"bounce.out",immediateRender:false}},{t_kar:.2f});tl.set("#wb2",{{opacity:0}},0);' + pop_js("#gop2", t_kar)
          + grow_js("#wb3", t_kal, .5) + pop_js("#gop3", t_kal) + punch_js("#gsvg", t_kal + .5, 1.04)
          + "".join(f'tl.fromTo(".bt:nth-of-type({i + 1})",{{opacity:0}},{{opacity:1,duration:.2,immediateRender:false}},{t:.2f});' for i, t in enumerate([s("gelir") + .6, t_ins, t_kar, t_kal]))
          + f'tl.fromTo("#gbld .gk",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.22,stagger:.18,ease:"back.out(2)",immediateRender:false}},{s("gelir") + 1.15:.2f});tl.set("#gbld .gk",{{opacity:0}},0);'
          + punch_js("#wb0", t_sat, 1.04) + punch_js("#gbld", t_sat, 1.12))
SFX += [(t_kal + .5, "ding", .35)]

# 9) GERÇEK RAPOR (Urla 2024): proje hesabı ≈807 milyon, benzer satışlar ≈665 milyon; ortalama yok, satışlar esas
UH = 600
uy0, uy1 = BY - UH, BY - UH * 665 / 807
urla = (svg(BG + f'<line x1="120" y1="{BY}" x2="960" y2="{BY}" stroke="#9FB4C8" stroke-width="4"/>'
            + f'<g id="ub0"><rect x="215" y="{uy0}" width="230" height="{UH}" rx="12" fill="{GOLD}" stroke="#1B1414" stroke-width="5"/></g>'
            + f'<g id="ub1"><rect x="635" y="{uy1:.0f}" width="230" height="{BY - uy1:.0f}" rx="12" fill="{BLUE}" stroke="#1B1414" stroke-width="5"/></g>', "usvg")
        + tag("ut", "GERÇEK RAPOR · URLA · 35 PARSEL", TOP)
        + f'<div class="uv" id="uv0" style="left:180px;top:{uy0 - 175:.0f}px;opacity:0">≈<b id="uv0n">0</b><small>milyon ₺</small></div>'
        + f'<div class="uv" id="uv1" style="left:600px;top:{uy1 - 175:.0f}px;opacity:0">≈<b id="uv1n">0</b><small>milyon ₺</small></div>'
        + f'<div class="ul" style="left:180px;top:{BY + 20}px">PROJE<br>HESABI</div><div class="ul" style="left:600px;top:{BY + 20}px">PAZAR<br>YOLU</div>'
        + '<div class="avg" id="uavg" style="opacity:0">ORTALAMA<div class="strike" id="ustk"></div></div>'
        + f'<div class="ok" id="uok" style="left:620px;top:{uy1 + 60:.0f}px;opacity:0">✓ NİHAİ DEĞER</div>')
t_807, t_665, t_ort, t_esas = A("sekiz yüz"), A("altı yüz"), A("ortalama"), A("pazar yolunu")
JS.append(pop_js("#ut", s("urla") + .1)
          + grow_js("#ub0", t_807 - .2, .6, "power2.out") + pop_js("#uv0", t_807) + count_js("uv0n", t_807, 0, 807, 1.0)
          + grow_js("#ub1", t_665 - .2, .6, "power2.out") + pop_js("#uv1", t_665) + count_js("uv1n", t_665, 0, 665, 1.0)
          + f'tl.set(".ul",{{opacity:0}},0);tl.to(".ul",{{opacity:1,duration:.25}},{t_807 - .2:.2f});'
          + pop_js("#uavg", t_ort) + f'tl.fromTo("#ustk",{{scaleX:0,transformOrigin:"0 50%"}},{{scaleX:1,duration:.25,immediateRender:false}},{t_ort+.45:.2f});tl.set("#ustk",{{scaleX:0}},0);'
          + f'tl.to("#uavg",{{opacity:0,duration:.2}},{t_esas-.2:.2f});tl.to("#ub0",{{opacity:.35,duration:.3}},{t_esas:.2f});tl.to("#uv0",{{opacity:.35,duration:.3}},{t_esas:.2f});'
          + pop_js("#uok", t_esas) + punch_js("#usvg", t_esas, 1.04))
SFX += [(t_ort + .45, "pop", .35), (t_esas, "ding", .4)]

# 10) MEĞERSE: iki arsaya geri dönüş, üstlerinde yapılabilecek binalar yükselir
m0 = A("Meğerse")
iso10 = Iso(493, 700, 1.2)
meg = (svg(BG + f'<g id="mg-d">{diorama(iso10, "mg", ghosts=True)}</g>', "mgsvg")
       + '<div class="megt" id="megt">MEĞERSE</div>'
       + tag("mgf", "EN VERİMLİ VE EN İYİ KULLANIM", LOW, "", "font-size:40px"))
t_yasal = A("yasal olarak")
JS.append(flash_js(m0, .9, .35) + f'tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out",immediateRender:false}},{m0+.05:.2f});tl.set("#megt",{{opacity:0}},0);'
          + f'tl.to("#megt",{{y:-450,scale:.62,duration:.5,ease:"power2.inOut"}},{A("arsanın değeri", m0):.2f});'
          + f'tl.fromTo("#mg-d",{{opacity:0,scale:1.1,transformOrigin:"540px 820px"}},{{opacity:1,scale:1,duration:.5,ease:"power2.out",immediateRender:false}},{A("arsanın değeri", m0):.2f});tl.set("#mg-d",{{opacity:0}},0);'
          + f'tl.fromTo("#mg-g0 .mgg0,#mg-g1 .mgg1",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.25,stagger:.22,ease:"back.out(2)",immediateRender:false}},{t_yasal:.2f});tl.set("#mg-g0 .mgg0,#mg-g1 .mgg1",{{opacity:0}},0);'
          + pop_js("#mgf", A("en verimli")))
SFX += [(m0 - 1.0, "riser", .6), (m0, "boom", .7)]

# İNTRO + OUTRO
JS.append(intro_js(s("intro")))
SFX += intro_sfx(s("intro"))
JS.append(outro_js(s("outro")))
SFX += outro_sfx(s("outro"))

HTML = dict(hook=hook, intro=intro_html("06"), rayic=rayic, yollar=yollar, emsal=emsal, imar=imar, kaks=kaks, dop=dop, gelir=gelir, urla=urla, meg=meg, outro=outro_html())
scenes_html = "".join(scene(k, HTML[k]) for k in keys)
js = "".join(f'tl.fromTo("#{k}-in",{{scale:1.08,opacity:0}},{{scale:1,opacity:1,duration:.22,ease:"power3.out",immediateRender:false}},{s(k)});' for k in keys if k not in ("hook", "intro"))
js += "".join(JS)

css = """
.tag { position:absolute; padding:14px 26px; border-radius:18px; font-weight:800; font-size:44px; background:#FFD23F; color:#111; box-shadow:0 8px 0 #000; }
.tag.c { left:0; right:0; margin:0 auto; width:fit-content; }
.tag.dark { background:rgba(10,14,22,.88); color:#fff; border:3px solid #fff; box-shadow:none; font-size:40px; }
.tag.red { background:#FF5A4E; color:#fff; }
.lab { position:absolute; width:600px; text-align:center; font-weight:800; font-size:38px; color:#fff; text-shadow:0 4px 0 #000, 0 0 16px rgba(0,0,0,.7); }
.lab.big { font-size:60px; color:#FFD23F; }
.pin { position:absolute; width:160px; padding:12px 0 10px; border-radius:20px; background:#fff; color:#141414; text-align:center; border:4px solid #1B1414; box-shadow:0 8px 0 rgba(0,0,0,.5); }
.pin b { display:block; font-weight:800; font-size:40px; } .pin i { font-style:normal; font-weight:600; font-size:22px; }
.pin:after { content:""; position:absolute; left:68px; bottom:-22px; border:12px solid transparent; border-top-color:#1B1414; }
.note { position:absolute; left:0; right:0; text-align:center; font-weight:600; font-size:30px; color:#9FB4C8; }
.doc { position:absolute; left:0; right:0; margin:0 auto; width:720px; height:300px; padding:30px 20px 40px; border-radius:22px; background:#F4EEDC; border:6px solid #1B1414; box-shadow:0 14px 0 rgba(0,0,0,.5); text-align:center; font-weight:800; font-size:52px; color:#1B1414; }
.doc small { display:block; font-weight:600; font-size:28px; letter-spacing:.12em; color:#6A5A3A; }
.stamp { position:absolute; left:90px; right:90px; top:170px; padding:8px 0; border:9px solid #E8423A; border-radius:16px; color:#E8423A; background:rgba(244,238,220,.85); font-size:50px; transform:rotate(-7deg); }
.mcard { position:absolute; top:480px; width:320px; height:560px; border-radius:30px; background:#16263A; border:5px solid #3A5A7A; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:22px; text-align:center; }
.mcard b { font-weight:800; font-size:46px; line-height:1.05; color:#fff; } .mcard span { font-weight:600; font-size:30px; color:#9FB4C8; }
.ecard { position:absolute; top:380px; width:310px; height:390px; border-radius:26px; background:#F4EEDC; border:5px solid #1B1414; box-shadow:0 12px 0 rgba(0,0,0,.45); text-align:center; color:#1B1414; }
.ecard small { display:block; margin-top:26px; font-weight:800; font-size:30px; letter-spacing:.08em; color:#6A5A3A; }
.ep { position:absolute; left:0; right:0; top:110px; font-weight:800; font-size:44px; line-height:1.2; } .ep i { font-style:normal; font-weight:600; font-size:34px; color:#6A5A3A; }
.em { position:absolute; left:0; right:0; top:110px; } .em b { display:block; font-weight:800; font-size:70px; } .em i { font-style:normal; font-weight:600; font-size:32px; color:#6A5A3A; }
.chip { position:absolute; left:20px; right:20px; bottom:26px; padding:10px 0; border-radius:16px; background:#1B1414; color:#fff; font-weight:800; font-size:30px; opacity:0; } .chip b { color:#FFD23F; }
.res { position:absolute; left:0; right:0; top:1110px; text-align:center; font-weight:800; font-size:70px; color:#fff; text-shadow:0 6px 0 #000; } .res b { color:#FFD23F; font-size:96px; }
.res small { display:block; font-weight:600; font-size:30px; color:#9FB4C8; text-shadow:none; }
.tapu { position:absolute; left:80px; top:400px; width:500px; padding:28px; border-radius:18px; background:#E9F0E2; border:5px solid #1B1414; font-weight:600; font-size:40px; color:#1B1414; transform:rotate(-5deg); }
.tapu small { display:block; font-weight:800; font-size:28px; letter-spacing:.14em; color:#4A6A3A; } .tapu b { font-weight:800; }
.nx { margin-top:10px; padding:6px 14px; width:fit-content; border-radius:12px; background:#FF5A4E; color:#fff; font-weight:800; font-size:34px; opacity:0; }
.idb { position:absolute; left:0; right:0; margin:0 auto; top:720px; width:920px; padding:30px 36px; border-radius:24px; background:#F4EEDC; border:6px solid #1B1414; box-shadow:0 14px 0 rgba(0,0,0,.45); color:#1B1414; }
.idb h3 { margin:0 0 18px; font-weight:800; font-size:46px; text-align:center; }
.row { display:flex; justify-content:space-between; padding:18px 22px; margin:10px 0; border-radius:14px; background:rgba(0,0,0,.06); font-size:44px; font-weight:600; } .row b { font-weight:800; }
.op { position:absolute; width:60px; text-align:center; font-weight:800; font-size:90px; color:#fff; text-shadow:0 6px 0 #000; }
.bt { font-family:Mont; font-weight:800; font-size:34px; fill:#fff; opacity:0; }
.uv { position:absolute; width:300px; text-align:center; font-weight:800; font-size:60px; color:#fff; text-shadow:0 6px 0 #000; } .uv b { font-size:100px; color:#FFD23F; } .uv small { display:block; font-size:32px; font-weight:600; }
#uv1 b { color:#5AB8FF; }
.ul { position:absolute; width:300px; text-align:center; font-weight:800; font-size:34px; line-height:1.1; color:#DDE6EE; opacity:0; }
.avg { position:absolute; left:0; right:0; margin:0 auto; top:292px; width:fit-content; padding:14px 30px; border-radius:40px; background:#fff; color:#141414; font-weight:800; font-size:46px; }
.strike { position:absolute; left:-10px; right:-10px; top:44%; height:12px; background:#FF5A4E; border-radius:6px; }
.ok { position:absolute; width:260px; padding:12px 0; border-radius:16px; background:#3FCB8E; border:4px solid #1B1414; text-align:center; font-weight:800; font-size:34px; color:#fff; }
.htitle { position:absolute; left:0; right:0; top:230px; text-align:center; font-weight:800; font-size:92px; line-height:1.05; color:#fff; text-shadow:0 8px 0 #000, 0 0 30px rgba(0,0,0,.6); opacity:0; }
.htitle span { color:#FFD23F; font-size:78px; }
.megt { position:absolute; left:0; right:0; top:700px; text-align:center; font-weight:800; font-size:200px; color:#FFD23F; -webkit-text-stroke:7px #000; paint-order:stroke fill; text-shadow:0 12px 0 #000; opacity:0; z-index:5; }
"""
DEFS = (DEFS2.replace("</defs>", "")
        + '<radialGradient id="bpbg" cx=".5" cy=".42" r=".8"><stop offset="0" stop-color="#16314D"/><stop offset="1" stop-color="#060B12"/></radialGradient>'
        + '<pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0 H0 V60" fill="none" stroke="#2C5378" stroke-width="1.5" opacity=".45"/></pattern></defs>')
html = page(words, [], scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="", voice_src=VOICE, extra_css=css + INTRO_CSS + OUTRO_CSS, defs=DEFS,
            avatar=False, chrome=False, caps="box", cap_top=L["cap_top"])
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(D / "sfx.json", "w"))
print("hf/index.html; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
