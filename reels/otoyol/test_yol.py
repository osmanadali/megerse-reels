"""Otoyol POV dolly testi (hf/index.html'i ezer)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from artlib2 import DEFS2  # noqa: E402
from depth import Cam, defs as depth_defs  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402
from roadart import car_rear_world, highway  # noqa: E402

cam = Cam(horizon=327, vpx=480, f=900, eye=120, sun=(-1, -.4), alt=40, haze="#C8D4DE", zfar=16000)
sc = highway(cam, z1=40000)
car_rear_world(sc)
bg = '<div class="fill" style="background:linear-gradient(180deg,#6FA8DC 0%,#BFD6E8 33%,#E6EDF2 36%)"></div>'
html = f'<div class="scene clip" id="s-m" data-start="0" data-duration="4" data-track-index="1"><div class="fill">{bg}{sc.svg()}</div></div>'
js = sc.js() + "window.PROJ_hw();" + sc.camera_js(0, 4, dz=13333, ease="none")
DEFS = DEFS2.replace("</defs>", "") + depth_defs(cam) + "</defs>"
(HF / "index.html").write_text(page([], [], html, js, total=4, voice_end=4, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS,
                                    avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
