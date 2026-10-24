"""Kapak v2 (videonun yeni tasarımı): kıl ormanında parlayan beyaz tel + Meğerse damgası + altyazı stili sarı kutu.

python3 reels/beyaz-sac/cover.py → hf/cover-beyazsac.html → chromium ile 1080x1920 → hf/renders/beyazsac-kapak.jpg
Profil ızgarası 3:4 kırpar (y 240-1680): önemli her şey o bantta.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import depth  # noqa: E402

depth.W, depth.H = 1080, 1920
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from hairart import hair_forest, tweezers  # noqa: E402

cam = Cam(horizon=760, vpx=540, f=1000, eye=110, sun=(-1, -.4), alt=46, haze="#E2B89A", zfar=4500)
sc = hair_forest(cam)
forest = sc.svg()
html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-600-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-ext-600-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:#000}}
.fill{{position:absolute;inset:0;width:1080px;height:1920px}}
#shade{{position:absolute;inset:0;background:radial-gradient(60% 40% at 50% 34%,transparent 40%,rgba(10,6,4,.55) 100%),linear-gradient(180deg,rgba(0,0,0,.55) 0%,transparent 20%,transparent 50%,rgba(8,5,3,.9) 66%,rgba(8,5,3,.96) 100%)}}
#ring{{position:absolute;left:0;top:0}}
.ghost{{opacity:.32}} .ghost path{{stroke-dasharray:16 12}}
#halo{{position:absolute;inset:0;background:radial-gradient(circle at 560px 600px,rgba(255,248,228,.30),rgba(255,248,228,.08) 240px,transparent 420px)}}
.t{{position:absolute;left:40px;right:40px;top:1150px;text-align:center;font-weight:800;text-transform:uppercase;color:#fff;font-size:104px;line-height:1.06;text-shadow:0 6px 0 rgba(0,0,0,.9),0 0 34px rgba(0,0,0,.8)}}
.pill{{display:inline-block;margin-top:22px;padding:6px 34px 12px;border-radius:30px;background:#FFD23F;color:#141414;font-size:118px;text-shadow:none;transform:rotate(-2deg);box-shadow:0 12px 0 rgba(0,0,0,.55)}}
</style></head><body>
<svg class="fill" viewBox="0 0 1080 1920"><defs>{DEFS2.replace('<defs>', '').replace('</defs>', '')}{depth_defs(cam).replace('<defs>', '').replace('</defs>', '')}
<linearGradient id="scalpsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A1810"/><stop offset=".35" stop-color="#8A5A42"/><stop offset=".42" stop-color="#E2B89A"/></linearGradient></defs>
<rect width="1080" height="1920" fill="url(#scalpsky)"/></svg>
{forest}
<div id="shade"></div><div id="halo"></div>
<svg id="ring" class="fill" viewBox="0 0 1080 1920"><ellipse cx="540" cy="1058" rx="96" ry="30" fill="none" stroke="#FFD23F" stroke-width="7" stroke-dasharray="18 12"/><g filter="url(#shadow)"><g transform="translate(600 452) scale(4.2)">{tweezers(.12)}</g></g><g transform="translate(604 452)"><path d="M0 -34 L7 -7 L34 0 L7 7 L0 34 L-7 7 L-34 0 L-7 -7 Z" fill="#FFF8D8"/><circle r="9" fill="#fff"/></g><g stroke="#FFD23F" stroke-width="7" stroke-linecap="round"><path d="M668 402 l34 -20"/><path d="M676 446 l40 0"/><path d="M668 490 l34 20"/></g></svg>
<div class="t">BEYAZ SAÇI<br>KOPARIRSAN<br><span class="pill">ÇOĞALIR MI?</span></div>

<script>{sc.js()}CAM_sp.cz=1700;PROJ_sp();const h=document.getElementById('herogrow');h.closest('g[filter]').removeAttribute('filter');[-30,-15,15,30].forEach(a=>{{const c=h.cloneNode(true);c.removeAttribute('id');c.setAttribute('class','ghost');c.setAttribute('transform','rotate('+a+')');h.parentNode.insertBefore(c,h);}});</script>
</body></html>"""
out_html = ROOT / "hf/cover-beyazsac.html"
out_html.write_text(html, encoding="utf-8")
png = ROOT / "hf/renders/beyazsac-kapak.png"
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1080,2000", "--virtual-time-budget=4000", f"--screenshot={png}", out_html.as_uri()], check=True, capture_output=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "2", str(png.with_suffix(".jpg"))], check=True)
png.unlink()
print("→", png.with_suffix(".jpg"))
