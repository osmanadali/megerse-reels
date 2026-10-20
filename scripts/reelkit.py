"""Reel kompozisyonları için ortak parçalar: sayfa iskeleti, avatar, balon altyazı, ağız/göz kırpma.

Kullanım (reels/<id>/build.py içinde):
    from reelkit import page, anchor
    html = page(words, mouth, scenes_html, scenes_js, total=..., voice_end=..., kicker=..., title=..., voice_src=...)
"""
import json
from pathlib import Path

HF = Path(__file__).resolve().parents[1] / "hf"


def anchor(words, phrase, after=0.0):
    """metindeki ifadenin ilk kelimesinin başlangıç saniyesi (after'dan sonra ilk eşleşme)."""
    toks = phrase.lower().split()
    for i in range(len(words) - len(toks) + 1):
        if words[i]["startMs"] / 1000 < after:
            continue
        if all(words[i + k]["text"].lower().strip(".,…:'’\"") .startswith(t.strip(".,…:'’\"")) for k, t in enumerate(toks)):
            return words[i]["startMs"] / 1000
    raise ValueError(f"bulunamadı: {phrase}")


def captions(words):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or w["text"][-1] in ".,…?!:":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    html, js = [], []
    for ci, ch in enumerate(chunks):
        a = ch[0]["startMs"] / 1000
        b = chunks[ci + 1][0]["startMs"] / 1000 if ci + 1 < len(chunks) else ch[-1]["endMs"] / 1000 + 0.4
        spans = " ".join(f'<span id="w{ci}_{wi}">{w["text"]}</span>' for wi, w in enumerate(ch))
        html.append(f'<div class="cap" id="c{ci}"><div>{spans}</div></div>')
        js.append(f'tl.set("#c{ci}",{{opacity:1}},{a:.2f});tl.set("#c{ci}",{{opacity:0}},{b:.2f});')
        js += [f'tl.set("#w{ci}_{wi}",{{color:"#F5B82E"}},{w["startMs"]/1000:.2f});' for wi, w in enumerate(ch)]
    return "".join(html), "".join(js)


def avatar_js(mouth, voice_end):
    ev, prev = [], None
    for i, m in enumerate(mouth):
        if m != prev:
            ev.append(f"[{i/30:.3f},{m}]")
            prev = m
    blinks = "".join(f'tl.set("#av",{{attr:{{"data-b":"1"}}}},{t+.05:.2f});tl.set("#av",{{attr:{{"data-b":"0"}}}},{t+.18:.2f});' for t in range(2, int(voice_end), 4))
    return (f'tl.to("#av #head",{{rotation:1.6,y:-3,transformOrigin:"50% 80%",duration:1.3,yoyo:true,repeat:{int(voice_end/1.3)},ease:"sine.inOut"}},0);'
            + blinks + f'[{",".join(ev)}].forEach(([t,m])=>tl.set("#av",{{attr:{{"data-m":String(m)}}}},t));tl.set("#av",{{attr:{{"data-m":"0"}}}},{voice_end});')


