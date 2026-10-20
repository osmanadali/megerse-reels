"""Çizim kütüphanesi v2: dokulu, ışıklı, katmanlı (alan derinliği) illüstrasyon parçaları.

v1 (artlib.py) korunur; yeni reel'ler bunları kullanır. Envanter: hf/art/README.md
Tanımlar (DEFS2) sayfada BİR KEZ, her zaman görünen bir <svg> içinde olmalı (reelkit.page(defs=DEFS2)); gizli sahnedeki <pattern> çizilmez.
Hareket edecek nesneler (motion blur) HTML <div> içinde ayrı <svg> olarak kullanılmalı: obj_svg().
"""

DEFS2 = """<defs>
<filter id="grainy" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .32 0" result="d"/><feComposite in="d" in2="SourceGraphic" operator="in" result="d2"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>
<filter id="woodgrain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".012 .32" numOctaves="3" seed="9" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 .12  0 0 0 0 .05  0 0 0 0 0  0 0 0 .55 0" result="d"/><feComposite in="d" in2="SourceGraphic" operator="in" result="d2"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>
<filter id="organic" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="7" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="34" xChannelSelector="R" yChannelSelector="G" result="d"/><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="2" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .4 0" result="nd"/><feComposite in="nd" in2="d" operator="in" result="nd2"/><feMerge><feMergeNode in="d"/><feMergeNode in="nd2"/></feMerge></filter>
<filter id="rough" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="2" seed="11" result="t"/><feDisplacementMap in="SourceGraphic" in2="t" scale="9" xChannelSelector="R" yChannelSelector="G"/></filter>
<filter id="dof" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="7"/></filter>
<filter id="dof2" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#000" flood-opacity=".38"/></filter>
<linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2F6EA8"/><stop offset=".55" stop-color="#86B6DA"/><stop offset="1" stop-color="#E9D7B4"/></linearGradient>
<linearGradient id="hazeG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9D8E2" stop-opacity="0"/><stop offset="1" stop-color="#E9DCC0" stop-opacity=".8"/></linearGradient>
<linearGradient id="grass2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8F9A52"/><stop offset="1" stop-color="#4C5A2A"/></linearGradient>
<linearGradient id="roof2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4A3A36"/><stop offset="1" stop-color="#2A201E"/></linearGradient>
<linearGradient id="wallLit" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F2EBDB"/><stop offset="1" stop-color="#E2D7BF"/></linearGradient>
<linearGradient id="wallShade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#B9AE95"/><stop offset="1" stop-color="#9E937B"/></linearGradient>
<linearGradient id="glass2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#DDEBF3"/><stop offset=".45" stop-color="#8FAFC4"/><stop offset="1" stop-color="#3E5A6E"/></linearGradient>
<linearGradient id="door2G" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5E2418"/><stop offset=".5" stop-color="#7C3324"/><stop offset="1" stop-color="#4E1C12"/></linearGradient>
<radialGradient id="brass" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#FFF1B8"/><stop offset=".4" stop-color="#D9A93E"/><stop offset="1" stop-color="#7A5512"/></radialGradient>
<linearGradient id="brassBar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7DC86"/><stop offset=".5" stop-color="#C9963A"/><stop offset="1" stop-color="#7A5512"/></linearGradient>
<radialGradient id="rock2G" cx=".32" cy=".28" r=".85"><stop offset="0" stop-color="#4A4643"/><stop offset=".45" stop-color="#26231F"/><stop offset="1" stop-color="#0B0A09"/></radialGradient>
<radialGradient id="fire2" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".2" stop-color="#FFF1BF"/><stop offset=".45" stop-color="#FFA43A"/><stop offset=".75" stop-color="#FF5A12" stop-opacity=".55"/><stop offset="1" stop-color="#FF3A00" stop-opacity="0"/></radialGradient>
<linearGradient id="smoke" x1="1" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#F5E6D0" stop-opacity=".9"/><stop offset="1" stop-color="#C9C2BA" stop-opacity="0"/></linearGradient>
<linearGradient id="paper2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9DCC0"/><stop offset="1" stop-color="#D3C3A0"/></linearGradient>
<pattern id="wallpaper" width="90" height="120" patternUnits="userSpaceOnUse"><rect width="90" height="120" fill="#E6DCC4"/><path d="M45 6 C30 30 60 40 45 64 C30 88 60 98 45 120" stroke="#B9AE8E" stroke-width="3" fill="none"/><g fill="#C3B48F"><ellipse cx="34" cy="26" rx="9" ry="5" transform="rotate(-35 34 26)"/><ellipse cx="57" cy="48" rx="9" ry="5" transform="rotate(35 57 48)"/><ellipse cx="33" cy="80" rx="9" ry="5" transform="rotate(-35 33 80)"/><ellipse cx="57" cy="102" rx="9" ry="5" transform="rotate(35 57 102)"/></g><circle cx="45" cy="64" r="7" fill="#C9907E"/></pattern>
<pattern id="shingles" width="40" height="22" patternUnits="userSpaceOnUse"><rect width="40" height="22" fill="#3B2E2B"/><path d="M0 21 H40 M20 0 V11 M0 11 H40 M0 0 V11 M40 11 V22" stroke="#251C1A" stroke-width="2"/></pattern>
<pattern id="clapboard" width="20" height="18" patternUnits="userSpaceOnUse"><rect width="20" height="18" fill="none"/><path d="M0 17 H20" stroke="#000" stroke-opacity=".12" stroke-width="2"/><path d="M0 2 H20" stroke="#fff" stroke-opacity=".25" stroke-width="2"/></pattern>
<pattern id="quilt" width="44" height="44" patternUnits="userSpaceOnUse"><rect width="44" height="44" fill="#E7DDC9"/><circle cx="11" cy="11" r="5" fill="#B66A5E"/><circle cx="33" cy="33" r="5" fill="#6E8E9E"/><path d="M0 22 H44 M22 0 V44" stroke="#CDBFA4" stroke-width="2" stroke-dasharray="4 4"/></pattern>
<pattern id="rug" width="60" height="60" patternUnits="userSpaceOnUse"><rect width="60" height="60" fill="#7A2E2A"/><path d="M30 6 L54 30 L30 54 L6 30 Z" fill="none" stroke="#C9A24A" stroke-width="3"/><circle cx="30" cy="30" r="6" fill="#2E4A5A"/></pattern>
</defs>"""


