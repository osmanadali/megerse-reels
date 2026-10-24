"""Kapak: python3 reels/beyaz-sac/cover.py → hf/cover-beyazsac.html (chromium ile 1080x1920 ekran görüntüsü)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from hairart import bathroom_bg, mirror_glass  # noqa: E402
from toon import toon_figure  # noqa: E402

HERO = dict(outfit="tee", shirt="#2F5D7C", sleeve="#2F5D7C", hair_style="short", hair="#2A1E18", skin="#E2B48C", shorts=False, pants="#2A2C33")
fig = toon_figure(pose="pluck", look=(0, -1), expr=dict(lid=.1, smile=-.4, brow=.8), **HERO)
greys = "".join(f'<path d="M{x} {y} q{dx} -3 {dx*1.6} -6" stroke="#F4F4F0" stroke-width="1.1" fill="none"/>' for x, y, dx in [(6, -174, 2), (11, -171, 2), (-8, -173, -2), (14, -167, 2.4)])
refl = ('<defs><clipPath id="mc"><rect x="170" y="330" width="740" height="940" rx="10"/></clipPath></defs><g clip-path="url(#mc)"><rect x="170" y="330" width="740" height="940" fill="#BFD0D6"/>'
        f'<g transform="translate(560 1720) scale(6.6)">{fig}{greys}<circle cx="-1" cy="-194" r="8" fill="#FFF6C8" opacity=".95" filter="url(#glow)"/></g></g>')
F = ROOT / "hf/assets/fonts"
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-600-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-ext-600-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:#000}}
svg{{position:absolute;inset:0}} .sh{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.75) 0%,transparent 22%,transparent 55%,rgba(0,0,0,.85) 78%)}}
.k{{position:absolute;left:0;right:0;top:120px;text-align:center;font-weight:600;font-size:34px;letter-spacing:.16em;color:#fff}} .k b{{color:#FFD23F}}
.t{{position:absolute;left:40px;right:40px;top:1140px;text-align:center;font-weight:800;font-size:112px;line-height:1.02;color:#fff;-webkit-text-stroke:6px #000;paint-order:stroke fill;text-shadow:0 10px 0 #000}}
.t span{{color:#FFD23F}} .q{{position:absolute;right:70px;top:300px;width:200px;height:200px;border-radius:30px;background:#FF4D4D;border:8px solid #111;box-shadow:0 10px 0 #111;color:#fff;font-weight:800;font-size:150px;line-height:184px;text-align:center;transform:rotate(10deg)}}
</style></head><body><svg viewBox="0 0 1080 1920" width="1080" height="1920"><defs>{DEFS2.replace('<defs>','').replace('</defs>','')}</defs>{bathroom_bg()}{refl}{mirror_glass()}</svg>
<div class="sh"></div><div class="k">MEĞERSE DOSYASI <b>|</b> MİT</div><div class="q">?</div>
<div class="t">BEYAZ SAÇI<br>KOPARIRSAN<br><span>ÇOĞALIR MI?</span></div></body></html>"""
(ROOT / "hf/cover-beyazsac.html").write_text(html, encoding="utf-8")
print("ok")
