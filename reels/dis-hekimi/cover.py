"""Diş hekimi reeli kapağı: reklam çekimindeki önlüklü "hekim" + elinde taklit marka tüp, dev başlık "9'U*" ve yıldızın üstünde büyüteç. Damga yok, altyazı yok.

python3 reels/dis-hekimi/cover.py → hf/cover-dis.html → chromium → hf/renders/dis-kapak.jpg
Profil ızgarası 3:4 kırpar (y 240-1680): önemli her şey o bantta; iPhone yanlardan ~100 px kırpar.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from dentart import magnifier, set_flat, softbox  # noqa: E402
from toon import TOON_H, toon_figure  # noqa: E402

DOC = dict(outfit="labcoat", jacket="#F4F6F8", pants="#2E3440", shoes="#E8ECEF")
s = 1250 / TOON_H
doc = f'<g transform="translate(330 2050) scale({s:.3f})">{toon_figure(pose="offer", prop="tube:#2F7FD8", expr=dict(smile=.95, lid=.3), hair_style="quiff", **DOC)}</g>'
world = (f'<rect width="1080" height="1920" fill="#16181F"/><g transform="translate(540 1900) scale(1.6)">{set_flat(760, 1200)}</g>'
         f'<g transform="translate(-40 1500) scale(1.4)">{softbox()}</g><g transform="translate(1120 1500) scale(-1.4 1.4)">{softbox()}</g>'
         '<rect width="1080" height="1920" fill="url(#cvv)"/>' + doc)

html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:#0B0E14}}
svg{{position:absolute;left:0;top:0}}
.t{{position:absolute;left:40px;right:40px;top:270px;text-align:center;font-weight:800;color:#fff;font-size:96px;line-height:1.0;text-shadow:0 8px 0 #000,0 0 40px rgba(0,0,0,.6)}}
.t b{{display:block;font-size:330px;line-height:.95;color:#FFD23F;-webkit-text-stroke:9px #000;paint-order:stroke fill;text-shadow:0 14px 0 #000}}
.pill{{position:absolute;left:0;right:0;margin:0 auto;top:1520px;width:fit-content;padding:10px 32px 16px;border-radius:30px;background:#FFD23F;color:#141414;font-weight:800;font-size:56px;transform:rotate(-2deg);box-shadow:0 12px 0 rgba(0,0,0,.55)}}
</style></head><body>
<svg width="1080" height="1920" viewBox="0 0 1080 1920">{DEFS2.replace("</defs>", "")}<radialGradient id="cvv" cx=".5" cy=".4" r=".75"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient></defs>{world}</svg>
<div class="t">10 DİŞ HEKİMİNDEN<b>9'U*</b></div>
<svg width="1080" height="1920" viewBox="0 0 1080 1920"><g transform="translate(818 640) rotate(-10)">{magnifier(120)}</g></svg>
<div class="pill">GERÇEKTEN ÖNERİYOR MU?</div>
</body></html>"""
out = ROOT / "hf/cover-dis.html"
out.write_text(html, encoding="utf-8")
png = ROOT / "hf/renders/dis-kapak.png"
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1080,2000", "--virtual-time-budget=3000", f"--screenshot={png}", out.as_uri()], check=True, capture_output=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "2", str(png.with_suffix(".jpg"))], check=True)
png.unlink()
print("→", png.with_suffix(".jpg"))
