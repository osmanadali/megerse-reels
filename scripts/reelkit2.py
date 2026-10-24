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
.cap { position: absolute; left: 60px; right: 60px; top: 1010px; height: 300px; display: flex; flex-wrap: wrap; align-content: center; justify-content: center; gap: 0 34px; text-align: center; opacity: 0;
  font-weight: 800; font-size: 86px; line-height: 1.08; color: #fff; text-transform: uppercase;
  text-shadow: 0 6px 0 #000, 0 0 24px rgba(0,0,0,.65); -webkit-text-stroke: 3px #000; paint-order: stroke fill; }
.cap span { display: inline-block; margin: 0 .16em; }
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
            js.append(f'tl.set("#k{ci}_{wi}",{{color:"#FFD23F"}},{t:.2f});tl.fromTo("#k{ci}_{wi}",{{scale:1.1}},{{scale:1,duration:.16,ease:"power2.out",immediateRender:false}},{t:.2f});')
            if wi + 1 < len(ch):
                js.append(f'tl.set("#k{ci}_{wi}",{{color:"#FFFFFF"}},{ch[wi+1]["startMs"]/1000:.2f});')
    return "".join(html), "".join(js)


CAP6_CSS = """
#capbg { position: absolute; left: 0; right: 0; top: CAPBG_TOPpx; height: 460px; pointer-events: none; background: linear-gradient(180deg, transparent, rgba(0,0,0,.42) 28%, rgba(0,0,0,.42) 72%, transparent); }
.cap6 { position: absolute; left: 70px; right: 70px; top: CAP_TOPpx; height: 250px; display: flex; flex-wrap: wrap; align-content: center; justify-content: center; gap: 8px 0; text-align: center; opacity: 0;
  font-weight: 800; font-size: 76px; line-height: 1.1; color: #fff; text-transform: uppercase; letter-spacing: .01em; text-shadow: 0 4px 0 rgba(0,0,0,.85), 0 0 26px rgba(0,0,0,.7); }
.cap6 span { display: inline-block; margin: 0 .1em; padding: .03em .17em .05em; border-radius: 18px; }
"""
SH6 = "0 4px 0 rgba(0,0,0,.85), 0 0 26px rgba(0,0,0,.7)"
# Instagram güvenli alan: üstte "Reels / Arkadaşlar" sekmesi (~0-250), altta kullanıcı adı/açıklama (~1600+).
# cap_top=1250: beyaz saç v2 (eski); arsa reeli ve sonrası LAYOUT_V7 (görsel alan 250-1390, altyazı 1400-1650, ortalı;
# son kelime sağ düğmelerin altına girebilir, Osman: ortalılık daha önemli).
LAYOUT_V7 = dict(cap_top=1400, top_tag=250, low_tag=1290, vis=(250, 1390))
VIGN_V7 = "#vign { background: radial-gradient(85% 60% at 50% 46%, transparent 55%, rgba(0,0,0,.5) 100%), linear-gradient(180deg, rgba(0,0,0,.55) 0%, transparent 12%, transparent 70%, rgba(0,0,0,.45) 84%, rgba(0,0,0,.7) 100%); }\n"


def captions_box(words, per=3, maxc=17):
    """v6 altyazı: 2-3 kelime (≤ maxc harf); etkin kelime sarı yuvarlak kutuya girer, hafif eğik zıplar."""
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= per or sum(len(x["text"]) for x in cur) + len(w["text"]) > maxc):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if w["text"][-1] in ".,…?!:;":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    html, js = [], []
    on = '{backgroundColor:"#FFD23F",color:"#141414",textShadow:"none"}'
    off = f'{{backgroundColor:"rgba(255,210,63,0)",color:"#FFFFFF",textShadow:"{SH6}",rotation:0}}'
    for ci, ch in enumerate(chunks):
        a = ch[0]["startMs"] / 1000
        b = chunks[ci + 1][0]["startMs"] / 1000 if ci + 1 < len(chunks) else ch[-1]["endMs"] / 1000 + .4
        b = min(b, ch[-1]["endMs"] / 1000 + .9)          # uzun suskunlukta ekranda asılı kalmasın
        spans = "".join(f'<span id="k{ci}_{wi}">{w["text"].rstrip(".,;:")}</span>' for wi, w in enumerate(ch))
        html.append(f'<div class="cap6" id="k{ci}">{spans}</div>')
        js.append(f'tl.set("#k{ci}",{{opacity:1}},{a:.2f});tl.fromTo("#k{ci}",{{y:34,opacity:0,scale:.92}},{{y:0,opacity:1,scale:1,duration:.18,ease:"back.out(2.2)",immediateRender:false}},{a:.2f});tl.set("#k{ci}",{{opacity:0}},{b:.2f});')
        for wi, w in enumerate(ch):
            t = w["startMs"] / 1000
            js.append(f'tl.set("#k{ci}_{wi}",{on},{t:.2f});tl.fromTo("#k{ci}_{wi}",{{scale:1.16,rotation:-5}},{{scale:1,rotation:-2,duration:.18,ease:"back.out(3)",immediateRender:false}},{t:.2f});')
            if wi + 1 < len(ch):
                js.append(f'tl.set("#k{ci}_{wi}",{off},{ch[wi+1]["startMs"]/1000:.2f});')
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


