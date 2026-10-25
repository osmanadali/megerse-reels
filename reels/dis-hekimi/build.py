"""10 diş hekiminden 9'u reklamlarının perde arkası (Meğerse finalde + ayrı gönderme çağrısı). LAYOUT_V7, anlatıcı yok, az efekt, outro.

Marka kuralı (Osman): Colgate hiçbir yerde geçmez (Kolgate da yok); seslendirmede marka adı yok, ekrandaki tüpler taklit adlı (dentart.BRANDS).
Ses akışı (ses_isle.sh): ElevenLabs "Fatih Yıldırım" → tighten → atempo → align.py --text metin.txt → insert_gap (kancadan sonra intro)
         → reels/dis-hekimi/words.json + hf/assets/dis/voice.mp3 → build → sfx miksi → render hf/renders/dis-hekimi.mp4
Ses yokken yerleşim testi: DIS_GECICI=1 (metinden sahte kelime zamanları, sessiz ses; metin.txt yoksa metin-taslak.txt).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reels/dis-hekimi"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from reelkit2 import (HF, INTRO_CSS, INTRO_DUR, LAYOUT_V7, OUTRO_CSS, OUTRO_DUR, SHARE_CSS, anchor, flash_js, intro_html, intro_js,  # noqa: E402
                      intro_sfx, outro_html, outro_js, outro_sfx, page, share_cta_html, share_cta_js, share_cta_sfx)
import sahneler as S  # noqa: E402

D = ROOT / "reels/dis-hekimi"
GECICI = os.environ.get("DIS_GECICI") == "1"
METIN = D / ("metin.txt" if (D / "metin.txt").exists() else "metin-taslak.txt")
HOOK_END = "öneriyor?"
if GECICI:
    txt = METIN.read_text(encoding="utf-8").split()
    words, t = [], .3
    for w in txt:
        dur = .09 + len(w) * .055
        words.append({"text": w, "startMs": int(t * 1000), "endMs": int((t + dur) * 1000)})
        t += dur + (.22 if w[-1] in ".,;:?" else .04)
        if w == HOOK_END and len(words) < 12:
            t += INTRO_DUR + .15
    VOICE = "assets/dis/gecici.mp3"
    a = HF / "assets/dis"
    a.mkdir(parents=True, exist_ok=True)
    if not (a / "gecici.mp3").exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "120", str(a / "gecici.mp3")], check=True)
else:
    words = json.loads((D / "words.json").read_text(encoding="utf-8"))
    VOICE = "assets/dis/mix.mp3"

L = LAYOUT_V7
TOP, LOW = L["top_tag"], L["low_tag"]
HOOK_I = next(i for i, w in enumerate(words) if w["text"] == HOOK_END)
INTRO_T = round(words[HOOK_I]["endMs"] / 1000 + .1, 2)
A = lambda p, after=0.0: anchor(words, p, after)

# paylaşım çağrısı: düğme cümle başında, el + uçak cümle bitince → outro
T_CTA = A("Sen de bunu")
T_GO = round(words[-1]["endMs"] / 1000 + .15, 2)
CTA_JS, OUTRO_T, LAND_T = share_cta_js(T_CTA + .3, T_GO)
TOTAL = round(OUTRO_T + OUTRO_DUR, 2)
VOICE_END = round(words[-1]["endMs"] / 1000 + .3, 2)

T = {"hook": 0.0, "intro": INTRO_T, "afis": A("İngiltere,"), "anket": A("Ama telefon"), "dipnot": A("İki bin on altıda"), "yuzde": A("İki bin on sekizde"),
     "kurul": A("Türkiye'de"), "florur": A("Dünya Diş"), "meg": A("Meğerse"), "cta": T_CTA, "outro": OUTRO_T}
keys = list(T)
X = .3
S_ = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
s = lambda k: S_[k][0]


def win(k):
    a, b = S_[k]
    return a, round(b - a + (X if b < TOTAL else 0), 2)


def scene(k, inner, bg="radial-gradient(80% 55% at 50% 42%,#1E2A3C,#070A10)"):
    a, dd = win(k)
    return (f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{dd}" data-track-index="{1 + keys.index(k) % 2}">'
            f'<div class="fill" style="background:{bg}"></div><div class="fill" id="{k}-in">{inner}</div></div>')


def tag(idn, text, y=TOP, cls="", style=""):
    return f'<div class="tag c {cls}" id="{idn}" style="top:{y}px;opacity:0;{style}">{text}</div>'


JS, SFX = [], []
pop = S.pop_js

# 1) KANCA: reklam çekimi (vizör) → kamera geri çekilir, set ortaya çıkar → yıldız işareti
hook = S.hook_html()
JS.append(S.hook_js(0, A("gerçekten"), A("macunu")))
SFX += [(A("gerçekten") + .1, "whoosh", .35)]

# 2) İNTRO
JS.append(intro_js(s("intro")))
SFX += intro_sfx(s("intro"))

# 3) AFİŞ: İngiltere 2007, "%80+"
afis = S.afis_html()
JS.append(S.afis_js(s("afis"), t_count=A("yüzde sekseninden")))

# 4) ANKET: çoklu seçim → iki çubuk neredeyse eşit → YANILTICI
anket = (S.anket_html(note="(birden fazla marka söyleyebilirsiniz)") + '<div class="stamp3" id="ast2" style="top:1060px">YANILTICI</div>'
         + tag("atag", "☎ TELEFON ANKETİ", TOP, "dark"))
t_yan = A("yanıltıcı", s("anket"))
JS.append(pop("#atag", s("anket") + .1) + S.anket_js(s("anket"), A("birden fazla"), A("marka söyleyebiliyordu"), A("bir rakip"))
          + f'tl.to("#atag",{{opacity:0,duration:.2}},{A("bir rakip") - .1:.2f});'
          + f'tl.fromTo("#ast2",{{scale:2.8,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t_yan:.2f});tl.set("#ast2",{{opacity:0}},0);')
SFX += [(t_yan + .2, "boom", .35)]

# 6) %22: 100 hekim, 22'si yanar, #1 madalya
cam2 = Cam(horizon=300, vpx=480, f=1000, eye=170, sun=(-1, -.4), alt=46, haze="#2A3446", zfar=4200)
crs, crowd = S.crowd_html(cam2)
yuzde = (crowd + tag("ytag", "İNGİLTERE · 2018 · ŞARJLI DİŞ FIRÇASI", TOP, "dark") + '<div class="stamp3 ok" id="ykab" style="top:1000px">KABUL EDİLDİ</div>' + '<div id="medal" style="top:300px">#1<small>DİŞ HEKİMİ TAVSİYESİ</small></div>'
         + '<div id="pct">yalnızca <b>%22</b></div>')
y0, y1 = S_["yuzde"]
JS.append(pop("#ytag", y0 + .1) + S.crowd_js(crs, y0, round(y1 - y0 + X, 2), A("Ankette onu"))
          + pop("#medal", A("bir numaralı"), .2, .45) + f'tl.fromTo("#medal",{{rotationY:-180}},{{rotationY:0,duration:.6,ease:"back.out(1.6)",immediateRender:false}},{A("bir numaralı"):.2f});'
          + f'tl.fromTo("#ykab",{{scale:2.6,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{A("kabul edildi"):.2f});tl.set("#ykab",{{opacity:0}},0);'
          + f'tl.to("#ykab",{{opacity:0,duration:.2}},{A("Ankette") + .2:.2f});'
          + pop("#pct", A("yüzde yirmi")))
SFX += [(A("bir numaralı") + .1, "ding", .3)]

# 7) KURUL: tokmak, KANITLANAMADI, 81.554 TL
kurul = (S.kurul_html(claim="Hassas dişler için<br>10 diş hekiminden") + tag("ktag", "TÜRKİYE · REKLAM KURULU · 2014", TOP, "dark")
         + '<div class="stamp2" id="kst2" style="top:860px;font-size:44px;transform:rotate(5deg)">ALTYAZI OKUNMUYOR</div>')
JS.append(pop("#ktag", s("kurul") + .1) + S.kurul_js(s("kurul"), A("kanıtlanamadığı"), A("durdurdu", s("kurul")))
          + f'tl.fromTo("#kst2",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{A("altyazı"):.2f});tl.set("#kst2",{{opacity:0}},0);')
SFX += [(A("altyazı") + .2, "pop", .3)]
SFX += [(A("kanıtlanamadığı"), "boom", .5)]

# 5) DİPNOT: 2016 ara yüz fırçası "%100'ü öneriyor*" → büyüteç: fuarlarda sorulan 46 kişi → YANILTICI
dip = (S.dipnot_html(big_top="DİŞ PROFESYONELLERİNİN", big="%100'Ü", big_bot="ÖNERİYOR*", big_size=150, top_size=64, fine="*Fuar listesinden 46 kişiye: önerir miydiniz?",
                     fine_big="*Fuar listesinden <b>46 kişiye</b><br>“önerir miydiniz?”") + tag("dtag2", "İNGİLTERE · 2016 · ARA YÜZ FIRÇASI", TOP, "dark")
       + '<div class="stamp3" id="ast3" style="top:640px">YANILTICI</div>')
t_yan2 = A("o da yanıltıcı")
JS.append(pop("#dtag2", s("dipnot") + .1) + S.dipnot_js(s("dipnot"), A("Dayanak"), A("kırk altı"))
          + f'tl.fromTo("#ast3",{{scale:2.8,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t_yan2 + .2:.2f});tl.set("#ast3",{{opacity:0}},0);')
SFX += [(t_yan2 + .4, "boom", .3)]

# 8) FLORÜR: ağız içi dalış, mine parlar
cam = Cam(horizon=403, vpx=480, f=1000, eye=165, sun=(-1, -.4), alt=46, haze="#7A2A3A", zfar=4000)
sc, flor = S.florur_html(cam, (("fl1", "MARKA <b>YOK</b>", 260), ("fl2", "günde <b>2</b> kez", 1180), ("fl3", "<b>florürlü</b> macun", 1180)))
flor += tag("ftag", "DÜNYA DİŞ HEKİMLERİ FEDERASYONU", TOP, "dark")
flor = flor.replace('günde <b>2</b> kez', 'günde <b>2</b> kez · yaşa uygun')
f0, f1 = s("florur"), S_["florur"][1]
JS.append(pop("#ftag", A("Dünya", f0)) + f'tl.to("#ftag",{{opacity:0,duration:.2}},{A("marka yok", f0) - .15:.2f});'
          + S.florur_js(sc, f0, round(f1 - f0 + X, 2), A("florürlü", f0), (A("marka yok", f0), A("günde", f0), A("florürlü", f0))))

# 9) MEĞERSE: reklam cümlesinin anlamı → tüpler FLORÜR olur
m0 = s("meg")
meg = S.meg_html()
JS.append(flash_js(m0, .9, .35) + S.meg_js(m0, A("o yüzdeler", m0), A("en iyisi", m0), A("önerdiklerimden", m0), A("Asıl", m0), A("içerikmiş", m0)))
SFX += [(m0 - 1.0, "riser", .5), (m0, "boom", .6)]

# 10) ÇAĞRI: 10 hekim, 9'u söner, 10.'su parlar + GÖNDER → uçak outro'ya
cta = S.cta_html()
JS.append(S.cta_js(s("cta"), A("dokuzdan", s("cta")), s("cta") + .2) + CTA_JS)
SFX += share_cta_sfx(T_GO, LAND_T)

# OUTRO
JS.append(outro_js(s("outro"), land_t=LAND_T))
SFX += outro_sfx(s("outro"))

HTML = dict(hook=hook, intro=intro_html("07"), afis=afis, anket=anket, yuzde=yuzde, kurul=kurul, dipnot=dip, florur=flor, meg=meg, cta=cta,
            outro=outro_html(label3="GÖNDER", fixed_icons=True))
BG = dict(hook="#0B0E14", florur="#3A0E18", meg="radial-gradient(80% 55% at 50% 40%,#2A2440,#08060E)")
scenes_html = "".join(scene(k, HTML[k], BG.get(k, "radial-gradient(80% 55% at 50% 42%,#1E2A3C,#070A10)")) for k in keys) + share_cta_html()

# geçiş: yeni sahne hafif büyükten oturur (kamera itişi), ardından süre boyunca yavaş yakınlaşma; eskisi geri çekilip söner
js = ""
for i, k in enumerate(keys):
    a, dd = win(k)
    if k not in ("hook", "intro", "outro"):
        js += (f'tl.fromTo("#{k}-in",{{scale:1.12,opacity:0,filter:"blur(10px)"}},{{scale:1,opacity:1,filter:"blur(0px)",duration:.35,ease:"power3.out",immediateRender:false}},{a:.2f});'
               f'tl.to("#{k}-in",{{scale:1.035,duration:{max(.1, dd - .7):.2f},ease:"none"}},{a + .35:.2f});')
    if i + 1 < len(keys) and keys[i + 1] not in ("intro", "outro") and k != "intro":
        js += f'tl.to("#{k}-in",{{scale:.94,opacity:0,duration:{X:.2f},ease:"power2.in"}},{T[keys[i + 1]]:.2f});'
js += f'tl.fromTo("#outro-in",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{s("outro"):.2f});'
js += "".join(JS)

css = """
.tag { position:absolute; padding:14px 26px; border-radius:18px; font-weight:800; font-size:44px; background:#FFD23F; color:#111; box-shadow:0 8px 0 #000; }
.tag.c { left:0; right:0; margin:0 auto; width:fit-content; }
.tag.dark { background:rgba(10,14,22,.88); color:#fff; border:3px solid #fff; box-shadow:none; font-size:38px; }
.stamp3.ok { border-color:#2FB36E; color:#2FB36E; font-size:66px; }
""" + S.CSS + S.CTA_CSS + S.ANKET_CSS + S.YUZ_CSS + S.KURUL_CSS + S.DIP_CSS + S.AFIS_CSS + S.FLOR_CSS + S.MEG_CSS
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"   # atm süzgeçleri iki kamera için ortak (pus rengi ilk kameradan)
html = page(words, [], scenes_html, js, total=TOTAL, voice_end=VOICE_END, title="", voice_src=VOICE, extra_css=css + INTRO_CSS + OUTRO_CSS + SHARE_CSS, defs=DEFS,
            avatar=False, chrome=False, caps="box", cap_top=L["cap_top"])
(HF / "index.html").write_text(html, encoding="utf-8")
json.dump(sorted(SFX), open(D / "sfx.json", "w"))
print("hf/index.html; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S_.items()})
