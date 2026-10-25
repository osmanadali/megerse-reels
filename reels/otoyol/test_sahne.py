"""POV gündüz/sis/sarı/gece + yol türleri testi (hf/index.html'i ezer)."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "reels/otoyol"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402
from roadart import YELLOW  # noqa: E402
import sahneler as S  # noqa: E402

cam = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#C8D4DE", zfar=16000)
items = []
sc1 = S.pov_scene(cam, "p1"); h1 = S.pov_html(sc1, "gun", hud='<div class="hud" id="cntw" style="top:230px">120 km/sa<br><b id="cnt">0</b> çizgi</div>')
sc2 = S.pov_scene(cam, "p2", 900, 300); h2 = S.pov_html(sc2, "sis", fog=True)
sc3 = S.pov_scene(cam, "p3", 600, 900, paint=YELLOW, cones=True); h3 = S.pov_html(sc3, "gun")
camn = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#1A2234", zfar=16000)
sc4 = S.pov_scene(camn, "p4", night=True); h4 = S.pov_html(sc4, "gece", night=True)
o = [0, 4, 8, 12, 16]
sc_list = [("p1", h1, S.pov_js(sc1, "p1", 0, 4, counter=("cnt", .2))), ("p2", h2, S.pov_js(sc2, "p2", 4, 4, speed_kmh=60)),
           ("p3", h3, S.pov_js(sc3, "p3", 8, 4, speed_kmh=50)), ("p4", h4, S.pov_js(sc4, "p4", 12, 4)),
           ("tur", S.turler_html(), S.turler_js(16, 4, (16.2, 16.5, 16.8)))]
html = "".join(f'<div class="scene clip" id="s-{k}" data-start="{o[i]}" data-duration="4" data-track-index="{i + 1}"><div class="fill" style="background:#0B0E14">{h}</div></div>'
               for i, (k, h, _) in enumerate(sc_list))
js = "".join(j for _, _, j in sc_list)
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"
(HF / "index.html").write_text(page([], [], html, js, total=20, voice_end=20, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS,
                                    extra_css=S.POV_CSS + S.TUR_CSS, avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
