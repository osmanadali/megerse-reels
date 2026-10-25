"""Otoyol reeli kapağı: asfaltın hemen üstünden (alçak kamera) uzanan kesik çizgi, yanında "? m" ölçü bandı, başlık "BU ÇİZGİ KAÇ METRE?". Damga/altyazı yok.

python3 reels/otoyol/cover.py → hf/cover-otoyol.html → chromium → hf/renders/otoyol-kapak.jpg
Profil ızgarası 3:4 kırpar (y 240-1680); iPhone yanlardan ~100 px kırpar.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from roadart import highway  # noqa: E402

cam = Cam(horizon=250, vpx=480, f=900, eye=55, sun=(-1, -.4), alt=40, haze="#E8C9A0", zfar=16000)
sc = highway(cam, sid="cv", x0=187.5, z0=-200, z1=30000)        # orta şerit çizgisi x=0'da, kameranın tam önünde
svg = sc.svg()
html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:linear-gradient(180deg,#3A5A8A 0%,#E8A868 30%,#F4D2A0 33%)}}
.fill{{position:absolute;left:0;top:0;width:1080px;height:1920px}} .fill > svg{{width:100%;height:100%;display:block}}
.t{{position:absolute;left:40px;right:40px;top:230px;text-align:center;font-weight:800;color:#fff;font-size:110px;line-height:1.0;text-shadow:0 8px 0 #000,0 0 40px rgba(0,0,0,.5)}}
.t b{{display:block;margin-top:14px;font-size:150px;color:#FFD23F;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 12px 0 #000}}
.q{{position:absolute;left:600px;top:1120px;font-weight:800;font-size:150px;color:#FFD23F;-webkit-text-stroke:7px #000;paint-order:stroke fill;text-shadow:0 10px 0 #000;transform:rotate(-6deg)}}
.vig{{position:absolute;left:0;top:0;width:1080px;height:1920px;background:radial-gradient(75% 60% at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}}
</style></head><body>
<svg width="0" height="0" style="position:absolute">{DEFS2.replace("</defs>", "")}{depth_defs(cam).replace("<defs>", "")}</defs></svg>
<div class="fill">{svg}</div><div class="vig"></div>
<svg class="fill" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0"><path d="M560 1700 L560 1010 M530 1700 H590 M530 1010 H590" stroke="#1B1414" stroke-width="16" stroke-linecap="round"/>
<path d="M560 1700 L560 1010 M530 1700 H590 M530 1010 H590" stroke="#FFD23F" stroke-width="8" stroke-linecap="round"/></svg>
<div class="t">BU ÇİZGİ<b>KAÇ METRE?</b></div><div class="q">? m</div>
</body></html>"""
out = ROOT / "hf/cover-otoyol.html"
out.write_text(html, encoding="utf-8")
png = ROOT / "hf/renders/otoyol-kapak.png"
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1080,2000", "--virtual-time-budget=3000", f"--screenshot={png}", out.as_uri()], check=True, capture_output=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "2", str(png.with_suffix(".jpg"))], check=True)
png.unlink()
print("→", png.with_suffix(".jpg"))
