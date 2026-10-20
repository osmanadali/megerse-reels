"""Çizim kütüphanesi: reel'lerde tekrar kullanılan gerçekçi vektör parçalar (SVG string).

Yeni bir çizim ürettiğinde buraya ekle; mevcut olanı yeniden çizme, gerekiyorsa burada geliştir.
Envanter: hf/art/README.md
"""
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "hf/art"


def ship():
    """Römorkör (Okene): yan profil, merkez (0,0) güverte, ~620x460 birim; kendi <defs>'i içinde."""
    return (ART / "ship.frag").read_text(encoding="utf-8")


DEFS = """<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3E7CB8"/><stop offset=".6" stop-color="#8FBCE0"/><stop offset="1" stop-color="#F2D6A2"/></linearGradient>
<radialGradient id="fire" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".25" stop-color="#FFE7A0"/><stop offset=".55" stop-color="#FF8A1F"/><stop offset="1" stop-color="#FF5A00" stop-opacity="0"/></radialGradient>
<linearGradient id="trail" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFB347" stop-opacity="0"/><stop offset="1" stop-color="#FFD27A" stop-opacity=".95"/></linearGradient>
<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5B3A2E"/><stop offset="1" stop-color="#3A241C"/></linearGradient>
<linearGradient id="siding" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9E2D0"/><stop offset=".7" stop-color="#F7F2E6"/><stop offset="1" stop-color="#CFC6B0"/></linearGradient>
<linearGradient id="lawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6E9A4C"/><stop offset="1" stop-color="#3E6230"/></linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7D5B0"/><stop offset="1" stop-color="#CDB68C"/></linearGradient>
<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A5A36"/><stop offset="1" stop-color="#5E3B22"/></linearGradient>
<linearGradient id="couch" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4E8C8A"/><stop offset="1" stop-color="#2F5E5C"/></linearGradient>
<linearGradient id="wood" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7A4A26"/><stop offset=".5" stop-color="#A86E3E"/><stop offset="1" stop-color="#6A3E1E"/></linearGradient>
<radialGradient id="rockG" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#5A5550"/><stop offset=".6" stop-color="#2E2B28"/><stop offset="1" stop-color="#141210"/></radialGradient>
<radialGradient id="flash" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6D8"/><stop offset="1" stop-color="#FFF6D8" stop-opacity="0"/></radialGradient>
<radialGradient id="bruise" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#3B1D4F"/><stop offset=".5" stop-color="#6B3A7E" stop-opacity=".85"/><stop offset=".8" stop-color="#B0A23E" stop-opacity=".35"/><stop offset="1" stop-color="#B0A23E" stop-opacity="0"/></radialGradient>
<linearGradient id="cash" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9CC48A"/><stop offset="1" stop-color="#5E8A4C"/></linearGradient>
<filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
</defs>"""

ROCK = '<path d="M-46 -30 L-10 -48 L34 -40 L52 -8 L44 30 L8 48 L-34 40 L-54 8 Z" fill="url(#rockG)" stroke="#0A0908" stroke-width="4"/><path d="M-30 -24 L-6 -36 L20 -30" stroke="#7A736C" stroke-width="4" fill="none" stroke-linecap="round" opacity=".7"/><circle cx="16" cy="10" r="5" fill="#1A1816"/><circle cx="-18" cy="16" r="4" fill="#1A1816"/>'

FIREBALL = '<g><polygon points="-520,-300 -20,-26 20,22" fill="url(#trail)" filter="url(#soft)"/><circle r="70" fill="url(#fire)"/><circle r="22" fill="#FFF8E6"/></g>'


def house(x, y, s=1.0, idp="h"):
    return f"""<g transform="translate({x} {y}) scale({s})" id="{idp}">
<rect x="-300" y="-40" width="600" height="250" fill="url(#siding)" stroke="#2B2420" stroke-width="5"/>
{''.join(f'<path d="M-300 {yy} H300" stroke="#C9BFA6" stroke-width="2"/>' for yy in range(-20, 210, 18))}
<path d="M-340 -36 L0 -230 L340 -36 Z" fill="url(#roof)" stroke="#1E140F" stroke-width="6" stroke-linejoin="round"/>
{''.join(f'<path d="M{-300+i*12} {-36-i*6.6} H{300-i*12}" stroke="#2A1A13" stroke-width="2" opacity=".5"/>' for i in range(1, 26, 3))}
<rect x="150" y="-200" width="46" height="110" fill="#8A3B2A" stroke="#2B1510" stroke-width="5"/><rect x="144" y="-212" width="58" height="16" fill="#6A2A1C"/>
<g id="{idp}-win"><rect x="-240" y="20" width="130" height="110" fill="#CFE6F5" stroke="#2B2420" stroke-width="6"/><path d="M-175 20 V130 M-240 75 H-110" stroke="#2B2420" stroke-width="5"/><path d="M-236 24 Q-210 70 -236 126" fill="#E8A7A0" opacity=".8"/><path d="M-114 24 Q-140 70 -114 126" fill="#E8A7A0" opacity=".8"/></g>
<rect x="110" y="20" width="130" height="110" fill="#CFE6F5" stroke="#2B2420" stroke-width="6"/><path d="M175 20 V130 M110 75 H240" stroke="#2B2420" stroke-width="5"/>
<path d="M-60 210 V40 H60 V210" fill="#7A2E22" stroke="#2B1510" stroke-width="6"/><circle cx="38" cy="130" r="7" fill="#E7C46A"/>
<path d="M-110 0 H110 L120 -10 H-120 Z" fill="#E9E2D0" stroke="#2B2420" stroke-width="4"/><rect x="-104" y="0" width="14" height="210" fill="#F7F2E6" stroke="#2B2420" stroke-width="3"/><rect x="90" y="0" width="14" height="210" fill="#F7F2E6" stroke="#2B2420" stroke-width="3"/>
<rect x="-130" y="206" width="260" height="16" fill="#B8AE98" stroke="#2B2420" stroke-width="3"/>
</g>"""


TREE = '<g><rect x="-14" y="0" width="28" height="170" fill="#5A3B26"/><circle cx="0" cy="-30" r="110" fill="#3F6B34"/><circle cx="-70" cy="10" r="80" fill="#4C7C3C"/><circle cx="70" cy="0" r="86" fill="#365F2C"/><circle cx="20" cy="-100" r="70" fill="#5A8A45"/></g>'


def person(x, y, s=1, c="#1F2733", hat=True):
    h = f'<path d="M-26 -132 H26 L18 -150 H-18 Z M-38 -132 H38" stroke="{c}" stroke-width="8" fill="{c}"/>' if hat else ""
    return f'<g transform="translate({x} {y}) scale({s})" fill="{c}"><circle cx="0" cy="-112" r="26"/>{h}<path d="M-40 -80 Q0 -96 40 -80 L50 20 H-50 Z"/><rect x="-36" y="18" width="26" height="90" rx="10"/><rect x="10" y="18" width="26" height="90" rx="10"/></g>'