def page(words, mouth, scenes_html, scenes_js, *, total, voice_end, title, voice_src, extra_css="", defs="", grain=True, avatar=True, chrome=True, caps="kinetic", cap_top=1250):
    """avatar=False: anlatıcı yok (ekran tamamen sahneye); chrome=False: başlık çipi ve kanal adı yok; caps="box": v6 altyazı."""
    svg = (HF / "avatar/osman.svg").read_text(encoding="utf-8").replace("<svg ", '<svg id="av" data-m="0" data-b="0" ', 1)
    cap_html, cap_js = captions_box(words) if caps == "box" else captions_kinetic(words)
    if caps == "box":
        extra_css = CAP6_CSS.replace("CAPBG_TOP", str(cap_top - 80)).replace("CAP_TOP", str(cap_top)) + (VIGN_V7 if cap_top >= 1400 else "") + extra_css
        cap_html = '<div id="capbg"></div>' + cap_html
    av_html = f'<div id="avwrap"><div id="avring"></div><div id="avbox">{svg}</div></div>' if avatar else ""
    av_js = (f'tl.fromTo("#avwrap",{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:.4,ease:"back.out(2)"}},.2);\n'
             f'{avatar_js(mouth, voice_end)}\n{ring_js(mouth, voice_end)}') if avatar else ""
    ch_html = f'<div id="tchip">{title}</div><div id="handle">@megerse.tr</div>' if chrome else ""
    ch_js = 'tl.fromTo("#tchip",{y:-40,opacity:0},{y:0,opacity:1,duration:.4,ease:"back.out(2)"},.3);' if chrome else ""
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
  {ch_html}
  {cap_html}
  {av_html}
</div>
{mblur}
<script>
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#progf",{{scaleX:0}},{{scaleX:1,duration:{voice_end},ease:"none"}},0);
{ch_js}
{scenes_js}
{av_js}
{cap_js}
tl.set({{}}, {{}}, {total});
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""


def flash_js(t, peak=.85, dur=.25):
    return f'tl.fromTo("#flash",{{opacity:{peak}}},{{opacity:0,duration:{dur},ease:"power2.out",immediateRender:false}},{t:.2f});'


def punch_js(sel, t, s=1.08, dur=.35):
    """vuruş anında hızlı yakınlaşma (zoom punch)."""
    return f'tl.fromTo("{sel}",{{scale:{s}}},{{scale:1,duration:{dur},ease:"power3.out",immediateRender:false}},{t:.2f});'


def shake_js(sel, t, amp=14, n=8):
    return f'tl.fromTo("{sel}",{{x:-{amp}}},{{x:{amp},duration:.04,repeat:{n},yoyo:true,ease:"none",immediateRender:false}},{t:.2f});tl.set("{sel}",{{x:0}},{t+.04*(n+1):.2f});'


# ---------------- kanal introsu (kancadan sonra, ~1,8 sn) ----------------
INTRO_DUR = 1.8


def intro_html(case_no="05"):
    """'Meğerse dosyası' introsu: dosya kaydı gelir, MEĞERSE damgası iner, kanal adı. Sahne kabı içine konur."""
    folder = ('<svg viewBox="0 0 1080 1920" class="fill" id="ifold-svg"><g id="ifold" transform="translate(540 900)">'
              '<path d="M-400 -260 L-400 300 L400 300 L400 -260 Z" fill="#000" opacity=".35" transform="translate(16 22)"/>'
              '<path d="M-400 -300 L-160 -300 L-120 -260 L400 -260 L400 300 L-400 300 Z" fill="#C9965A" stroke="#1B1414" stroke-width="10" stroke-linejoin="round"/>'
              '<rect x="-360" y="-300" width="700" height="520" rx="10" fill="#F4EEDC" stroke="#1B1414" stroke-width="6" transform="rotate(-3)"/>'
              + "".join(f'<path d="M-300 {-200+i*48} H{180 - (i*61) % 160}" stroke="#9A907A" stroke-width="10" stroke-linecap="round" transform="rotate(-3)"/>' for i in range(7))
              + '<path d="M-400 -180 L400 -180 L400 300 L-400 300 Z" fill="#DDA968" stroke="#1B1414" stroke-width="10" stroke-linejoin="round"/>'
              '<path d="M-400 -180 L400 -180" stroke="#fff" stroke-opacity=".35" stroke-width="8"/>'
              f'<text x="-340" y="250" font-family="Mont" font-weight="800" font-size="46" fill="#6A4A22">DOSYA NO: {case_no}</text>'
              '<path d="M260 -330 C260 -380 320 -380 320 -330 L320 -150 C320 -120 280 -120 280 -150 L280 -320" fill="none" stroke="#B9BEC4" stroke-width="12" stroke-linecap="round"/>'
              '</g></svg>')
    return (f'<div class="fill" style="background:radial-gradient(80% 60% at 50% 45%,#2A2440,#08060E)"></div>{folder}'
            '<div id="istamp">MEĞERSE</div><div id="ihandle">@megerse.tr</div><div id="itag">bilinen yanlışlar · gerçek hikâyeler</div>')


