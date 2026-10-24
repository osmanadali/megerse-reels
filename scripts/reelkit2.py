"""v5 sayfa teması: tam ekran 9:16 sinematik (panel/çerçeve yok).

Öğeler: sahneler tüm ekranı kaplar; üstte ilerleme çubuğu + küçük başlık; ortada kinetik altyazı
(2-3 kelimelik parçalar, etkin kelime büyür ve sarıya döner); sol altta yuvarlak avatar (sesle nabız atan halka);
film greni + vinyet; sahne geçişleri için flaş ve hızlı yakınlaşma yardımcıları.
Güvenli alan: Instagram arayüzü alt ~320 px ve sağ ~140 px'i örter → altyazı 1080-1380, avatar sol 1330-1560.
"""
import json

from reelkit import HF, anchor, avatar_js, component  # noqa: F401  (anchor dışa aktarılır)

CSS = """
@font-face { font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-800-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }
@font-face { font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-ext-800-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }
@font-face { font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-600-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }
@font-face { font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-ext-600-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
#root { position: relative; width: 100%; height: 100%; font-family: "Mont", sans-serif; color: #fff; overflow: hidden; background: #000; }
#stage { position: absolute; inset: 0; overflow: hidden; }
.scene { position: absolute; inset: 0; }
.fill { position: absolute; inset: 0; }
.fill > svg { width: 100%; height: 100%; display: block; }
#vign { position: absolute; inset: 0; pointer-events: none; background: radial-gradient(85% 60% at 50% 42%, transparent 55%, rgba(0,0,0,.55) 100%), linear-gradient(180deg, rgba(0,0,0,.45) 0%, transparent 14%, transparent 52%, rgba(0,0,0,.55) 78%, rgba(0,0,0,.75) 100%); }
#flash { position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; }
#prog { position: absolute; left: 0; top: 0; height: 10px; width: 1080px; background: rgba(255,255,255,.18); }
#progf { position: absolute; left: 0; top: 0; height: 10px; width: 1080px; background: linear-gradient(90deg, #FFD23F, #FF6B3D); transform-origin: 0 50%; transform: scaleX(0); }
#tchip { position: absolute; left: 44px; top: 70px; padding: 12px 22px; border-radius: 16px; background: rgba(10,10,14,.72); border: 3px solid rgba(255,255,255,.85); font-weight: 800; font-size: 34px; letter-spacing: .02em; }
#tchip b { color: #FFD23F; }
#handle { position: absolute; right: 44px; top: 84px; font-weight: 600; font-size: 30px; color: rgba(255,255,255,.8); }
.cap { position: absolute; left: 70px; right: 70px; top: 1090px; height: 300px; display: flex; flex-wrap: wrap; align-content: center; justify-content: center; gap: 0 22px; text-align: center; opacity: 0;
  font-weight: 800; font-size: 86px; line-height: 1.08; color: #fff; text-transform: uppercase;
  text-shadow: 0 6px 0 #000, 0 0 24px rgba(0,0,0,.65); -webkit-text-stroke: 3px #000; paint-order: stroke fill; }
.cap span { display: inline-block; }
.cap span.hot { color: #FFD23F; }
#avwrap { position: absolute; left: 40px; top: 1360px; width: 230px; height: 230px; }
#avring { position: absolute; inset: -10px; border-radius: 50%; border: 8px solid #FFD23F; }
#avbox { position: absolute; inset: 0; border-radius: 50%; overflow: hidden; background: #F2ECE1; box-shadow: 0 10px 30px rgba(0,0,0,.6); }
#avbox svg { width: 112%; height: 112%; margin: -6% 0 0 -6%; display: block; }
#av #mouth-0, #av #mouth-1, #av #mouth-2, #av #mouth-3, #av #eyes-closed { display: none; }
#av[data-m="0"] #mouth-0, #av[data-m="1"] #mouth-1, #av[data-m="2"] #mouth-2, #av[data-m="3"] #mouth-3 { display: inline; }
#av[data-b="1"] #eyes-open { display: none; }
#av[data-b="1"] #eyes-closed { display: inline; }
.big { position: absolute; left: 0; right: 0; text-align: center; font-weight: 800; text-shadow: 0 8px 0 #000; -webkit-text-stroke: 4px #000; paint-order: stroke fill; }
.tag { position: absolute; padding: 14px 24px; border-radius: 18px; font-weight: 800; font-size: 44px; background: #FFD23F; color: #111; box-shadow: 0 8px 0 #000; }
.tag.red { background: #FF4D4D; color: #fff; } .tag.dark { background: rgba(10,10,14,.85); color: #fff; border: 3px solid #fff; box-shadow: none; }
.src { font-weight: 600; font-size: 34px; line-height: 1.55; color: #D9DEE8; }
"""


