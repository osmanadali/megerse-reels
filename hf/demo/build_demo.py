"""Derinlik demosu: python3 hf/demo/build_demo.py && (cd hf && npx -y hyperframes@0.8.181 render -c demo/derinlik.html -o renders/derinlik-demo.mp4)"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from depth import FIG_H, Cam, Scene, defs, figure, pole, tree_simple  # noqa: E402
from artlib2 import DEFS2, house2  # noqa: E402

cam = Cam(horizon=400, vpx=430, f=900, eye=165, sun=(-1, -.7), alt=42)
sc = Scene(cam, "st")
sc.add_road(-40, 700, 40, 9000)
sc.row(520, 900, 900, 9, lambda i: pole(i), 900, 900, w=30)            # direkler: eşit aralık → sıkışma
sc.row(-620, 1100, 1000, 7, lambda i: tree_simple(i), 700, 650, w=120, jitter=20)
sc.add(1500, 5200, house2(0, -230, 1.0, "dh"), 500, 900, w=900)          # uzak ev (pus)
# iki kişi birbirine üç-çeyrek dönük konuşuyor
sc.add_toon(-30, 760, look_at=(150, 800), h=178, pose="talk", shirt="#2E4A7A", pants="#5A5E66", shorts=False, shoes="#2A2420", expr=dict(smile=.7, talk=.5))
sc.add_toon(150, 800, look_at=(-30, 760), h=165, female=True, shirt="#C8553D", pants="#2E3B4E", shorts=False, shoes="#7A2A2A", skin="#F0C8A6", hair="#5A3420", socks=False, expr=dict(lid=.3, smile=.3))
sc.add_toon(380, 2300, look_at=(-200, 2000), h=175, pose="walk", shirt="#3E6A4A")
sc.add(-170, 330, tree_simple(3), 700, 650, w=120, focus=False, shadow=False)          # ön plan: bulanık, örter
layers = sc.svg()
js = sc.js() + sc.camera_js(0, 6, dx=-160, dz=380, ease="sine.inOut")
html = f"""<!doctype html><html lang="tr" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0}} html,body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220}}
#panel{{position:absolute;left:60px;top:270px;width:960px;height:1080px;border-radius:36px;overflow:hidden;border:8px solid #F4F1EA}}
.fill{{position:absolute;inset:0;width:100%;height:100%}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="6" data-width="1080" data-height="1920">
<div id="panel"><svg width="0" height="0" style="position:absolute">{DEFS2.replace('</defs>','')}{defs(cam)}</defs></svg>
<div class="clip fill" data-start="0" data-duration="6" data-track-index="1">{layers}</div></div></div>
<script>const tl=gsap.timeline({{paused:true}});{js}tl.set({{}},{{}},6);window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;</script></body></html>"""
(Path(__file__).parent / "derinlik.html").write_text(html, encoding="utf-8")
print("ok", len(html))