CSS = """
@font-face { font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-800-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }
@font-face { font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-ext-800-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }
@font-face { font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-600-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }
@font-face { font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-ext-600-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0B1220; }
#root { position: relative; width: 100%; height: 100%; font-family: "Mont", sans-serif; color: #F4F1EA; background: radial-gradient(120% 70% at 50% 0%, var(--glow, #17304A) 0%, #0B1220 60%); }
.grid { position: absolute; inset: 0; opacity: .07; background-image: linear-gradient(#9FC3E6 1px, transparent 1px), linear-gradient(90deg, #9FC3E6 1px, transparent 1px); background-size: 54px 54px; }
#kicker { position: absolute; left: 60px; top: 92px; font-weight: 600; font-size: 30px; letter-spacing: .14em; color: #9FB4CC; }
#kicker b { color: #E8524A; font-weight: 800; }
#title { position: absolute; left: 60px; top: 150px; padding: 16px 28px; background: #F4F1EA; color: #0B1220; border-radius: 18px; font-weight: 800; font-size: 46px; box-shadow: 0 8px 0 #E8524A; }
#panel { position: absolute; left: 60px; top: 270px; width: 960px; height: 1080px; border-radius: 36px; overflow: hidden; border: 8px solid #F4F1EA; background: #06101C; }
.scene { position: absolute; inset: 0; }
.fill { position: absolute; inset: 0; }
.fill > img, .fill > video { width: 100%; height: 100%; object-fit: cover; display: block; }
.vign { position: absolute; inset: 0; background: radial-gradient(70% 60% at 50% 45%, transparent 40%, rgba(0,0,0,.7) 100%); }
.chip { position: absolute; left: 36px; bottom: 36px; padding: 12px 22px; border-radius: 14px; background: rgba(6,16,28,.82); border: 3px solid #F4F1EA; font-weight: 800; font-size: 34px; letter-spacing: .02em; }
.chip.red { background: #E8524A; border-color: #E8524A; color: #fff; }
.chip.top { top: 36px; bottom: auto; }
#avatarbox { position: absolute; left: 44px; top: 1420px; width: 330px; height: 330px; }
#avatarbox svg { width: 100%; height: 100%; display: block; }
#av #mouth-0, #av #mouth-1, #av #mouth-2, #av #mouth-3, #av #eyes-closed { display: none; }
#av[data-m="0"] #mouth-0, #av[data-m="1"] #mouth-1, #av[data-m="2"] #mouth-2, #av[data-m="3"] #mouth-3 { display: inline; }
#av[data-b="1"] #eyes-open { display: none; }
#av[data-b="1"] #eyes-closed { display: inline; }
#bubble { position: absolute; left: 400px; top: 1452px; width: 636px; height: 266px; border-radius: 30px; background: #111A28; border: 6px solid #F4F1EA; }
#bubble::before { content: ""; position: absolute; left: -30px; top: 104px; border: 22px solid transparent; border-right: 30px solid #F4F1EA; border-left: 0; }
.cap { position: absolute; inset: 0; padding: 30px 36px; display: flex; align-items: center; font-weight: 800; font-size: 54px; line-height: 1.15; opacity: 0; color: #F4F1EA; }
#handle { position: absolute; right: 60px; top: 1790px; font-weight: 600; font-size: 30px; color: #6F86A0; letter-spacing: .06em; }
.big { position: absolute; left: 0; right: 0; text-align: center; font-weight: 800; }
.src { font-weight: 600; font-size: 34px; line-height: 1.5; color: #C9D6E4; }
"""


def component(name):
    return (HF / f"compositions/components/{name}.html").read_text(encoding="utf-8")


def page(words, mouth, scenes_html, scenes_js, *, total, voice_end, kicker, title, voice_src, extra_css="", glow="#17304A", fx=False, defs=""):
    """fx=True: sahne alanına film greni + data-hf-motion-blur işaretli öğelere motion blur."""
    grain = component("grain-overlay").replace("opacity: 0.15;", "opacity: 0.09;") if fx else ""
    mblur = component("motion-blur") if fx else ""
    svg = (HF / "avatar/osman.svg").read_text(encoding="utf-8").replace("<svg ", '<svg id="av" data-m="0" data-b="0" ', 1)
    cap_html, cap_js = captions(words)
    return f"""<!doctype html>
<html lang="tr" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}{extra_css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920" style="--glow:{glow}">
  <div class="grid"></div>
  <div id="kicker">{kicker}</div>
  <div id="title">{title}</div>
  <audio id="vo" src="{voice_src}" data-start="0" data-duration="{voice_end}" data-track-index="9" data-volume="1"></audio>
  <div id="panel"><svg width="0" height="0" style="position:absolute" aria-hidden="true">{defs}</svg>{scenes_html}{grain}</div>
  <div id="avatarbox">{svg}</div>
  <div id="bubble">{cap_html}</div>
  <div id="handle">@megerse.tr</div>
</div>
{mblur}
<script>
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#title",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.6)"}},.1);
tl.fromTo("#avatarbox",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(1.8)"}},0);
tl.fromTo("#bubble",{{x:-30,opacity:0}},{{x:0,opacity:1,duration:.4}},.15);
{scenes_js}
{avatar_js(mouth, voice_end)}
{cap_js}
tl.set({{}}, {{}}, {total});
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
