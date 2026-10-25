"""Görsel prototip: reklam seti (yakın/geniş), 10 hekim dizisi, anket formu. python3 reels/dis-hekimi/proto.py → hf/renders/proto-dis-*.jpg"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from dentart import boom_mic, brand_tube, cable, clapper, director_chair, gavel, magnifier, set_flat, softbox, studio_camera, tooth  # noqa: E402
from toon import TOON_H, toon_figure  # noqa: E402

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTS = "".join(f'@font-face{{font-family:Mont;font-weight:{w};src:url(assets/fonts/montserrat-{s}-{w}-normal.woff2);unicode-range:{r}}}'
                for w in (600, 800) for s, r in (("latin", "U+0000-00FF"), ("latin-ext", "U+0100-024F")))


def shot(name, body, bg="#0B0E14"):
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}*{{margin:0;padding:0;box-sizing:border-box}}'
            f'body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont;background:{bg};position:relative}}svg{{position:absolute;left:0;top:0}}'
            '.ad{position:absolute;font-weight:800;color:#fff;text-align:center;text-shadow:0 5px 0 #000}</style></head><body>' + body + '</body></html>')
    p = ROOT / f"hf/_proto-{name}.html"
    p.write_text(html, encoding="utf-8")
    png = ROOT / f"hf/renders/proto-dis-{name}.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--window-size=1080,2000",
                    "--virtual-time-budget=2000", f"--screenshot={png}", p.as_uri()], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "3", str(png.with_suffix(".jpg"))], check=True)
    png.unlink()
    p.unlink()
    print("→", png.with_suffix(".jpg"))


def fig(x, y, h, **kw):
    s = h / TOON_H
    return f'<g transform="translate({x} {y}) scale({s:.3f})">{toon_figure(**kw)}</g>'


DOC = dict(outfit="labcoat", jacket="#F4F6F8", pants="#2E3440", shoes="#E8ECEF")
DEFS = DEFS2

# reklam seti dünyası: set merkezde (540, 1250 taban), etrafında stüdyo
set_w, set_h = 760, 900
world = ['<rect x="-600" y="-200" width="2280" height="1450" fill="#16181F"/>',
         '<rect x="-600" y="1250" width="2280" height="1000" fill="#22252E"/>',
         '<ellipse cx="540" cy="1250" rx="700" ry="90" fill="#FFF6D8" opacity=".08"/>',
         f'<g transform="translate(540 1250)">{set_flat(set_w, set_h)}</g>',
         fig(400, 1250, 640, pose="offer", prop="tube:#2F7FD8", expr=dict(smile=.95, lid=.3), hair_style="quiff", **DOC),
         f'<g transform="translate(720 1040) scale(.55)">{brand_tube("NARVİS")}</g>',
         cable("M120 1330 C200 1500 420 1420 520 1560 S760 1700 900 1640"), cable("M960 1330 C900 1450 760 1480 700 1600", 6),
         f'<g transform="translate(40 1340) scale(1.2)">{softbox()}</g>', f'<g transform="translate(1040 1340) scale(-1.2 1.2)">{softbox()}</g>',
         f'<g transform="translate(990 1330)">{boom_mic(560, 1110)}</g>',
         f'<g transform="translate(250 1800) scale(1.5)">{studio_camera()}</g>',
         f'<g transform="translate(830 1840) scale(1.1)">{director_chair()}</g>',
         f'<g transform="translate(600 1880) scale(.9)">{clapper()}</g>',
         ]
W = "".join(world)
ad = ('<div class="ad" style="left:110px;right:110px;top:1130px;font-size:64px;line-height:1.05;background:rgba(20,40,90,.85);padding:22px 10px;border-radius:24px;border:5px solid #fff">10 DİŞ HEKİMİNDEN<br><span style="color:#FFD23F;font-size:110px">9\'U*</span> ÖNERİYOR</div>')
shot("set-genis", f'<svg width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}{W}</svg>')
shot("set-yakin", f'<svg width="1080" height="1920" viewBox="0 0 1080 1920"><g transform="translate(540 760) scale(2.4) translate(-470 -880)">{DEFS}{W}</g></svg>' + ad)
props = "".join([f'<g transform="translate({140 + i*160} 520) scale(.8)">{brand_tube(n)}</g>' for i, n in enumerate(["NARVİS", "SENSODAYN", "İPENA", "ORAL-P", "SİNYAL"])])
props += f'<g transform="translate(300 1000)">{gavel()}</g><g transform="translate(300 1300)"><g transform="rotate(-35 230 -79)">{gavel()}</g></g><g transform="translate(760 820)">{magnifier(140)}</g>'
shot("props", f'<svg width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}<rect width="1080" height="1920" fill="#1A2230"/>{props}</svg>')

# 10 hekim dizisi
row = []
for i in range(10):
    x = 150 + (i % 5) * 195
    y = 1000 if i < 5 else 1330
    row.append(fig(x, y, 330, pose="stand", expr=dict(smile=.6), hair_style=["short", "bob", "fade", "balding", "long", "quiff", "short", "long", "fade", "bob"][i],
                   female=i in (1, 4, 7, 9), skin=["#F2C9A0", "#E8B98C", "#C98B63", "#F2C9A0", "#D9A577"][i % 5], **DOC))
shot("hekimler", f'<svg width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}<rect width="1080" height="1920" fill="#10141C"/>{"".join(row)}</svg>')

# dişler
shot("disler", f'<svg width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS}<rect width="1080" height="1920" fill="#5A1E2A"/>'
     f'<g transform="translate(340 1100)">{tooth("molar", 400)}</g><g transform="translate(740 1100)">{tooth("incisor", 400, glow=True)}</g></svg>')
