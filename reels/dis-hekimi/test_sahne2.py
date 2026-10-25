"""Orta sahneler testi: anket, %22, kurul, dipnot (her biri 4 sn). hf/index.html'i ezer."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "reels/dis-hekimi"))
from artlib2 import DEFS2  # noqa: E402
from reelkit2 import HF, LAYOUT_V7, page  # noqa: E402
import sahneler as S  # noqa: E402

o = [0, 4, 8, 12]
SC = [("anket", S.anket_html(), S.anket_js(o[0], o[0] + .6, o[0] + 1.0, o[0] + 2.4)),
      ("yuzde", S.yuzde_html(), S.yuzde_js(o[1], o[1] + .7, o[1] + 2.0, o[1] + 2.6)),
      ("kurul", S.kurul_html(), S.kurul_js(o[2], o[2] + 1.0, o[2] + 1.6)),
      ("dipnot", S.dipnot_html(), S.dipnot_js(o[3], o[3] + .7, o[3] + 2.4))]
html = "".join(f'<div class="scene clip" id="s-{k}" data-start="{o[i]}" data-duration="4" data-track-index="{i + 1}"><div class="fill" style="background:radial-gradient(80% 55% at 50% 40%,#1E2A3C,#080B10)">{h}</div></div>'
               for i, (k, h, _) in enumerate(SC))
js = "".join(j for _, _, j in SC)
(HF / "index.html").write_text(page([], [], html, js, total=16, voice_end=16, title="", voice_src="assets/arsa/gecici.mp3", defs=DEFS2,
                                    extra_css=S.ANKET_CSS + S.YUZ_CSS + S.KURUL_CSS + S.DIP_CSS, avatar=False, chrome=False, caps="box", cap_top=LAYOUT_V7["cap_top"]), encoding="utf-8")
