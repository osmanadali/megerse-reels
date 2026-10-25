"""Afiş, kapsam, florür testi (hf/index.html'i ezer)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reels/dis-hekimi"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402
import sahneler as S  # noqa: E402

cam = Cam(horizon=403, vpx=480, f=1000, eye=165, sun=(-1, -.4), alt=46, haze="#7A2A3A", zfar=4000)
sc, fhtml = S.florur_html(cam)
o = [0, 4, 8]
SC = [("afis", S.afis_html(), S.afis_js(o[0], o[0] + 2.0)), ("kapsam", S.kapsam_html(), S.kapsam_js(o[1], o[1] + 1.4, o[1] + 2.6)),
      ("flor", fhtml, S.florur_js(sc, o[2], 4, o[2] + 1.0, (o[2] + .4, o[2] + 1.6, o[2] + 2.8)))]
html = "".join(f'<div class="scene clip" id="s-{k}" data-start="{o[i]}" data-duration="4" data-track-index="{i + 1}"><div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#1E2A3C,#080B10)">{h}</div></div>'
               for i, (k, h, _) in enumerate(SC))
js = "".join(j for _, _, j in SC)
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"
(HF / "index.html").write_text(page([], [], html, js, total=12, voice_end=12, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS,
                                    extra_css=S.AFIS_CSS + S.KAPSAM_CSS + S.FLOR_CSS, avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
