"""Omuz üstü konuşma demosu: python3 hf/demo/build_ots.py && (cd hf && npx -y hyperframes@0.8.181 render -c demo/ots.html -o renders/ots-demo.mp4)"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from portrait import DEFS_P, back_shoulder, bust, chiaroscuro, defs_light, hand_cup, light_shafts  # noqa: E402

DUR = 6
# arka plan: 1950'ler salon, sol üstte pencere (anahtar ışık soldan), alan derinliği ile bulanık
bg = f"""<svg class="fill" viewBox="0 0 960 1080" style="overflow:visible"><g filter="url(#dofBG)">
<rect x="-200" y="-200" width="1400" height="1500" fill="url(#wallpaper)"/><rect x="-200" y="-200" width="1400" height="1500" fill="#2A1A10" opacity=".35"/>
<rect x="-120" y="60" width="300" height="420" fill="#FFF3D6"/><rect x="-120" y="60" width="300" height="420" fill="none" stroke="#E9E0CC" stroke-width="22"/>
<path d="M30 60 V480 M-120 270 H180" stroke="#E9E0CC" stroke-width="12"/><path d="M180 50 Q230 280 200 500 L250 500 Q270 280 230 50 Z" fill="#8A3A2A"/>
<rect x="560" y="160" width="190" height="150" fill="#5A3A22"/><rect x="574" y="174" width="162" height="122" fill="#7A8A8E"/><path d="M574 260 L640 220 L700 250 L736 230 V296 H574 Z" fill="#4A5A3A"/>
<path d="M820 420 L900 420 L880 360 L840 360 Z" fill="#E9D9B0"/><rect x="856" y="420" width="8" height="200" fill="#6A5030"/><ellipse cx="860" cy="390" rx="70" ry="50" fill="#FFE7B0" opacity=".35" filter="url(#soft8)"/>
<rect x="-200" y="760" width="1400" height="500" fill="#4A2E1C"/><rect x="-200" y="760" width="1400" height="12" fill="#6A4630"/>
</g>{light_shafts(-60, 80, angle=-32, n=5, length=1300, spread=60, op=.4)}</svg>"""
# orta plan: kadın, adama (sola) dönük, ona bakıyor; elinde fincan
mid = f"""<svg class="fill" viewBox="0 0 960 1080" style="overflow:visible">
<g transform="translate(600 470) scale(1.05)">{bust(.5, flip=True, lit_left=True, coat="#7A3B30", female=True, skin="#D9A07A", hair="#5A3420", iris="#3E5A3A", gaze=(.85, -.05), expr=dict(brow=.35, smile=.25), age=.2, pid="w")}</g>
<path d="M-200 880 L1200 860 L1200 1300 L-200 1300 Z" fill="#5A341E" filter="url(#woodgrain)"/><path d="M-200 880 L1200 860" stroke="#C8925A" stroke-opacity=".55" stroke-width="5"/>
<rect x="-200" y="900" width="1400" height="40" fill="#000" opacity=".25" filter="url(#soft8)"/>
<ellipse cx="530" cy="1000" rx="80" ry="14" fill="#000" opacity=".55" filter="url(#soft3)"/><path d="M560 990 L760 1010 L740 1030 L540 1010 Z" fill="#000" opacity=".25" filter="url(#soft8)"/>
<g transform="translate(520 935) scale(.95)">{hand_cup("#D9A07A", sleeve="#7A3B30", cuff="#D9A07A")}</g></svg>"""
# ön plan: adamın omzu ve başı (sırtı kameraya), bulanık, kadrajı keser
fg = f"""<svg class="fill" viewBox="0 0 960 1080" style="overflow:visible"><g transform="translate(70 700) scale(1.25)" filter="url(#dofFG)">{back_shoulder(lit_left=True)}</g></svg>"""
top = f'<svg class="fill" viewBox="0 0 960 1080" style="overflow:visible">{chiaroscuro(560, 400, 820, .7)}</svg>'

js = (f'tl.fromTo("#L-bg",{{scale:1.06,x:10}},{{scale:1.1,x:-14,duration:{DUR},ease:"sine.inOut",transformOrigin:"55% 40%"}},0);'
      f'tl.fromTo("#L-mid",{{scale:1.0,x:0}},{{scale:1.09,x:-34,duration:{DUR},ease:"sine.inOut",transformOrigin:"62% 42%"}},0);'
      f'tl.fromTo("#L-fg",{{scale:1.0,x:0}},{{scale:1.16,x:-110,duration:{DUR},ease:"sine.inOut",transformOrigin:"10% 90%"}},0);'
      f'tl.fromTo("#L-bg .dust",{{y:0,x:0}},{{y:40,x:30,duration:{DUR},ease:"none"}},0);'
      f'tl.fromTo("#L-mid",{{rotation:0}},{{rotation:-.6,duration:1.4,yoyo:true,repeat:3,ease:"sine.inOut",transformOrigin:"62% 60%"}},0);')
html = f"""<!doctype html><html lang="tr" data-resolution="portrait"><head><meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0}} html,body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220}}
#panel{{position:absolute;left:60px;top:270px;width:960px;height:1080px;border-radius:36px;overflow:hidden;border:8px solid #F4F1EA;background:#1A120C}}
.fill{{position:absolute;inset:0;width:100%;height:100%}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
<div id="panel"><svg width="0" height="0" style="position:absolute">{DEFS2.replace('</defs>','')}{DEFS_P}{defs_light(True)}</defs></svg>
<div class="clip fill" data-start="0" data-duration="{DUR}" data-track-index="1"><div class="fill" id="L-bg">{bg}</div><div class="fill" id="L-mid">{mid}</div><div class="fill" id="L-fg">{fg}</div><div class="fill">{top}</div></div></div></div>
<script>const tl=gsap.timeline({{paused:true}});{js}tl.set({{}},{{}},{DUR});window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;</script></body></html>"""
(Path(__file__).parent / "ots.html").write_text(html, encoding="utf-8")
print("ok", len(html))