def captions_kinetic(words, per=3):
    """2-3 kelimelik parçalar; noktalama parçayı böler. Etkin kelime 'hot' olur ve küçük bir zıplama yapar."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= per or w["text"][-1] in ".,…?!:;":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    html, js = [], []
    for ci, ch in enumerate(chunks):
        a = ch[0]["startMs"] / 1000
        b = chunks[ci + 1][0]["startMs"] / 1000 if ci + 1 < len(chunks) else ch[-1]["endMs"] / 1000 + .4
        spans = "".join(f'<span id="k{ci}_{wi}">{w["text"]}</span>' for wi, w in enumerate(ch))
        html.append(f'<div class="cap" id="k{ci}">{spans}</div>')
        js.append(f'tl.set("#k{ci}",{{opacity:1}},{a:.2f});tl.fromTo("#k{ci}",{{scale:.82,y:24}},{{scale:1,y:0,duration:.16,ease:"back.out(3)"}},{a:.2f});tl.set("#k{ci}",{{opacity:0}},{b:.2f});')
        for wi, w in enumerate(ch):
            t = w["startMs"] / 1000
            js.append(f'tl.set("#k{ci}_{wi}",{{color:"#FFD23F"}},{t:.2f});tl.fromTo("#k{ci}_{wi}",{{scale:1.18}},{{scale:1,duration:.18,ease:"power2.out"}},{t:.2f});')
            if wi + 1 < len(ch):
                js.append(f'tl.set("#k{ci}_{wi}",{{color:"#FFFFFF"}},{ch[wi+1]["startMs"]/1000:.2f});')
    return "".join(html), "".join(js)


def ring_js(mouth, voice_end):
    """avatar halkası sesle nabız atar (ağız seviyesinden)."""
    ev, prev = [], None
    for i, m in enumerate(mouth):
        if m != prev:
            ev.append(f"[{i/30:.3f},{m}]")
            prev = m
    return (f'[{",".join(ev)}].forEach(([t,m])=>tl.set("#avring",{{scale:1+m*.035,opacity:.55+m*.15}},t));'
            f'tl.set("#avring",{{scale:1,opacity:.5}},{voice_end});')


def page(words, mouth, scenes_html, scenes_js, *, total, voice_end, title, voice_src, extra_css="", defs="", grain=True):
    svg = (HF / "avatar/osman.svg").read_text(encoding="utf-8").replace("<svg ", '<svg id="av" data-m="0" data-b="0" ', 1)
    cap_html, cap_js = captions_kinetic(words)
    g = component("grain-overlay").replace("opacity: 0.15;", "opacity: 0.08;") if grain else ""
    mblur = component("motion-blur")
    return f"""<!doctype html>
<html lang="tr" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{CSS}{extra_css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
  <audio id="vo" src="{voice_src}" data-start="0" data-duration="{total}" data-track-index="9" data-volume="1"></audio>
  <div id="stage"><svg width="0" height="0" style="position:absolute" aria-hidden="true">{defs}</svg>{scenes_html}</div>
  <div id="vign"></div>{g}
  <div id="flash"></div>
  <div id="prog"><div id="progf"></div></div>
  <div id="tchip">{title}</div><div id="handle">@megerse.tr</div>
  {cap_html}
  <div id="avwrap"><div id="avring"></div><div id="avbox">{svg}</div></div>
</div>
{mblur}
<script>
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#progf",{{scaleX:0}},{{scaleX:1,duration:{voice_end},ease:"none"}},0);
tl.fromTo("#avwrap",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},.2);
tl.fromTo("#tchip",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.4,ease:"back.out(2)"}},.3);
{scenes_js}
{avatar_js(mouth, voice_end)}
{ring_js(mouth, voice_end)}
{cap_js}
tl.set({{}}, {{}}, {total});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""


def flash_js(t, peak=.85, dur=.25):
    return f'tl.fromTo("#flash",{{opacity:{peak}}},{{opacity:0,duration:{dur},ease:"power2.out"}},{t:.2f});'


def punch_js(sel, t, s=1.08, dur=.35):
    """vuruş anında hızlı yakınlaşma (zoom punch)."""
    return f'tl.fromTo("{sel}",{{scale:{s}}},{{scale:1,duration:{dur},ease:"power3.out"}},{t:.2f});'


def shake_js(sel, t, amp=14, n=8):
    return f'tl.fromTo("{sel}",{{x:-{amp}}},{{x:{amp},duration:.04,repeat:{n},yoyo:true,ease:"none"}},{t:.2f});tl.set("{sel}",{{x:0}},{t+.04*(n+1):.2f});'