def svg(inner, w=960, h=1080, cls="fill", style=""):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" style="{style}">{inner}</svg>'


def obj_svg(inner, w, h, vb=None):
    vb = vb or f"{-w/2} {-h/2} {w} {h}"
    return f'<svg viewBox="{vb}" width="{w}" height="{h}" style="display:block; overflow:visible">{inner}</svg>'


# --- göktaşı: müzedeki gibi siyah, regmaglipt çukurlu, füzyon kabuğu
def rock2(s=1.0):
    """Müzedeki Hodges göktaşı gibi: köşeli, siyah füzyon kabuğu, yumuşak regmaglipt çukurları."""
    dents = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#0A0908" opacity=".5"/>' for x, y, rx, ry in [(-26, -24, 12, 8), (10, -36, 10, 6), (30, -6, 12, 8), (-8, 16, 13, 9), (22, 30, 9, 6)])
    return f'''<g transform="scale({s})" filter="url(#shadow)"><g filter="url(#grainy)"><g filter="url(#rough)">
<path d="M-62 -6 L-44 -48 L-6 -62 L38 -54 L62 -22 L58 22 L30 54 L-14 60 L-50 40 Z" fill="#1C1A17" stroke="#050404" stroke-width="3" stroke-linejoin="round"/>
<path d="M-44 -48 L-6 -62 L38 -54 L20 -18 L-18 -14 Z" fill="#5E5852"/>
<path d="M-62 -6 L-44 -48 L-18 -14 L-30 22 Z" fill="#46413C"/>
<path d="M20 -18 L38 -54 L62 -22 L58 22 L34 10 Z" fill="#2E2A26"/>
<path d="M-18 -14 L20 -18 L34 10 L10 34 L-30 22 Z" fill="#383430"/>
{dents}
<path d="M-44 -48 L-6 -62 L38 -54" stroke="#8A847E" stroke-width="3" fill="none" stroke-linecap="round" opacity=".6"/>
<path d="M-18 -14 L20 -18" stroke="#5A5550" stroke-width="2" opacity=".6"/></g></g></g>'''


def fireball2(s=1.0):
    return f'''<g transform="scale({s})"><path d="M0 0 L-620 -360 L-640 -320 Z" fill="url(#smoke)" filter="url(#dof)" opacity=".85"/>
<path d="M0 0 L-420 -250 L-430 -228 Z" fill="#FFC56A" opacity=".55" filter="url(#dof2)"/>
<circle r="110" fill="url(#fire2)" filter="url(#glow)"/><circle r="64" fill="url(#fire2)"/><circle r="22" fill="#FFFDF4"/></g>'''


