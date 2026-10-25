"""Diş hekimi reeli sahne parçaları (senaryodan bağımsız, zamanları parametre). build.py bunları kelime çapalarıyla bağlar.
DİKKAT: transform özniteliği olan SVG <g>'yi GSAP x/y ile oynatma (özniteliği ezer); dışına id'li boş <g> sar.
Her fonksiyon (html, js) ya da html/js ayrı döner; koordinatlar 1080×1920 sayfa, görsel alan LAYOUT_V7 (200-1410, yanlar 100-980)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from dentart import boom_mic, brand_tube, cable, clapper, director_chair, set_flat, softbox, studio_camera  # noqa: E402
from toon import TOON_H, toon_figure  # noqa: E402

DOC = dict(outfit="labcoat", jacket="#F4F6F8", pants="#2E3440", shoes="#E8ECEF")
GOLD = "#FFD23F"


def fig(x, y, h, **kw):
    return f'<g transform="translate({x} {y}) scale({h / TOON_H:.3f})">{toon_figure(**kw)}</g>'


def pop_js(sel, t, s0=.4, dur=.3):
    return (f'tl.fromTo("{sel}",{{scale:{s0},opacity:0}},{{scale:1,opacity:1,duration:{dur},ease:"back.out(2.4)",immediateRender:false}},{t:.2f});'
            f'tl.set("{sel}",{{opacity:0}},0);')


def out_js(sel, t, dur=.2):
    return f'tl.to("{sel}",{{opacity:0,duration:{dur}}},{t:.2f});'


# ---------------- 1) KANCA: reklam çekimi, vizörden geri çekilme ----------------
CSS = """
.vf { position:absolute; width:90px; height:90px; border:0 solid #fff; opacity:.9; }
#vfrec { position:absolute; left:130px; top:250px; font-weight:800; font-size:40px; color:#fff; text-shadow:0 3px 0 #000; }
#vfrec i { display:inline-block; width:26px; height:26px; margin-right:12px; border-radius:50%; background:#FF3B30; vertical-align:-2px; }
#vftc { position:absolute; right:130px; top:250px; font-weight:800; font-size:36px; color:#fff; text-shadow:0 3px 0 #000; }
#adban { position:absolute; left:110px; right:110px; top:1120px; padding:20px 10px; border-radius:26px; text-align:center; font-weight:800; font-size:62px; line-height:1.05;
         color:#fff; background:rgba(16,40,96,.9); border:5px solid #fff; box-shadow:0 12px 0 rgba(0,0,0,.45); }
#adban b { color:#FFD23F; font-size:112px; } #adstar { display:inline-block; color:#FFD23F; }
#bigstar { position:absolute; left:0; right:0; top:330px; text-align:center; font-weight:800; font-size:420px; line-height:1; color:#FFD23F;
           -webkit-text-stroke:10px #000; paint-order:stroke fill; text-shadow:0 16px 0 #000; opacity:0; }
"""


def hook_html():
    world = ['<rect x="-1200" y="-800" width="3480" height="2050" fill="#16181F"/>',
             '<rect x="-1200" y="1250" width="3480" height="1400" fill="#22252E"/>',
             '<ellipse cx="540" cy="1250" rx="700" ry="90" fill="#FFF6D8" opacity=".08"/>',
             f'<g transform="translate(540 1250)">{set_flat(760, 900)}</g>',
             f'<g id="addoc">{fig(400, 1250, 640, pose="offer", prop="tube:#2F7FD8", expr=dict(smile=.95, lid=.3), hair_style="quiff", **DOC)}</g>',
             f'<g transform="translate(720 1040) scale(.55)">{brand_tube("NARVİS")}</g>',
             cable("M120 1330 C200 1500 420 1420 520 1560 S760 1700 900 1640"), cable("M960 1330 C900 1450 760 1480 700 1600", 6),
             f'<g transform="translate(40 1340) scale(1.2)">{softbox()}</g>', f'<g transform="translate(1040 1340) scale(-1.2 1.2)">{softbox()}</g>',
             f'<g transform="translate(990 1330)">{boom_mic(560, 1110)}</g>']
    fg = (f'<g transform="translate(230 1640) scale(1.35)">{studio_camera()}</g>'
          f'<g transform="translate(870 1700) scale(1.05)">{director_chair()}</g>'
          f'<g transform="translate(640 1720) scale(.85)">{clapper()}</g>')
    corners = "".join(f'<div class="vf" style="{a}:110px;{b}:{y}px;border-{a}-width:8px;border-{b}-width:8px"></div>'
                      for a in ("left", "right") for b, y in (("top", 230), ("bottom", 560)))
    return (f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:visible"><g id="adw">{"".join(world)}</g><g id="adfg">{fg}</g></svg>'
            f'<div class="fill" id="vfin">{corners}<div id="vfrec"><i></i>REC</div><div id="vftc">00:00:09:12</div></div>'
            '<div id="adban">10 DİŞ HEKİMİNDEN<br><b>9\'U</b> ÖNERİYOR<span id="adstar">*</span></div>'
            '<div id="bigstar">*</div>')


def hook_js(t0, t_pull, t_star, pull=1.7):
    """t0: sahne başı (yakın plan, vizör); t_pull: kamera geri çekilir, set ortaya çıkar; t_star: yıldız işareti büyür."""
    return (f'tl.fromTo("#adw",{{scale:2.4,svgOrigin:"470 880",x:70,y:-120}},{{scale:2.25,x:70,y:-110,duration:{t_pull - t0:.2f},ease:"none"}},{t0:.2f});'
            f'tl.to("#adw",{{scale:1,x:0,y:0,duration:{pull},ease:"power3.inOut"}},{t_pull:.2f});'
            f'tl.fromTo("#adfg",{{y:520,scale:1.4,svgOrigin:"540 1920"}},{{y:0,scale:1,duration:{pull},ease:"power3.inOut",immediateRender:false}},{t_pull:.2f});tl.set("#adfg",{{y:520}},0);'
            f'tl.to("#vfin",{{opacity:0,scale:1.15,duration:.4}},{t_pull + .2:.2f});'
            f'tl.to("#vfrec i",{{opacity:.15,duration:.3,repeat:{int((t_pull - t0) / .6)},yoyo:true}},{t0:.2f});'
            f'tl.fromTo("#adban",{{y:60,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"back.out(2)",immediateRender:false}},{t0 + .15:.2f});tl.set("#adban",{{opacity:0}},0);'
            f'tl.to("#adban",{{y:-30,opacity:0,duration:.3}},{t_pull + .1:.2f});'
            f'tl.fromTo("#adstar",{{scale:1}},{{scale:1.5,duration:.25,yoyo:true,repeat:1}},{t_pull - .5:.2f});'
            + pop_js("#bigstar", t_star, .2, .45)
            + f'tl.to("#bigstar",{{rotation:180,duration:2.4,ease:"none"}},{t_star:.2f});')


# ---------------- SON: 10 hekim, 9'u söner, 10.'su parlar + GÖNDER ----------------
CTA_CSS = """
#dglow { position:absolute; width:300px; height:520px; border-radius:50%; background:radial-gradient(closest-side,rgba(255,226,120,.75),rgba(255,210,63,0)); opacity:0; }
#dtag { position:absolute; left:0; right:0; margin:0 auto; top:200px; width:fit-content; padding:14px 26px; border-radius:18px; font-weight:800; font-size:46px;
        background:#FFD23F; color:#111; box-shadow:0 8px 0 #000; opacity:0; }
"""
COLS = (190, 365, 540, 715, 890)
ROWS = (690, 1090)
HERO = 9                                     # 10. hekim (alt sıra, en sağ)
_LOOKS = [dict(hair_style="short"), dict(hair_style="bob", female=True, skin="#E8B98C"), dict(hair_style="fade", skin="#C98B63"),
          dict(hair_style="balding"), dict(hair_style="long", female=True, skin="#D9A577"), dict(hair_style="quiff", skin="#E8B98C"),
          dict(hair_style="short", skin="#C98B63"), dict(hair_style="long", female=True), dict(hair_style="fade", skin="#D9A577"),
          dict(hair_style="bob", female=True, skin="#F2C9A0")]


def cta_html():
    figs = []
    for i in range(10):
        x, y = COLS[i % 5], ROWS[i // 5]
        expr = dict(smile=.8, lid=.25) if i == HERO else dict(smile=.5)
        figs.append(f'<g class="dk" id="dk{i}">{fig(x, y, 340, pose="stand", expr=expr, **_LOOKS[i], **DOC)}</g>')
    hx, hy = COLS[HERO % 5], ROWS[HERO // 5]
    return (f'<div id="dglow" style="left:{hx - 150}px;top:{hy - 420}px"></div>'
            f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:visible">{"".join(figs)}</svg>'
            '<div id="dtag">10 DİŞ HEKİMİ</div>')


def cta_js(t0, t_dim, t_tag=None):
    """t0: hekimler dizilir; t_dim: 9'u söner, 10.'su öne çıkar."""
    hx, hy = COLS[HERO % 5], ROWS[HERO // 5]
    return (f'tl.fromTo(".dk",{{y:60,opacity:0}},{{y:0,opacity:1,duration:.3,stagger:.06,ease:"back.out(2)",immediateRender:false}},{t0:.2f});tl.set(".dk",{{opacity:0}},0);'
            + (pop_js("#dtag", t_tag) if t_tag else "")
            + f'tl.to(".dk:not(#dk{HERO})",{{opacity:.22,filter:"grayscale(1)",duration:.5}},{t_dim:.2f});'
            f'tl.to("#dk{HERO}",{{scale:1.18,svgOrigin:"{hx} {hy}",duration:.5,ease:"back.out(2)"}},{t_dim:.2f});'
            f'tl.fromTo("#dglow",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.5,immediateRender:false}},{t_dim:.2f});tl.set("#dglow",{{opacity:0}},0);'
            f'tl.to("#dglow",{{opacity:.6,duration:.6,yoyo:true,repeat:5}},{t_dim + .5:.2f});')


# ---------------- ANKET: çoklu seçim → çubuklar ----------------
ANKET_CSS = """
.clip2 { position:absolute; left:130px; right:130px; top:330px; height:780px; border-radius:30px; background:#F4EEDC; border:7px solid #1B1414; box-shadow:0 16px 0 rgba(0,0,0,.5); }
.clip2:before { content:""; position:absolute; left:0; right:0; margin:0 auto; top:-38px; width:220px; height:70px; border-radius:16px; background:#8A8E98; border:6px solid #1B1414; }
.aq { position:absolute; left:40px; right:40px; top:60px; text-align:center; font-weight:800; font-size:46px; line-height:1.12; color:#1B1414; }
.aq small { display:block; margin:14px auto 0; width:fit-content; padding:4px 16px; border-radius:12px; font-weight:600; font-size:32px; color:#6A5A3A; }
.arow { position:absolute; left:60px; right:60px; height:96px; display:flex; align-items:center; gap:26px; font-weight:800; font-size:44px; color:#1B1414; }
.arow svg { flex:none; } .arow span { flex:1; }
.abox { flex:none; position:relative; width:72px; height:72px; border-radius:14px; border:6px solid #1B1414; background:#fff; }
.abox i { position:absolute; left:4px; top:-18px; font-style:normal; font-weight:800; font-size:84px; line-height:1; color:#1FA37A; opacity:0; }
.bar { position:absolute; bottom:560px; width:220px; border-radius:22px 22px 0 0; border:6px solid #1B1414; border-bottom:0; }
.bval { position:absolute; width:300px; text-align:center; font-weight:800; font-size:64px; color:#fff; text-shadow:0 6px 0 #000; opacity:0; }
.bval small { display:block; font-size:30px; color:#FFD23F; }
"""
TUBES = ["?", "NARVİS", "SENSODAYN", "İPENA", "ORAL-P"]


def anket_html(question="Hastalarınıza hangi diş macunlarını önerirsiniz?", note="(birden fazla seçebilirsiniz)", ticks=(0, 1, 2, 3, 4)):
    rows = []
    for i, n in enumerate(TUBES):
        icon = f'<svg viewBox="-70 -320 140 330" width="44" height="104">{brand_tube(n)}</svg>'
        name = "BİR DEV MARKA" if n == "?" else n
        rows.append(f'<div class="arow" style="top:{270 + i * 100}px">{icon}<span>{name}</span><div class="abox"><i id="atk{i}">✓</i></div></div>')
    pen = ('<svg id="apen" viewBox="0 0 60 260" width="60" height="260" style="position:absolute;left:0;top:0;width:60px;height:260px;opacity:0;z-index:6;transform-origin:8px 252px">'
           '<path d="M8 252 L2 220 L22 214 Z" fill="#F2D2B6" stroke="#1B1414" stroke-width="4" stroke-linejoin="round"/><path d="M4 236 L10 252" stroke="#1B1414" stroke-width="5"/>'
           '<path d="M2 220 L40 40 L60 46 L22 214 Z" fill="#2F7FD8" stroke="#1B1414" stroke-width="5" stroke-linejoin="round"/>'
           '<path d="M40 40 L46 10 L66 16 L60 46 Z" fill="#E8423A" stroke="#1B1414" stroke-width="5"/></svg>')
    return (pen + f'<div class="clip2" id="aclip"><div class="aq">{question}<small id="anote">{note}</small></div>{"".join(rows)}</div>'
            '<div class="bar" id="bar0" style="left:250px;height:0;background:#B9C2CC"></div><div class="bar" id="bar1" style="left:610px;height:0;background:#E8577A"></div>'
            '<div class="bval" id="bv0" style="left:210px;top:0">%80+<small>BİR DEV MARKA</small></div>'
            '<div class="bval" id="bv1" style="left:570px;top:0">≈<small>BİR RAKİP</small></div>')


def anket_js(t0, t_note, t_ticks, t_bars, h0=470, h1=440, ticks=(0, 1, 2, 3, 4)):
    """t_ticks: ilk işaret (her biri .22 sn arayla); t_bars: form yukarı kayıp küçülür, iki çubuk neredeyse aynı boya çıkar."""
    js = [pop_js("#aclip", t0, .7, .35),
          f'tl.to("#anote",{{backgroundColor:"#FFD23F",color:"#141414",scale:1.12,duration:.25,ease:"back.out(2)"}},{t_note:.2f});']
    # kalem: kutuların üstüne gelir, her kutuda tık atar (kutu merkezi: x≈130+60+..., sayfa koordinatı)
    bx = 1080 - 130 - 7 - 60 - 36
    js.append(f'tl.fromTo("#apen",{{x:1100,y:1500,opacity:0,rotation:20}},{{x:{bx - 8},y:{330 + 7 + 270 + 12 + 36 - 252},opacity:1,rotation:22,duration:.35,ease:"power2.out",immediateRender:false}},{t_ticks - .35:.2f});tl.set("#apen",{{opacity:0}},0);')
    for k, i in enumerate(ticks):
        tk = t_ticks + k * .22
        y = 330 + 7 + 270 + i * 100 + 12 + 36 - 252
        js.append(f'tl.to("#apen",{{x:{bx - 8},y:{y},duration:.12,ease:"power2.inOut"}},{tk - .12:.2f});tl.to("#apen",{{rotation:10,duration:.06,yoyo:true,repeat:1}},{tk:.2f});')
        js.append(pop_js(f"#atk{i}", tk, 2.2, .22))
    js.append(f'tl.to("#apen",{{x:1150,y:1700,opacity:0,duration:.35,ease:"power2.in"}},{t_ticks + len(ticks) * .22 + .1:.2f});')
    js.append(f'tl.to("#aclip",{{y:-110,scale:.58,transformOrigin:"50% 0%",duration:.45,ease:"power2.inOut"}},{t_bars:.2f});')
    for b, (h, d) in enumerate(((h0, 0), (h1, .35))):
        js.append(f'tl.fromTo("#bar{b}",{{height:0,opacity:1}},{{height:{h},duration:.8,ease:"power2.out",immediateRender:false}},{t_bars + .3 + d:.2f});tl.set("#bar{b}",{{height:0,opacity:0}},0);')
        js.append(f'tl.set("#bv{b}",{{top:{1920 - 560 - h - 120}}},0);' + pop_js(f"#bv{b}", t_bars + 1.0 + d))
    return "".join(js)


# ---------------- %22: 100 hekimden 22'si yeter, "1 NUMARA" ----------------
YUZ_CSS = """
#medal { position:absolute; left:0; right:0; margin:0 auto; top:240px; width:250px; height:250px; border-radius:50%; background:radial-gradient(circle at 35% 30%,#FFE680,#E8B020);
         border:9px solid #1B1414; box-shadow:0 12px 0 rgba(0,0,0,.5); text-align:center; font-weight:800; font-size:120px; line-height:232px; color:#1B1414; opacity:0; }
#medal small { position:absolute; left:-120px; right:-120px; top:262px; white-space:nowrap; font-size:34px; line-height:1; color:#FFD23F; text-shadow:0 4px 0 #000; }
#pct { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:4px 34px 10px; border-radius:30px; background:rgba(8,12,20,.86); top:1215px; text-align:center; font-weight:800; font-size:76px; color:#fff; text-shadow:0 6px 0 #000; opacity:0; }
#pct b { color:#FFD23F; font-size:120px; }
"""


def _mini_doc(lit=False):
    col = "#FFD23F" if lit else "#3A4658"
    return (f'<circle cx="0" cy="-44" r="15" fill="{"#F2C9A0" if lit else "#5A6678"}" stroke="#1B1414" stroke-width="3"/>'
            f'<path d="M-22 0 C-22 -22 -14 -28 0 -28 C14 -28 22 -22 22 0 Z" fill="{col}" stroke="#1B1414" stroke-width="3"/>')


def yuzde_html(n_lit=22):
    cells = []
    for i in range(100):
        x, y = 225 + (i % 10) * 70, 640 + (i // 10) * 58
        cells.append(f'<g transform="translate({x} {y})"><g class="md0">{_mini_doc()}</g><g class="md1" id="md{i}" opacity="0">{_mini_doc(True)}</g></g>')
    return (f'<svg class="fill" viewBox="0 0 1080 1920">{"".join(cells)}</svg>'
            '<div id="medal">#1<small>DİŞ HEKİMİ TAVSİYESİ</small></div>'
            f'<div id="pct">yalnızca <b>%{n_lit}</b></div>')


def yuzde_js(t0, t_lit, t_medal, t_pct, n_lit=22):
    import random
    rnd = random.Random(7)
    order = rnd.sample(range(100), n_lit)
    return (f'tl.fromTo(".md0",{{opacity:0,scale:.3}},{{opacity:1,scale:1,duration:.25,stagger:{{each:.006,from:"center"}},immediateRender:false}},{t0:.2f});tl.set(".md0",{{opacity:0}},0);'
            + "".join(f'tl.to("#md{i}",{{opacity:1,duration:.12}},{t_lit + k * .045:.2f});' for k, i in enumerate(order))
            + pop_js("#medal", t_medal, .2, .45) + f'tl.fromTo("#medal",{{rotationY:-180}},{{rotationY:0,duration:.6,ease:"back.out(1.6)",immediateRender:false}},{t_medal:.2f});'
            + pop_js("#pct", t_pct))


# ---------------- KURUL: tokmak + KANITLANAMADI + ceza sayacı ----------------
KURUL_CSS = """
.adcard { position:absolute; left:140px; right:140px; top:300px; height:470px; border-radius:28px; background:linear-gradient(160deg,#FCE4EC,#F7B9C8); border:7px solid #1B1414;
          box-shadow:0 14px 0 rgba(0,0,0,.5); overflow:hidden; }
.adcard .t { position:absolute; left:280px; right:24px; top:70px; font-weight:800; font-size:44px; line-height:1.1; color:#7A1E3A; }
.adcard .t b { display:block; font-size:110px; line-height:1.05; color:#C81E4A; }
.adcard svg { position:absolute; left:60px; top:70px; }
.stamp2 { position:absolute; left:0; right:0; margin:0 auto; top:700px; width:fit-content; padding:10px 34px; border:11px solid #E8423A; border-radius:18px;
          color:#E8423A; background:rgba(255,255,255,.88); font-weight:800; font-size:66px; transform:rotate(-8deg); opacity:0; }
#fine { position:absolute; left:0; right:0; top:1225px; text-align:center; font-weight:800; font-size:110px; color:#FFD23F; -webkit-text-stroke:5px #000; paint-order:stroke fill; text-shadow:0 8px 0 #000; opacity:0; }
#fine small { display:block; font-size:36px; color:#fff; -webkit-text-stroke:0; text-shadow:0 4px 0 #000; }
"""


COURT_BG = ('<div class="fill" style="background:linear-gradient(180deg,#2A1A10 0%,#4A2E1A 38%,#3A2414 39%,#2A1A10 100%)"></div>'
            '<svg class="fill" viewBox="0 0 1080 1920">' + "".join(f'<rect x="{60 + k*250}" y="140" width="210" height="560" rx="10" fill="none" stroke="#6A4428" stroke-width="10"/>' for k in range(4))
            + '<rect x="0" y="1180" width="1080" height="60" fill="#5A3A20"/><rect x="0" y="1240" width="1080" height="260" fill="#3A2414"/>'
            + '<ellipse cx="540" cy="1150" rx="520" ry="300" fill="#FFE6B0" opacity=".08"/></svg>')


def kurul_html(brand="SENSODAYN", claim="10 diş<br>hekiminden", big="9'u", tail="öneriyor", stamp="KANITLANAMADI", fine_note="PARA CEZASI · 2014"):
    return (COURT_BG + f'<div class="adcard" id="kad"><svg viewBox="-70 -320 140 330" width="190" height="440">{brand_tube(brand)}</svg>'
            f'<div class="t">{claim}<b>{big}</b>{tail}</div></div>'
            f'<div class="stamp2" id="kst">{stamp}</div>'
            f'<svg class="fill" viewBox="0 0 1080 1920"><g id="kgv" transform="translate(470 1130) scale(1.5)">{__import__("dentart").gavel()}</g></svg>'
            f'<div id="fine"><span id="finen">0</span> TL<small>{fine_note}</small></div>')


def kurul_js(t0, t_hit, t_fine, fine=81554):
    return (pop_js("#kad", t0, .7, .35)
            + f'tl.fromTo("#kgv .gvh",{{rotation:-38,svgOrigin:"230 -79"}},{{rotation:-38,duration:.01,immediateRender:false}},{t0:.2f});tl.set("#kgv .gvh",{{rotation:-38,svgOrigin:"230 -79"}},0);'
            f'tl.to("#kgv .gvh",{{rotation:0,svgOrigin:"230 -79",duration:.16,ease:"power3.in"}},{t_hit - .16:.2f});'
            f'tl.to("#kgv .gvh",{{rotation:-20,svgOrigin:"230 -79",duration:.3,ease:"power2.out"}},{t_hit + .05:.2f});'
            f'tl.fromTo("#kst",{{scale:2.6,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t_hit:.2f});tl.set("#kst",{{opacity:0}},0);'
            f'tl.to("#kad",{{x:10,duration:.04,yoyo:true,repeat:5}},{t_hit + .2:.2f});'
            + pop_js("#fine", t_fine)
            + f'(function(){{const o={{v:0}};tl.to(o,{{v:{fine},duration:1.1,ease:"power2.out",onUpdate:()=>{{document.getElementById("finen").textContent=Math.round(o.v).toLocaleString("tr-TR");}}}},{t_fine:.2f});}})();')


# ---------------- DİPNOT: büyüteç küçük yazının üstünden geçer ----------------
DIP_CSS = """
.dcard { position:absolute; left:120px; right:120px; top:330px; height:760px; border-radius:30px; background:linear-gradient(170deg,#1E5FC8,#0E3A88); border:7px solid #1B1414;
         box-shadow:0 14px 0 rgba(0,0,0,.5); overflow:hidden; }
.dcard .big { position:absolute; left:0; right:0; top:120px; text-align:center; font-weight:800; font-size:96px; line-height:1.02; color:#fff; text-shadow:0 6px 0 rgba(0,0,0,.4); }
.dcard .big b { display:block; font-size:170px; color:#FFD23F; }
.fp { position:absolute; left:40px; right:40px; bottom:34px; text-align:center; font-weight:600; font-size:17px; line-height:1.3; color:rgba(255,255,255,.75); }
#lens { position:absolute; left:0; top:0; width:1080px; height:1920px; clip-path:circle(0px at 540px 1050px); pointer-events:none; }
#lens .fp2 { position:absolute; left:40px; right:40px; top:960px; text-align:center; font-weight:800; font-size:50px; line-height:1.18; color:#fff;
             background:#0E3A88; padding:20px 10px; border-radius:20px; }
#lens .fp2 b { color:#FFD23F; }
"""


def dipnot_html(big_top="10 KİŞİDEN", big="9'U", big_bot="TAVSİYE EDİYOR", big_size=170, top_size=96, fine="*Bir ürün deneme platformunda 713 tüketiciyle yapılan anket.",
                fine_big="*Bir ürün deneme platformunda <b>713 tüketiciyle</b> yapılan anket."):
    return (f'<div class="dcard" id="dcd"><div class="big"><span style="font-size:{top_size}px">{big_top}</span><b style="font-size:{big_size}px">{big}</b>{big_bot}</div><div class="fp">{fine}</div></div>'
            f'<div id="lens"><div class="fp2">{fine_big}</div></div>'
            f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:visible"><g id="mag" transform="translate(-200 1300)">{__import__("dentart").magnifier(170)}</g></svg>')


def dipnot_js(t0, t_mag, t_stay):
    """t_mag: büyüteç dipnota gelir, mercek içi büyük yazı görünür; t_stay: mercek büyür, yazı okunur kalır."""
    return (pop_js("#dcd", t0, .7, .35)
            + f'tl.fromTo("#mag",{{x:-260,y:1300}},{{x:540,y:1050,duration:.7,ease:"power3.out",immediateRender:false}},{t_mag:.2f});tl.set("#mag",{{x:-260,y:1300}},0);'
            f'tl.fromTo("#lens",{{clipPath:"circle(0px at 540px 1050px)"}},{{clipPath:"circle(150px at 540px 1050px)",duration:.3,immediateRender:false}},{t_mag + .55:.2f});tl.set("#lens",{{clipPath:"circle(0px at 540px 1050px)"}},0);'
            f'tl.to("#lens",{{clipPath:"circle(720px at 540px 1050px)",duration:.5,ease:"power2.inOut"}},{t_stay:.2f});'
            f'tl.to("#mag",{{x:1300,y:1500,duration:.5,ease:"power2.in"}},{t_stay:.2f});')


# ---------------- AFİŞ: İngiltere 2007, "%80+" afişi → YANILTICI ----------------
AFIS_CSS = """
.poster { position:absolute; left:150px; right:150px; top:300px; height:900px; border-radius:16px; background:linear-gradient(175deg,#F7F7F2,#DCE3EA); border:8px solid #1B1414;
          box-shadow:0 18px 0 rgba(0,0,0,.5); overflow:hidden; }
.poster .pt { position:absolute; left:30px; right:30px; top:60px; text-align:center; font-weight:800; font-size:58px; line-height:1.08; color:#1B2A44; }
.poster .pt b { display:block; font-size:170px; line-height:1; color:#1E5FC8; }
.poster svg { position:absolute; left:0; right:0; margin:0 auto; top:470px; }
#uk { position:absolute; left:0; right:0; margin:0 auto; top:200px; width:fit-content; padding:12px 24px; border-radius:16px; background:rgba(10,14,22,.88); border:3px solid #fff;
      color:#fff; font-weight:800; font-size:40px; opacity:0; }
.stamp3 { position:absolute; left:0; right:0; margin:0 auto; top:820px; width:fit-content; padding:10px 34px; border:12px solid #E8423A; border-radius:18px;
          color:#E8423A; background:rgba(255,255,255,.9); font-weight:800; font-size:80px; transform:rotate(-9deg); opacity:0; }
"""


def afis_html(place="İNGİLTERE · 2007", top="Diş hekimlerinin", big="%80+", bot="bizi öneriyor", stamp="YANILTICI"):
    return (f'<div id="uk">{place}</div><div class="poster" id="post"><div class="pt">{top}<b>{big}</b>{bot}</div>'
            f'<svg viewBox="-80 -330 160 340" width="200" height="425">{brand_tube("?")}</svg></div>'
            f'<div class="stamp3" id="ast">{stamp}</div>')


def afis_js(t0, t_stamp=None, push=1.06):
    js = (pop_js("#uk", t0) + f'tl.fromTo("#post",{{y:120,rotation:-3,opacity:0}},{{y:0,rotation:0,opacity:1,duration:.5,ease:"power3.out",immediateRender:false}},{t0:.2f});tl.set("#post",{{opacity:0}},0);'
          f'tl.fromTo("#post",{{scale:1}},{{scale:{push},duration:3,ease:"none",immediateRender:false}},{t0 + .5:.2f});')
    if t_stamp:
        js += (f'tl.fromTo("#ast",{{scale:2.8,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t_stamp:.2f});tl.set("#ast",{{opacity:0}},0);'
               f'tl.to("#post",{{x:12,duration:.04,yoyo:true,repeat:5}},{t_stamp + .2:.2f});')
    return js


# ---------------- KAPSAM: hassasiyet önerisi beyazlatma tüpüne taşınır ----------------
KAPSAM_CSS = """
.kt { position:absolute; top:1180px; width:360px; text-align:center; font-weight:800; font-size:40px; color:#fff; text-shadow:0 4px 0 #000; }
#badge { position:absolute; left:175px; top:640px; width:230px; height:230px; border-radius:50%; background:#FFD23F; border:7px solid #1B1414; box-shadow:0 10px 0 rgba(0,0,0,.5);
         display:flex; align-items:center; justify-content:center; text-align:center; font-weight:800; font-size:34px; line-height:1.05; color:#1B1414; opacity:0; z-index:3; }
.stamp4 { position:absolute; left:500px; top:900px; padding:8px 26px; border:10px solid #E8423A; border-radius:16px; color:#E8423A; background:rgba(255,255,255,.9);
          font-weight:800; font-size:58px; transform:rotate(-8deg); opacity:0; z-index:4; }
"""


def kapsam_html(b1="HASSASİYET", b2="BEYAZLATMA", badge="DİŞ HEKİMİ<br>ÖNERİSİ", stamp="DURDURULDU"):
    t1 = brand_tube("SENSODAYN").replace(">SENSODAYN<", f">{b1}<")
    t2 = paste_tube_white(b2)
    return (f'<svg class="fill" viewBox="0 0 1080 1920"><g id="kt1"><g transform="translate(290 1140) scale(2.1)">{t1}</g></g><g id="kt2"><g transform="translate(790 1140) scale(2.1)">{t2}</g></g></svg>'
            f'<div class="kt" style="left:110px" id="kl1">hekimlerin önerdiği</div><div class="kt" style="left:610px" id="kl2">reklamı yapılan</div>'
            f'<div id="badge">{badge}</div><div class="stamp4" id="kst4">{stamp}</div>')


def paste_tube_white(label):
    from dentart import paste_tube
    return paste_tube(label, "#F4F6F8", 120, 300, "#5AB8FF")


def kapsam_js(t0, t_move, t_stamp):
    return (f'tl.fromTo("#kt1,#kt2",{{y:200,opacity:0}},{{y:0,opacity:1,duration:.45,stagger:.15,ease:"back.out(1.8)",immediateRender:false}},{t0:.2f});tl.set("#kt1,#kt2",{{opacity:0}},0);'
            + pop_js("#kl1", t0 + .3) + pop_js("#badge", t0 + .5, .2, .4) + pop_js("#kl2", t_move - .2)
            + f'tl.to("#badge",{{x:500,rotation:360,duration:.7,ease:"power2.inOut"}},{t_move:.2f});'
            f'tl.fromTo("#kst4",{{scale:2.6,opacity:0}},{{scale:1,opacity:1,duration:.2,ease:"power4.in",immediateRender:false}},{t_stamp:.2f});tl.set("#kst4",{{opacity:0}},0);')


# ---------------- FLORÜR: ağız içi dalış, mine parlar ----------------
FLOR_CSS = """
.fl { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; padding:14px 28px; border-radius:20px; font-weight:800; font-size:52px; background:#fff; color:#141414;
      border:5px solid #1B1414; box-shadow:0 10px 0 rgba(0,0,0,.5); opacity:0; }
.fl b { color:#1E8FE0; }
"""


def florur_html(cam, labels=(("fl1", "<b>1000–1500</b> ppm florür", 260), ("fl2", "günde <b>2</b> kez", 1180), ("fl3", "tükür, <b>çalkalama</b>", 1180))):
    from dentart import mouth_corridor
    sc = mouth_corridor(cam, sid="flm")
    bg = ('<svg class="fill" viewBox="0 0 1080 1920"><defs><linearGradient id="pal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A0E18"/>'
          '<stop offset=".3" stop-color="#9A3A4A"/><stop offset=".42" stop-color="#7A2A3A"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#pal)"/></svg>')
    lab = "".join(f'<div class="fl" id="{i}" style="top:{y}px">{t}</div>' for i, t, y in labels)
    return sc, bg + sc.svg() + lab


def florur_js(sc, t0, dur, t_glow, t_labels):
    js = sc.js() + "window.PROJ_flm();" + sc.camera_js(t0, dur, dz=1700, ease="power1.inOut")
    js += f'tl.to("#flm .enamel",{{filter:"drop-shadow(0 0 18px #9FE4FF) brightness(1.15)",duration:.6}},{t_glow:.2f});'
    for k, t in enumerate(t_labels):
        js += pop_js(f"#fl{k + 1}", t)
        if k + 1 < len(t_labels) and k > 0:
            js += out_js(f"#fl{k + 1}", t_labels[k + 1] - .15)
    return js


# ---------------- MEĞERSE: reklam cümlesinin gerçek anlamı → tüpler FLORÜR olur ----------------
MEG_CSS = """
.megt { position:absolute; left:0; right:0; top:640px; text-align:center; font-weight:800; font-size:190px; color:#FFD23F; -webkit-text-stroke:7px #000; paint-order:stroke fill;
        text-shadow:0 12px 0 #000; opacity:0; z-index:5; }
#mban { position:absolute; left:110px; right:110px; top:430px; padding:18px 10px; border-radius:26px; text-align:center; font-weight:800; font-size:54px; line-height:1.05;
        color:#fff; background:rgba(16,40,96,.92); border:5px solid #fff; box-shadow:0 12px 0 rgba(0,0,0,.45); opacity:0; }
#mban b { color:#FFD23F; font-size:96px; }
.mp { position:absolute; left:0; right:0; margin:0 auto; width:fit-content; max-width:860px; padding:16px 30px; border-radius:22px; text-align:center; font-weight:800; font-size:50px;
      line-height:1.1; border:5px solid #1B1414; box-shadow:0 10px 0 rgba(0,0,0,.5); opacity:0; }
#mp1 { top:760px; background:#FF5A4E; color:#fff; } #mp2 { top:930px; background:#FFD23F; color:#141414; }
#mp1 s { text-decoration-thickness:6px; }
"""


def meg_html(brands=("NARVİS", "SENSODAYN", "İPENA", "ORAL-P", "SİNYAL")):
    from dentart import paste_tube
    tubes = []
    for i, n in enumerate(brands):
        x = 160 + i * 190
        from dentart import BRANDS
        col, st = BRANDS[n]
        tubes.append(f'<g class="mt" id="mt{i}"><g transform="translate({x} 1390) scale(1.05)">'
                     f'<g class="mta" id="mta{i}">{brand_tube(n)}</g><g class="mtb" id="mtb{i}" opacity="0">{paste_tube("FLORÜR", col, 120, 300, st)}</g></g></g>')
    return ('<div class="megt" id="megt">MEĞERSE</div>'
            '<div id="mban">10 DİŞ HEKİMİNDEN <b>9\'U</b><br>ÖNERİYOR*</div>'
            '<div class="mp" id="mp1">≠ “EN İYİSİ BU”</div><div class="mp" id="mp2">= “ÖNERDİKLERİMDEN<br>BİRİ”</div>'
            f'<svg class="fill" viewBox="0 0 1080 1920" style="overflow:visible">{"".join(tubes)}</svg>')


def meg_js(t0, t_ban, t_p1, t_p2, t_tubes, t_flip, n=5):
    js = (f'tl.fromTo("#megt",{{scale:3,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.out",immediateRender:false}},{t0 + .05:.2f});tl.set("#megt",{{opacity:0}},0);'
          f'tl.to("#megt",{{y:-440,scale:.6,duration:.5,ease:"power2.inOut"}},{t_ban - .1:.2f});'
          + pop_js("#mban", t_ban, .7, .35) + pop_js("#mp1", t_p1) + pop_js("#mp2", t_p2)
          + f'tl.to("#mban,#mp1,#mp2",{{y:-60,opacity:0,duration:.3,stagger:.05}},{t_tubes - .2:.2f});'
          f'tl.fromTo(".mt",{{y:500,opacity:0}},{{y:0,opacity:1,duration:.5,stagger:.08,ease:"back.out(1.6)",immediateRender:false}},{t_tubes:.2f});tl.set(".mt",{{y:500,opacity:0}},0);')
    for i in range(n):
        tf = t_flip + i * .1
        js += (f'tl.to("#mta{i}",{{scaleX:0,svgOrigin:"0 -150",duration:.14,ease:"power2.in"}},{tf:.2f});'
               f'tl.set("#mtb{i}",{{opacity:1,scaleX:0,svgOrigin:"0 -150"}},{tf + .14:.2f});tl.to("#mtb{i}",{{scaleX:1,svgOrigin:"0 -150",duration:.16,ease:"power2.out"}},{tf + .14:.2f});')
    js += f'tl.to(".mtb",{{filter:"drop-shadow(0 0 22px #9FE4FF)",duration:.5}},{t_flip + .7:.2f});'
    return js


# ---------------- KALABALIK: 100 hekim derinlikte, kamera yükselir, 22'si yanar ----------------
def _crowd_doc(i, lit=False, rnd=None):
    skins = ("#F2C9A0", "#E8B98C", "#C98B63", "#D9A577")
    hairs = ("#16110F", "#3A2416", "#6A4A2A", "#8A8A8A")
    sk, hr = skins[i % 4], hairs[(i * 7) % 4]
    coat, sh = ("#FFD23F", "#C99A10") if lit else ("#F4F6F8", "#C9CED4")
    long_h = i % 3 == 1
    hair = (f'<path d="M-16 -150 C-18 -170 18 -170 16 -150 L18 -128 C14 -140 -14 -140 -18 -128 Z" fill="{hr}"/>' if not long_h else
            f'<path d="M-17 -150 C-19 -172 19 -172 17 -150 L19 -112 L12 -112 L12 -136 C6 -142 -6 -142 -12 -136 L-12 -112 L-19 -112 Z" fill="{hr}"/>')
    return (f'<path d="M-9 -4 L-9 -46 M9 -4 L9 -46" stroke="#2E3440" stroke-width="10"/>'
            f'<path d="M-26 -50 C-28 -80 -26 -110 -16 -120 L16 -120 C26 -110 28 -80 26 -50 Z" fill="{coat}" stroke="#1B1414" stroke-width="3.5"/>'
            f'<path d="M4 -120 C14 -100 18 -80 20 -52" stroke="{sh}" stroke-width="7" fill="none"/>'
            f'<path d="M-5 -120 L0 -106 L5 -120 Z" fill="#8FC8E8"/>'
            f'<circle cx="0" cy="-140" r="16" fill="{sk}" stroke="#1B1414" stroke-width="3.5"/>{hair}'
            f'<circle cx="-6" cy="-139" r="2.6" fill="#1B1414"/><circle cx="6" cy="-139" r="2.6" fill="#1B1414"/><path d="M-5 -131 Q0 -127 5 -131" stroke="#1B1414" stroke-width="2" fill="none"/>'
            f'<ellipse cx="-9" cy="-1" rx="9" ry="4" fill="#E8ECEF" stroke="#1B1414" stroke-width="2"/><ellipse cx="9" cy="-1" rx="9" ry="4" fill="#E8ECEF" stroke="#1B1414" stroke-width="2"/>')


CROWD_LIT = sorted(__import__("random").Random(22).sample(range(100), 22))


def crowd_html(cam, sid="cr"):
    from depth import Scene
    sc = Scene(cam, sid, ground=("#1A2230", "#2A3446"), sky=False)
    for i in range(100):
        r, c = divmod(i, 10)
        x, z = -810 + c * 180 + (r % 2) * 40, 520 + r * 190
        lit = (f'<g class="crl" id="crl{i}" opacity="0"><ellipse cx="0" cy="-80" rx="60" ry="110" fill="#FFE680" opacity=".45" filter="url(#glow)"/>{_crowd_doc(i, True)}</g>'
               if i in CROWD_LIT else "")
        sc.add(x, z, f'<g>{_crowd_doc(i)}</g>{lit}', 175, 175, w=50)
    bg = '<div class="fill" style="background:linear-gradient(180deg,#05070C 0%,#0E1522 40%,#1A2230 42%)"></div>'
    return sc, bg + sc.svg()


def crowd_js(sc, t0, dur, t_lit, sid="cr"):
    js = sc.js() + f"window.PROJ_{sid}();" + sc.camera_js(t0, dur, dz=300, dy=220, ease="power1.inOut")
    for k, i in enumerate(CROWD_LIT):
        js += f'tl.to("#crl{i}",{{opacity:1,duration:.15}},{t_lit + k * .05:.2f});'
    js += f'tl.to("#{sid} .crl",{{opacity:1,duration:.01}},{t_lit + 22 * .05 + .2:.2f});'
    return js
