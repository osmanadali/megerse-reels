"""Önizleme: paylaşım çağrısı → gönder uçağı kalkar → outro'daki GÖNDER düğmesine iner (sessiz, ~7,5 sn).
python3 reels/_demo/paylas_demo.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/paylas-demo.mp4)
Not: hf/index.html'i ezer; ardından asıl reelin build.py'sini yeniden çalıştır.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from reelkit2 import HF, LAYOUT_V7, OUTRO_CSS, OUTRO_DUR, SHARE_CSS, outro_html, outro_js, page, share_cta_html, share_cta_js  # noqa: E402

txt = "Bunu, o dokuzdan olmayan diş hekimi arkadaşına gönder.".split()
words, t = [], .5
for w in txt:
    dur = .1 + len(w) * .05
    words.append({"text": w, "startMs": int(t * 1000), "endMs": int((t + dur) * 1000)})
    t += dur + (.12 if w.endswith(",") else .05)
t_go = round(words[-1]["endMs"] / 1000 + .15, 2)
cta_js, outro_t0, land_t = share_cta_js(.45, t_go)
TOTAL = round(outro_t0 + OUTRO_DUR, 2)
bg = ('<div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#3A2A10,#0A0806)"></div>'
      '<div style="position:absolute;left:0;right:0;top:420px;text-align:center;font:800 170px Mont;color:#FFD23F;-webkit-text-stroke:6px #000;paint-order:stroke fill;text-shadow:0 10px 0 #000">MEĞERSE</div>')
scenes = (f'<div class="scene clip" id="s-a" data-start="0" data-duration="{outro_t0 + .3}" data-track-index="1"><div class="fill" id="a-in">{bg}</div></div>'
          f'<div class="scene clip" id="s-outro" data-start="{outro_t0}" data-duration="{OUTRO_DUR}" data-track-index="2"><div class="fill" id="outro-in">{outro_html(label3="GÖNDER", fixed_icons=True)}</div></div>'
          + share_cta_html())
js = (f'tl.fromTo("#outro-in",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{outro_t0});' + cta_js + outro_js(outro_t0, land_t=land_t))
html = page(words, [], scenes, js, total=TOTAL, voice_end=TOTAL, title="", voice_src="assets/arsa/gecici.mp3", extra_css=OUTRO_CSS + SHARE_CSS,
            avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"])
(HF / "index.html").write_text(html, encoding="utf-8")
print("t_go", t_go, "outro", outro_t0, "iniş", land_t, "toplam", TOTAL)