def cloud(x, y, s=1.0, o=.9):
    return f'<g transform="translate({x} {y}) scale({s})" opacity="{o}" filter="url(#dof2)"><ellipse cx="0" cy="0" rx="120" ry="42" fill="#F7F4EE"/><ellipse cx="-60" cy="-20" rx="70" ry="44" fill="#FBF9F5"/><ellipse cx="50" cy="-28" rx="80" ry="52" fill="#FFFFFF"/><ellipse cx="10" cy="14" rx="140" ry="26" fill="#DCE3EA"/></g>'


def tree_autumn(x, y, s=1.0, seed=0, blur=False):
    cols = ["#B5652A", "#C9893A", "#8E4A22", "#A67C3A", "#6E7A3A", "#D4A04A"]
    shade = "".join(f'<circle cx="{((i*53+seed*17)%200)-100}" cy="{-((i*37+seed*29)%170)-30}" r="{30+(i*13)%26}" fill="{["#6E3A1C","#7A4A22","#4E5226"][i%3]}"/>' for i in range(18))
    mid = "".join(f'<circle cx="{((i*61+seed*23)%180)-90}" cy="{-((i*43+seed*31)%160)-50}" r="{22+(i*11)%20}" fill="{cols[(i+seed)%6]}"/>' for i in range(26))
    hl = "".join(f'<circle cx="{((i*41+seed*11)%150)-100}" cy="{-((i*29+seed*7)%140)-80}" r="{8+(i*7)%12}" fill="#F6CF78" opacity=".8"/>' for i in range(16))
    outer = ' filter="url(#dof)"' if blur else ''
    return f'<g transform="translate({x} {y}) scale({s})"{outer}><ellipse cx="0" cy="4" rx="100" ry="14" fill="#000" opacity=".25"/><path d="M-12 0 C-10 -60 -16 -100 -6 -150 L6 -150 C10 -100 14 -60 14 0 Z" fill="#4A3122" filter="url(#woodgrain)"/><path d="M0 -110 L-50 -170 M2 -120 L46 -175" stroke="#4A3122" stroke-width="9"/><g filter="url(#organic)">{shade}{mid}{hl}</g></g>'


