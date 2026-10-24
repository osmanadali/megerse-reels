"""Yerleşim şablonu (LAYOUT_V7) görseli: örnek arsa sahnesi + Instagram arayüzü + güvenli alanlar.

python3 reels/arsa-degeri/sablon.py → hf/renders/sablon-v7.jpg
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from isoart import Iso  # noqa: E402
from reelkit2 import LAYOUT_V7  # noqa: E402

L = LAYOUT_V7
V0, V1 = L["vis"]
iso = Iso(560, 640, 1.5)
p = [iso.slab(-60, -60, 520, 420, 26, "#8FB46A"),
     iso.tile(0, 0, 200, 300, "#C9A46A"), iso.tile(220, 0, 200, 300, "#C9A46A"),
     iso.grass(0, 0, 200, 300, 60, "#8A7A44", 1), iso.grass(220, 0, 200, 300, 60, "#8A7A44", 9),
     iso.road(-60, 310, 520, 50)]
p += [iso.stake(x, y) for x, y in [(0, 0), (200, 0), (0, 300), (200, 300), (220, 0), (420, 0), (220, 300), (420, 300)]]
p += [iso.tree(-30, 20), iso.house(60, 110, 90, 80), iso.building(250, 60, 140, 180, 6, 34), iso.tree(440, 40, 1.1)]
scene = "".join(p)

heart = '<svg viewBox="0 0 48 48" width="62" height="62"><path d="M24 42 C10 32 4 24 4 16 C4 9 9 5 15 5 C19 5 22 7 24 10 C26 7 29 5 33 5 C39 5 44 9 44 16 C44 24 38 32 24 42 Z" fill="none" stroke="#fff" stroke-width="3.5"/></svg>'
bubble = '<svg viewBox="0 0 48 48" width="62" height="62"><path d="M24 6 C13 6 5 13 5 22 C5 27 8 31 12 34 L10 43 L19 38 C21 38 22 39 24 39 C35 39 43 31 43 22 C43 13 35 6 24 6 Z" fill="none" stroke="#fff" stroke-width="3.5"/></svg>'
plane = '<svg viewBox="0 0 48 48" width="62" height="62"><path d="M4 22 L44 6 L30 44 L22 27 Z M22 27 L44 6" fill="none" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/></svg>'

html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><style>
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-ext-800-normal.woff2);unicode-range:U+0100-024F}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-600-normal.woff2);unicode-range:U+0000-00FF}}
@font-face{{font-family:Mont;font-weight:600;src:url(assets/fonts/montserrat-latin-ext-600-normal.woff2);unicode-range:U+0100-024F}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont,sans-serif;position:relative;background:radial-gradient(80% 55% at 50% 45%,#2A3A4C,#0B1118)}}
.abs{{position:absolute}}
.band{{position:absolute;left:0;right:0;background:rgba(232,66,58,.28);border:3px dashed rgba(255,120,110,.9)}}
.zl{{position:absolute;font-weight:800;font-size:24px;color:#fff;background:rgba(0,0,0,.6);padding:6px 12px;border-radius:10px}}
.tag{{position:absolute;left:0;right:0;margin:0 auto;width:fit-content;padding:14px 24px;border-radius:18px;font-weight:800;font-size:44px;background:#FFD23F;color:#111;box-shadow:0 8px 0 #000}}
.tag.dark{{background:rgba(10,10,14,.85);color:#fff;border:3px solid #fff;box-shadow:none;font-size:38px}}
.cap{{position:absolute;left:70px;right:70px;top:{L["cap_top"]}px;height:230px;display:flex;flex-wrap:wrap;align-content:center;justify-content:center;font-weight:800;font-size:70px;line-height:1.1;color:#fff;text-shadow:0 4px 0 rgba(0,0,0,.85),0 0 26px rgba(0,0,0,.7)}}
.cap span{{display:inline-block;margin:0 .1em;padding:.03em .17em .05em;border-radius:18px}}
.cap span.on{{background:#FFD23F;color:#141414;text-shadow:none;transform:rotate(-2deg)}}
.ig{{color:#fff;text-shadow:0 2px 6px rgba(0,0,0,.6)}}
</style></head><body>
<svg class="abs" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">{scene}</svg>
<div class="band" style="top:0;height:190px"></div>
<div class="abs ig" style="left:0;right:0;top:120px;text-align:center;font-weight:800;font-size:40px">Reels&nbsp;&nbsp;&nbsp;&nbsp;<span style="opacity:.6">Arkadaşlar</span></div>
<div class="zl" style="left:20px;top:14px">0–190 · Instagram üst sekmesi</div>
<div class="tag" style="top:{L["top_tag"]}px">ÜST ETİKET · 200</div>
<div class="abs" style="left:40px;right:40px;top:{V0}px;height:{V1 - V0}px;border:4px dashed #5EF0D2;border-radius:24px"></div>
<div class="zl" style="left:56px;top:{V0 + 110}px;color:#5EF0D2">GÖRSEL ALAN {V0}–{V1}</div>
<div class="tag dark" style="top:{L["low_tag"]}px">ALT ETİKET · {L["low_tag"]}</div>
<div class="abs" style="left:0;right:0;top:{L["cap_top"] - 80}px;height:460px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.42) 28%,rgba(0,0,0,.42) 72%,transparent)"></div>
<div class="cap"><span>ARSA</span><span class="on">DEĞERİ</span><span>NASIL</span></div>
<div class="zl" style="left:20px;top:{L["cap_top"] + 6}px;color:#FFD23F">ALTYAZI {L["cap_top"]}–1670</div>
<div class="band" style="top:1675px;height:245px"></div>
<div class="band" style="top:1050px;left:auto;right:0;width:140px;height:550px"></div><div class="abs" style="left:60px;right:60px;top:{L["cap_top"]}px;height:230px;border:3px dashed #FFD23F;border-radius:18px"></div>
<div class="abs ig" style="right:34px;top:1090px;display:flex;flex-direction:column;align-items:center;gap:52px;font-weight:600;font-size:24px">{heart}{bubble}{plane}</div>
<div class="abs ig" style="left:36px;top:1700px;display:flex;align-items:center;gap:18px;font-weight:800;font-size:34px"><div style="width:64px;height:64px;border-radius:50%;background:#FFD23F"></div>megerse.tr <span style="border:2px solid #fff;border-radius:12px;padding:4px 14px;font-size:28px">Takip et</span></div>
<div class="abs ig" style="left:36px;top:1785px;font-weight:600;font-size:30px;opacity:.9">Arsa değerleri nasıl hesaplanıyor? 🏗️ …</div>
<div class="abs ig" style="left:36px;top:1835px;font-weight:600;font-size:26px;opacity:.8">♫ megerse.tr · Orijinal ses</div>
<div class="zl" style="right:150px;top:1858px">1675+ · alt arayüz</div>
<div class="zl" style="right:150px;top:1060px">sağ düğmeler</div>
</body></html>"""
out = ROOT / "hf/sablon-v7.html"
out.write_text(html, encoding="utf-8")
png = ROOT / "hf/renders/sablon-v7.png"
subprocess.run(["/opt/pw-browsers/chromium-1194/chrome-linux/chrome", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1080,2000", "--virtual-time-budget=3000", f"--screenshot={png}", out.as_uri()], check=True, capture_output=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=1080:1920:0:0", "-q:v", "2", str(png.with_suffix(".jpg"))], check=True)
png.unlink()
print("→", png.with_suffix(".jpg"))
