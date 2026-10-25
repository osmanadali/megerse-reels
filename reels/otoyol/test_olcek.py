import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "reels/otoyol"))
from artlib2 import DEFS2  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402
import sahneler as S  # noqa: E402
html = f'<div class="scene clip" id="s-o" data-start="0" data-duration="6" data-track-index="1"><div class="fill">{S.olcek_html()}</div></div>'
js = S.olcek_js(0, 1.0, 2.6, 3.6, 4.4, 4.9)
(HF / "index.html").write_text(page([], [], html, js, total=6, voice_end=6, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS2,
                                    avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