INTRO_CSS = """
#istamp { position:absolute; left:120px; right:120px; top:780px; padding:18px 0; text-align:center; border:16px solid #E8423A; border-radius:26px; color:#E8423A; background:rgba(244,238,220,.9); font-weight:800; font-size:150px; letter-spacing:.04em; transform:rotate(-8deg); opacity:0; }
#ihandle { position:absolute; left:0; right:0; top:1250px; text-align:center; font-weight:800; font-size:64px; color:#FFD23F; -webkit-text-stroke:4px #000; paint-order:stroke fill; opacity:0; }
#itag { position:absolute; left:0; right:0; top:1340px; text-align:center; font-weight:600; font-size:36px; color:#E6E2F0; opacity:0; }
"""


def intro_js(t0, sel="#intro-in"):
    t = t0
    return (f'tl.fromTo("#ifold",{{attr:{{transform:"translate(540 1700) rotate(14)"}}}},{{attr:{{transform:"translate(540 900) rotate(0)"}},duration:.35,ease:"back.out(1.6)",immediateRender:false}},{t:.2f});'
            f'tl.fromTo("#istamp",{{scale:2.6,opacity:0,rotation:-2}},{{scale:1,opacity:1,rotation:-8,duration:.18,ease:"power4.in",immediateRender:false}},{t+.45:.2f});'
            + flash_js(t + .63, .55, .25) + shake_js("#ifold-svg", t + .63, 18, 5)
            + f'tl.fromTo("#ihandle",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.25,ease:"back.out(2)",immediateRender:false}},{t+.8:.2f});'
            f'tl.fromTo("#itag",{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t+.95:.2f});'
            f'tl.to("{sel}",{{scale:2.4,opacity:0,duration:.3,ease:"power2.in"}},{t+INTRO_DUR-.3:.2f});')


def intro_sfx(t0):
    """az ve kısık (Osman: efekt yerinde, yüksek değil)."""
    return [(t0, "whoosh", .6), (t0 + .63, "boom", .7)]


# ---------------- kanal outrosu (ses bittikten sonra, sessiz; soru yok: takip / yorum / paylaş) ----------------
OUTRO_DUR = 3.6
_ICON = {
    "follow": '<svg viewBox="0 0 48 48" width="58" height="58"><circle cx="19" cy="15" r="9" fill="currentColor"/><path d="M3 41 C3 29 35 29 35 41 Z" fill="currentColor"/><path d="M39 14 V30 M31 22 H47" stroke="currentColor" stroke-width="5" stroke-linecap="round"/></svg>',
    "comment": '<svg viewBox="0 0 48 48" width="58" height="58"><path d="M6 8 H42 A4 4 0 0 1 46 12 V32 A4 4 0 0 1 42 36 H20 L10 44 V36 H6 A4 4 0 0 1 2 32 V12 A4 4 0 0 1 6 8 Z" fill="currentColor"/><circle cx="14" cy="22" r="3" fill="#fff"/><circle cx="24" cy="22" r="3" fill="#fff"/><circle cx="34" cy="22" r="3" fill="#fff"/></svg>',
    "share": '<svg viewBox="0 0 48 48" width="58" height="58"><path d="M3 22 L45 4 L32 44 L23 27 Z" fill="currentColor"/><path d="M23 27 L45 4" stroke="#fff" stroke-width="3"/></svg>',
}


