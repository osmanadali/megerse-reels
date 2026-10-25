"""Ağız içi koridor dolly testi (hf/index.html'i ezer; sonra git checkout hf/index.html)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from dentart import mouth_corridor  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402

cam = Cam(horizon=403, vpx=480, f=1000, eye=165, sun=(-1, -.4), alt=46, haze="#7A2A3A", zfar=4000)
sc = mouth_corridor(cam)
bg = ('<svg class="fill" viewBox="0 0 1080 1920"><defs><linearGradient id="pal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A0E18"/>'
      '<stop offset=".3" stop-color="#9A3A4A"/><stop offset=".42" stop-color="#7A2A3A"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#pal)"/></svg>')
html = f'<div class="scene clip" id="s-m" data-start="0" data-duration="4" data-track-index="1"><div class="fill">{bg}{sc.svg()}</div></div>'
js = sc.js() + "window.PROJ_mc();" + sc.camera_js(0, 4, dz=1900, ease="power1.inOut")
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"
(HF / "index.html").write_text(page([], [], html, js, total=4, voice_end=4, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS,
                                    avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
