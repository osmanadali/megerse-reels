"""Diş hekimi reeli sahne parçaları (senaryodan bağımsız, zamanları parametre). build.py bunları kelime çapalarıyla bağlar.
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