def house2(x, y, s=1.0, idp="h2"):
    """1950'ler ABD evi, hafif açılı (ön yüz aydınlık, yan yüz gölgede), dokulu."""
    return f'''<g transform="translate({x} {y}) scale({s})" id="{idp}" filter="url(#grainy)">
<ellipse cx="40" cy="232" rx="420" ry="26" fill="#000" opacity=".25" filter="url(#dof2)"/>
<path d="M300 -40 L400 -70 L400 200 L300 230 Z" fill="url(#wallShade)" stroke="#2B2420" stroke-width="4"/><path d="M300 -40 L400 -70 L400 200 L300 230 Z" fill="url(#clapboard)"/>
<path d="M310 30 L380 10 L380 100 L310 122 Z" fill="url(#glass2)" stroke="#2B2420" stroke-width="5" opacity=".85"/>
<rect x="-300" y="-40" width="600" height="270" fill="url(#wallLit)" stroke="#2B2420" stroke-width="5"/><rect x="-300" y="-40" width="600" height="270" fill="url(#clapboard)"/>
<path d="M-340 -36 L0 -236 L300 -40 Z" fill="url(#shingles)" stroke="#1E140F" stroke-width="5" stroke-linejoin="round"/>
<path d="M0 -236 L120 -270 L430 -72 L300 -40 Z" fill="url(#shingles)" stroke="#1E140F" stroke-width="5" stroke-linejoin="round"/><path d="M0 -236 L120 -270 L430 -72 L300 -40 Z" fill="#000" opacity=".28"/>
<path d="M-340 -36 L300 -40" stroke="#E9E2D0" stroke-width="8"/>
<rect x="160" y="-238" width="48" height="120" fill="#8A3B2A" stroke="#2B1510" stroke-width="4"/><rect x="152" y="-250" width="64" height="16" fill="#6A2A1C"/>{''.join(f'<path d="M160 {-228+i*14} H208" stroke="#6A2A1C" stroke-width="2"/>' for i in range(8))}
<g id="{idp}-win"><rect x="-250" y="10" width="140" height="120" fill="url(#glass2)" stroke="#F4F0E6" stroke-width="12"/><path d="M-180 10 V130 M-250 70 H-110" stroke="#F4F0E6" stroke-width="7"/><path d="M-246 14 Q-216 70 -246 126 Z M-114 14 Q-144 70 -114 126 Z" fill="#D9A79A" opacity=".85"/><path d="M-240 20 L-200 20 L-238 90 Z" fill="#fff" opacity=".35"/><rect x="-262" y="128" width="164" height="12" fill="#E9E2D0"/><rect x="-270" y="10" width="18" height="120" fill="#2E4A3A"/><rect x="-108" y="10" width="18" height="120" fill="#2E4A3A"/></g>
<rect x="110" y="10" width="140" height="120" fill="url(#glass2)" stroke="#F4F0E6" stroke-width="12"/><path d="M180 10 V130 M110 70 H250" stroke="#F4F0E6" stroke-width="7"/><path d="M120 20 L160 20 L122 90 Z" fill="#fff" opacity=".35"/><rect x="92" y="10" width="18" height="120" fill="#2E4A3A"/><rect x="250" y="10" width="18" height="120" fill="#2E4A3A"/>
<path d="M-130 -10 H130 L146 -30 H-146 Z" fill="#EFE8D8" stroke="#2B2420" stroke-width="4"/><path d="M-146 -10 H146 V2 H-146 Z" fill="#000" opacity=".2"/>
<path d="M-60 230 V40 H60 V230" fill="url(#door2G)" stroke="#2B1510" stroke-width="5"/><rect x="-40" y="56" width="80" height="60" fill="url(#glass2)" stroke="#2B1510" stroke-width="4"/><circle cx="40" cy="150" r="8" fill="url(#brass)"/>
{''.join(f'<rect x="{px}" y="-12" width="16" height="242" fill="#F7F2E6" stroke="#2B2420" stroke-width="3"/><rect x="{px}" y="-12" width="5" height="242" fill="#000" opacity=".12"/>' for px in (-124, 108))}
<path d="M-140 230 H140 L150 246 H-150 Z" fill="#B8AE98" stroke="#2B2420" stroke-width="3"/><path d="M-150 246 H150 L160 262 H-160 Z" fill="#A69C86" stroke="#2B2420" stroke-width="3"/>
<path d="M-300 230 C-280 200 -250 210 -240 190 C-220 210 -200 200 -180 230 Z M180 230 C200 200 230 210 240 192 C260 210 280 204 300 230 Z" fill="#3E5A2A"/>
</g>'''


def car50s(s=1.0, color="#C8402F"):
    return f'''<g transform="scale({s})" filter="url(#shadow)">
<ellipse cx="0" cy="58" rx="250" ry="16" fill="#000" opacity=".35" filter="url(#dof2)"/>
<path d="M-240 30 C-244 -6 -224 -22 -180 -26 L-120 -30 C-96 -70 -60 -92 0 -94 C70 -94 104 -70 128 -30 L200 -24 C236 -20 250 0 246 30 Z" fill="{color}" stroke="#2A0E0A" stroke-width="5"/>
<path d="M-240 30 C-244 -6 -224 -22 -180 -26 L200 -24 C236 -20 250 0 246 30 Z" fill="#000" opacity=".12"/>
<path d="M-100 -32 C-80 -66 -50 -82 -6 -84 L-6 -32 Z" fill="url(#glass2)" stroke="#2A0E0A" stroke-width="4"/><path d="M6 -84 C56 -84 88 -66 112 -32 L6 -32 Z" fill="url(#glass2)" stroke="#2A0E0A" stroke-width="4"/>
<path d="M-236 6 H244" stroke="#E8ECEF" stroke-width="6"/><path d="M-236 6 H244" stroke="#9AA3AA" stroke-width="2"/>
<rect x="-250" y="22" width="40" height="16" rx="6" fill="#D9DEE2"/><rect x="216" y="20" width="40" height="16" rx="6" fill="#D9DEE2"/>
<circle cx="238" cy="-6" r="9" fill="#FFF3C4"/><path d="M-60 -20 H-30" stroke="#D9DEE2" stroke-width="4"/>
{''.join(f'<g transform="translate({wx} 34)"><circle r="40" fill="#141414"/><circle r="26" fill="#F2F2EE"/><circle r="18" fill="#BFC5CA"/><circle r="6" fill="#7A8086"/></g>' for wx in (-150, 150))}
</g>'''


