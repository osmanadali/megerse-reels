"""Sahne parçaları testi (hf/index.html'i ezer). python3 reels/dis-hekimi/test_sahne.py && snapshot"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reels/dis-hekimi"))
from artlib2 import DEFS2  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, OUTRO_CSS, OUTRO_DUR, SHARE_CSS, outro_html, outro_js, page, share_cta_html, share_cta_js  # noqa: E402
import sahneler as S  # noqa: E402

cta_js, o0, land = share_cta_js(7.0, 8.6)
TOTAL = round(o0 + OUTRO_DUR, 2)
html = (f'<div class="scene clip" id="s-a" data-start="0" data-duration="5.2" data-track-index="1"><div class="fill" style="background:#0B0E14">{S.hook_html()}</div></div>'
        f'<div class="scene clip" id="s-b" data-start="5.1" data-duration="{o0 - 5.1 + .3:.2f}" data-track-index="2"><div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#1E2A3C,#080B10)">{S.cta_html()}</div></div>'
        f'<div class="scene clip" id="s-outro" data-start="{o0}" data-duration="{OUTRO_DUR}" data-track-index="3"><div class="fill" id="outro-in">{outro_html(label3="GÖNDER", fixed_icons=True)}</div></div>'
        + share_cta_html())
js = (S.hook_js(0, 1.6, 3.6) + S.cta_js(5.2, 6.4, 5.5) + cta_js + f'tl.fromTo("#outro-in",{{opacity:0}},{{opacity:1,duration:.3,immediateRender:false}},{o0});' + outro_js(o0, land_t=land))
(HF / "index.html").write_text(page([], [], html, js, total=TOTAL, voice_end=TOTAL, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS2,
                                    extra_css=S.CSS + S.CTA_CSS + OUTRO_CSS + SHARE_CSS, avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
print("toplam", TOTAL)