def outro_html(handle="@megerse.tr", tagline="bilinen yanlışlar · gerçek hikâyeler"):
    hand = ('<svg viewBox="0 0 80 100" width="120" height="150"><path d="M30 8 C30 0 42 0 42 8 V44 L60 40 C70 38 76 46 72 56 L64 86 C62 94 56 98 48 98 H32 C24 98 18 92 16 86 L8 60 C6 52 14 48 20 54 L30 64 Z" '
            'fill="#F2D2B6" stroke="#1B1414" stroke-width="5" stroke-linejoin="round"/></svg>')
    return ('<div class="fill" style="background:radial-gradient(80% 60% at 50% 40%,#2A2440,#08060E)"></div>'
            f'<div id="ostamp">MEĞERSE</div><div id="ohandle">{handle}</div><div id="otag">{tagline}</div>'
            f'<div class="obtn y" id="ob1">{_ICON["follow"]}<span id="ob1a">TAKİP ET</span><span id="ob1b">TAKİPTESİN ✓</span></div>'
            f'<div class="obtn" id="ob2">{_ICON["comment"]}<span>YORUM YAZ</span></div>'
            f'<div class="obtn" id="ob3">{_ICON["share"]}<span>PAYLAŞ</span></div>'
            f'<div id="otap">{hand}</div>')


OUTRO_CSS = """
#ostamp { position:absolute; left:0; right:0; margin:0 auto; top:300px; width:fit-content; padding:8px 40px; border:12px solid #E8423A; border-radius:22px; color:#E8423A; background:rgba(244,238,220,.92); font-weight:800; font-size:96px; letter-spacing:.04em; transform:rotate(-6deg); opacity:0; }
#ohandle { position:absolute; left:0; right:0; top:520px; text-align:center; font-weight:800; font-size:76px; color:#FFD23F; text-shadow:0 6px 0 #000; opacity:0; }
#otag { position:absolute; left:0; right:0; top:618px; text-align:center; font-weight:600; font-size:36px; color:#E6E2F0; opacity:0; }
.obtn { position:absolute; left:0; right:0; margin:0 auto; width:620px; height:118px; border-radius:60px; background:#fff; color:#141414; display:flex; align-items:center; justify-content:center; gap:22px; font-weight:800; font-size:52px; box-shadow:0 10px 0 rgba(0,0,0,.55); opacity:0; }
.obtn.y { background:#FFD23F; }
#ob1 { top:760px; } #ob2 { top:910px; } #ob3 { top:1060px; }
#ob1 span { position:relative; } #ob1b { position:absolute !important; left:150px; opacity:0; }
#otap { position:absolute; left:640px; top:860px; opacity:0; }
"""


def outro_js(t0, sel="#outro-in"):
    """damga iner → kanal adı → üç düğme sırayla → el 'takip et'e dokunur (TAKİPTESİN ✓) → yorum sallanır → paylaş uçağı kayar."""
    t = t0
    return (f'tl.fromTo("#ostamp",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t+.1:.2f});tl.set("#ostamp",{{opacity:0}},0);'
            + flash_js(t + .3, .35, .25)
            + f'tl.fromTo("#ohandle",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.25,ease:"back.out(2)",immediateRender:false}},{t+.4:.2f});tl.set("#ohandle",{{opacity:0}},0);'
            f'tl.fromTo("#otag",{{opacity:0}},{{opacity:1,duration:.25,immediateRender:false}},{t+.55:.2f});tl.set("#otag",{{opacity:0}},0);'
            f'tl.fromTo(".obtn",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.3,stagger:.14,ease:"back.out(2.2)",immediateRender:false}},{t+.75:.2f});tl.set(".obtn",{{opacity:0}},0);'
            f'tl.fromTo("#otap",{{x:160,y:220,opacity:0}},{{x:0,y:0,opacity:1,duration:.4,ease:"power2.out",immediateRender:false}},{t+1.35:.2f});tl.set("#otap",{{opacity:0}},0);'
            f'tl.to("#otap",{{scale:.86,duration:.08,yoyo:true,repeat:1}},{t+1.8:.2f});tl.to("#ob1",{{scale:.94,duration:.08,yoyo:true,repeat:1}},{t+1.8:.2f});'
            f'tl.set("#ob1a",{{opacity:0}},{t+1.88:.2f});tl.set("#ob1b",{{opacity:1}},{t+1.88:.2f});tl.to("#ob1",{{backgroundColor:"#5EF0D2",duration:.15}},{t+1.88:.2f});'
            f'tl.to("#otap",{{x:40,y:150,duration:.3,ease:"power2.inOut"}},{t+2.2:.2f});'
            f'tl.fromTo("#ob2",{{rotation:-3}},{{rotation:3,duration:.07,repeat:5,yoyo:true,ease:"none",immediateRender:false}},{t+2.45:.2f});tl.set("#ob2",{{rotation:0}},{t+2.9:.2f});'
            f'tl.to("#otap",{{x:40,y:300,duration:.3,ease:"power2.inOut"}},{t+2.75:.2f});'
            f'tl.fromTo("#ob3 svg",{{x:0}},{{x:22,y:-10,duration:.25,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t+3.0:.2f});')


def outro_sfx(t0):
    return [(t0 + .3, "boom", .45), (t0 + 1.88, "pop", .5)]