def farmer2(s=1.0):
    return f'''<g transform="scale({s})" filter="url(#grainy)">
<ellipse cx="0" cy="118" rx="70" ry="12" fill="#000" opacity=".3"/>
<path d="M-34 14 L-40 110 H-12 L-4 40 L4 40 L12 110 H40 L34 14 Z" fill="#3E6496" stroke="#1E3354" stroke-width="3"/>
<path d="M-42 -78 C-20 -94 20 -94 42 -78 L50 20 H-50 Z" fill="#E7DCC4" stroke="#7A6A4A" stroke-width="3"/>
<path d="M-30 -60 H30 V24 H-30 Z" fill="#4A72A8" stroke="#1E3354" stroke-width="3"/><path d="M-30 -60 L-38 -84 M30 -60 L38 -84" stroke="#1E3354" stroke-width="7"/>
<rect x="-14" y="-40" width="28" height="22" rx="3" fill="#3A5F8F"/>
<path d="M-48 -70 C-70 -40 -72 -10 -64 20" stroke="#E7DCC4" stroke-width="22" stroke-linecap="round" fill="none"/><circle cx="-64" cy="24" r="12" fill="#6B4430"/>
<path d="M48 -70 C70 -40 72 -10 64 20" stroke="#E7DCC4" stroke-width="22" stroke-linecap="round" fill="none"/><circle cx="64" cy="24" r="12" fill="#6B4430"/>
<path d="M-12 -96 H12 V-80 H-12 Z" fill="#5A3826"/><ellipse cx="0" cy="-118" rx="25" ry="29" fill="#6B4430"/><path d="M-18 -112 Q0 -104 18 -112" stroke="#3A2010" stroke-width="2" fill="none"/>
<path d="M-56 -136 Q0 -152 56 -136 Q40 -128 0 -128 Q-40 -128 -56 -136 Z" fill="#D9B56A" stroke="#7A5A1E" stroke-width="3"/><path d="M-28 -136 Q0 -178 28 -136 Z" fill="#E3C47C" stroke="#7A5A1E" stroke-width="3"/><path d="M-27 -142 H27" stroke="#7A3A1E" stroke-width="5"/>
</g>'''


def person2(x, y, s=1.0, coat="#2E3B4E", hat=True, skin="#C98B63", seed=0):
    h = f'<path d="M-30 -136 Q0 -146 30 -136 L24 -150 Q0 -160 -24 -150 Z M-40 -134 H40" fill="#22262C" stroke="#22262C" stroke-width="6"/>' if hat else f'<path d="M-24 -128 Q0 -156 24 -128 Q20 -140 0 -142 Q-20 -140 -24 -128 Z" fill="#3A2A1E"/>'
    return f'''<g transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="110" rx="46" ry="9" fill="#000" opacity=".3"/>
<rect x="-30" y="16" width="24" height="92" rx="9" fill="#2A2A2E"/><rect x="6" y="16" width="24" height="92" rx="9" fill="#2A2A2E"/>
<path d="M-42 -84 C-20 -98 20 -98 42 -84 L48 30 H-48 Z" fill="{coat}"/><path d="M-42 -84 C-20 -98 0 -96 0 -96 L-6 30 H-48 Z" fill="#000" opacity=".18"/><path d="M0 -92 L-10 -40 L0 -30 L10 -40 Z" fill="#E9E2D0"/>
<ellipse cx="0" cy="-114" rx="22" ry="26" fill="{skin}"/><path d="M-22 -114 A22 26 0 0 0 0 -88 L0 -140 A22 26 0 0 0 -22 -114 Z" fill="#000" opacity=".12"/>{h}</g>'''


def gavel(s=1.0):
    return f'''<g transform="scale({s})" filter="url(#shadow)"><rect x="-14" y="-10" width="28" height="220" rx="12" fill="#6A3A1E" filter="url(#woodgrain)"/>
<rect x="-90" y="-50" width="180" height="80" rx="24" fill="#7A4424" stroke="#3A1E0E" stroke-width="4" filter="url(#woodgrain)"/><rect x="-96" y="-50" width="20" height="80" rx="8" fill="url(#brassBar)"/><rect x="76" y="-50" width="20" height="80" rx="8" fill="url(#brassBar)"/></g>'''
