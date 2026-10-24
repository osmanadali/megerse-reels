"""Arsa değeri kapağı: aynı 500 m² iki arsa, fiyat sütunları kat kat ayrışır + başlık (altyazı stili sarı kutu). Damga yok.

python3 reels/arsa-degeri/cover.py → hf/cover-arsa.html → chromium → hf/renders/arsa-kapak.jpg
Profil ızgarası 3:4 kırpar (y 240-1680): önemli her şey o bantta.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from isoart import Iso  # noqa: E402

iso = Iso(493, 880, 1.32)
p = [iso.slab(-80, -70, 560, 450, 30, "#7FA65A"), iso.road(-80, 330, 560, 50)]
for k, x0 in enumerate((0, 240)):
    p.append(iso.tile(x0, 0, 200, 300, "#C9A46A") + iso.grass(x0, 0, 200, 300, 50, "#8A7A44", k * 13))
    p += [iso.stake(x, y) for x, y in ((x0, 0), (x0 + 200, 0), (x0, 300), (x0 + 200, 300))]
p += [iso.tree(-50, -30, 1.1), iso.tree(470, -20), iso.house(-60, 120, 50, 60, 40)]
p.append('<g opacity=".95">' + iso.box(70, 120, 0, 60, 60, 60, "#FFD23F") + '</g>')
p.append('<g filter="url(#glow2)" opacity=".55">' + iso.box(310, 120, 0, 60, 60, 330, "#FFE680") + '</g>')
p.append('<g opacity=".97">' + iso.box(310, 120, 0, 60, 60, 330, "#FFD23F") + '</g>')
m0, m1 = iso.label_pt(100, 150), iso.label_pt(340, 150)
t0, t1 = iso.label_pt(100, 150, 60), iso.label_pt(340, 150, 330)

html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-600-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-ext-600-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:#060B12}}
svg{{position:absolute;left:0;top:0}}
.t{{position:absolute;left:30px;right:30px;top:270px;text-align:center;font-weight:800;color:#fff;font-size:128px;line-height:1.02;text-shadow:0 8px 0 #000,0 0 40px rgba(0,0,0,.6)}}
.pill{{display:inline-block;margin-top:20px;padding:8px 34px 14px;border-radius:30px;background:#FFD23F;color:#141414;font-size:92px;text-shadow:none;transform:rotate(-2deg);box-shadow:0 12px 0 rgba(0,0,0,.55)}}
.m{{position:absolute;width:300px;text-align:center;font-weight:800;font-size:44px;color:#fff;text-shadow:0 4px 0 #000,0 0 16px rgba(0,0,0,.8)}}
.tl{{position:absolute;width:300px;text-align:center;font-weight:800;font-size:76px;color:#FFD23F;text-shadow:0 6px 0 #000}}
.same{{position:absolute;left:0;right:0;top:1500px;text-align:center;font-weight:800;font-size:54px;color:#fff;text-shadow:0 5px 0 #000}}
.same b{{color:#FFD23F}}
</style></head><body>
<svg width="1080" height="1920" viewBox="0 0 1080 1920"><defs>
<radialGradient id="bpbg" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#1B3A5A"/><stop offset="1" stop-color="#060B12"/></radialGradient>
<pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse"><path d="M60 0 H0 V60" fill="none" stroke="#2C5378" stroke-width="1.5" opacity=".45"/></pattern>
<filter id="glow2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter></defs>
<rect width="1080" height="1920" fill="url(#bpbg)"/><rect width="1080" height="1920" fill="url(#grid)"/>{"".join(p)}</svg>
<div class="t">ARSA DEĞERİ<br><span class="pill">NASIL HESAPLANIR?</span></div>
<div class="m" style="left:{m0[0] - 150}px;top:{m0[1] + 20}px">500 m²</div><div class="m" style="left:{m1[0] - 150}px;top:{m1[1] + 20}px">500 m²</div>
<div class="tl" style="left:{t0[0] - 150}px;top:{t0[1] - 100}px">₺</div><div class="tl" style="left:{t1[0] - 150}px;top:{t1[1] - 100}px">₺₺₺</div>
<div class="same">aynı büyüklük, <b>bambaşka fiyat</b></div>
</body></html>"""
out = ROOT / "hf/cover-arsa.html"
out.write_text(html, encoding="utf-8")
png = ROOT / "hf/renders/arsa-kapak.png"
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1080,2000", "--virtual-time-budget=3000", f"--screenshot={png}", out.as_uri()], check=True, capture_output=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "2", str(png.with_suffix(".jpg"))], check=True)
png.unlink()
print("→", png.with_suffix(".jpg"))
