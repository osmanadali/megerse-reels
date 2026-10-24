"""Saç / kıl folikülü çizimleri (toon dili: koyu kontur + düz renk + keskin gölge).

follicle(grey=False): kafa derisi kesiti; epidermis, dermis, yağ dokusu, folikül, soğan (bulb), papilla,
  melanositler (pigment hücreleri), çıkıntı (bulge) kök hücreleri, yağ bezi, kıl dikleştirici kas, kan damarı.
  Yerel koordinat: deri yüzeyi y=0, x=0 folikül ekseni; genişlik ~760, derinlik ~1000.
  Sınıflar (animasyon için): .pg pigment taneleri, .mc melanositler, .sc kök hücreleri, .shaft saç teli.
scalp_hairs(...): makro kafa derisi yüzeyi (perspektifli Scene için tek tel çizimi).
"""
import math

from toon import INK, cel, darker, line

SKIN = "#E9B996"
DERM = "#F2C4B0"
FAT = "#F6DE8A"


def _rnd(i, a=1.0):
    return ((i * 9301 + 49297) % 233280) / 233280 * a


def follicle(grey=False, stem_ok=True, pid="f", hair_col="#2A1C14", show_labels=False):
    shaft_col = "#F2F2EE" if grey else hair_col
    out = []
    # katmanlar
    out.append(cel("M-380 1000 L-380 60 L380 60 L380 1000 Z", DERM, darker(DERM, .9), -1, 20, 5))
    out.append("".join(f'<ellipse cx="{-380+(i%8)*100+(i//8)%2*50}" cy="{900+(i//8)*60}" rx="54" ry="34" fill="{FAT}" stroke="{INK}" stroke-width="3"/>' for i in range(24)))
    out.append(cel("M-380 60 L-380 0 L380 0 L380 60 Z", SKIN, darker(SKIN, .85), -1, 6, 5))
    out.append("".join(f'<path d="M{-380+i*38} 0 q19 30 0 60" stroke="{darker(SKIN,.8)}" stroke-width="2" fill="none" opacity=".6"/>' for i in range(21)))
    # kan damarı (papillaya)
    out.append(line("M380 960 C200 940 140 900 60 870 C20 860 0 850 0 840", 9, 1, "#B23A3A") + line("M380 975 C210 955 150 915 70 885", 5, .7, "#D9605A"))
    # kıl dikleştirici kas
    out.append(cel("M44 380 C120 300 200 180 250 60 L280 66 C232 190 150 318 64 400 Z", "#D9806A", "#B8604A", -1, 4, 3))
    # yağ bezi
    out.append(cel("M-58 230 C-140 200 -190 250 -170 310 C-150 360 -90 350 -60 320 Z", "#F7E7B0", "#D9C48A", -1, 8, 4)
               + "".join(f'<circle cx="{-130+_rnd(i,60)}" cy="{260+_rnd(i+7,70)}" r="9" fill="#EBD58E" stroke="{INK}" stroke-width="1.5"/>' for i in range(6)))
    # dış kök kını (folikül tüpü) + soğan
    out.append(cel("M-62 0 L-62 760 C-120 780 -130 900 -60 930 C-20 948 20 948 60 930 C130 900 120 780 62 760 L62 0 Z", "#F7D7C4", "#D9B49E", -1, 10, 5))
    out.append(cel("M-40 0 L-40 770 C-90 790 -96 890 -44 912 C-14 924 14 924 44 912 C96 890 90 790 40 770 L40 0 Z", "#FBE6D8", "#E2C4B0", -1, 6, 3))
    # papilla
    out.append(cel("M-40 930 C-56 880 -40 832 0 826 C40 832 56 880 40 930 Z", "#D9605A", "#B23A3A", -1, 6, 4))
    # saç teli (soğandan yukarı, deriden dışarı)
    shaft = f"M-17 -420 L-17 800 C-40 812 -36 830 -24 832 C-10 806 10 806 24 832 C36 830 40 812 17 800 L17 -420 Z"
    out.append(f'<g class="shaft">{cel(shaft, shaft_col, darker(shaft_col, .75), -1, 6, 4)}</g>')
    # pigment taneleri (yukarı akar)
    if not grey:
        out.append('<g class="pgs">' + "".join(f'<circle class="pg" cx="{-10+_rnd(i,20):.1f}" cy="{790-i*34}" r="{3+_rnd(i+3,3):.1f}" fill="#4A2A14"/>' for i in range(24)) + "</g>")
    # melanositler (yıldız hücre) — papilla üstünde
    mcs = []
    for i, (x, y) in enumerate([(-44, 812), (-24, 798), (24, 798), (44, 812), (0, 792)]):
        dend = "".join(f'<path d="M{x} {y} l{math.cos(a)*22:.1f} {math.sin(a)*22:.1f}" stroke="{"#7A4A2A" if not grey else "#B9B4A8"}" stroke-width="4" stroke-linecap="round"/>' for a in [k * math.pi / 3 + i for k in range(6)])
        body = f'<circle cx="{x}" cy="{y}" r="11" fill="{"#8A5A34" if not grey else "#D9D6CF"}" stroke="{INK}" stroke-width="2.5"/>'
        mcs.append(f'<g class="mc">{dend}{body}</g>')
    if not grey or not stem_ok:
        out.append("".join(mcs) if not grey else "")
    # çıkıntı (bulge) kök hücreleri
    sc = "".join(f'<circle class="sc" cx="{(-74 if i % 2 else 74)}" cy="{360+(i//2)*26}" r="12" fill="{"#7FC6E8" if stem_ok else "#9AA4AE"}" stroke="{INK}" stroke-width="2.5"/>' for i in range(6))
    out.append(f'<g class="scs">{sc}</g>')
    if show_labels:
        lab = lambda x, y, t, ax, ay: (f'<path d="M{ax} {ay} L{x} {y}" stroke="#fff" stroke-width="3"/>'
                                       f'<text x="{x + (8 if x > ax else -8)}" y="{y+10}" text-anchor="{"start" if x > ax else "end"}" font-family="Mont" font-weight="800" font-size="34" fill="#fff" stroke="#000" stroke-width="6" paint-order="stroke">{t}</text>')
        out.append(lab(170, 360, "kök hücreler", 86, 370) + lab(-170, 800, "pigment hücreleri", -50, 805) + lab(170, 900, "kıl kökü", 60, 900))
    return "".join(out)


def hair_strand(white=False, h=420, bend=0.0, seed=0):
    """Kafa derisinden çıkan tek tel (makro). Taban (0,0); kalınlık ~14."""
    col = "#EEEEEA" if white else ["#1E1612", "#2A1C14", "#241A12"][seed % 3]
    dx = bend * h
    d = f"M-7 0 C-7 {-h*.4:.0f} {dx*.6-7:.0f} {-h*.75:.0f} {dx-4:.0f} {-h} L{dx+4:.0f} {-h} C{dx*.6+7:.0f} {-h*.75:.0f} 7 {-h*.4:.0f} 7 0 Z"
    hl = f'<path d="M-2 -10 C-2 {-h*.4:.0f} {dx*.6-2:.0f} {-h*.75:.0f} {dx-1:.0f} {-h+6}" stroke="#fff" stroke-opacity="{.5 if white else .22}" stroke-width="2.4" fill="none"/>'
    pore = f'<ellipse cx="0" cy="2" rx="12" ry="5" fill="{darker(SKIN,.7)}" stroke="{INK}" stroke-width="2"/>'
    return pore + f'<path d="{d}" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>' + hl


def tweezers(open_=0.0):
    """Cımbız: uçlar (0,0), sap yukarı-sağa; uzunluk ~120."""
    o = open_ * 8
    return (f'<g transform="rotate(-35)">'
            + cel(f"M-2 0 L-6 -110 L4 -120 L2 0 Z", "#C9CDD2", "#8A9096", -1, 2, 2.5)
            + f'<g transform="rotate({o})">' + cel(f"M2 0 L10 -116 L18 -110 L6 0 Z", "#DDE1E6", "#9AA0A6", -1, 2, 2.5) + "</g>"
            + '<path d="M-4 -100 L14 -104" stroke="#8A9096" stroke-width="3"/></g>')


def bathroom_bg(W=1080, H=1920):
    """Banyo: metro fayans duvar, aynanın çerçevesi (iç kısmı boş: yansıma ayrı katman), lavabo, üstte lamba ışığı."""
    tiles = "".join(f'<rect x="{(c*120 + (r%2)*60) - 60}" y="{r*60}" width="116" height="56" rx="6" fill="#E6EEF0" stroke="#B9C8CC" stroke-width="3"/>' for r in range(33) for c in range(11))
    mirror = (cel("M140 300 L940 300 L940 1300 L140 1300 Z", "#C9D2D6", "#9AA8AE", -1, 18, 8)
              + '<rect x="170" y="330" width="740" height="940" rx="10" fill="#9FB8C2" stroke="#1B1414" stroke-width="6"/>')
    lamp = (cel("M380 220 L700 220 L680 270 L400 270 Z", "#F2EBDD", "#C9C0AE", -1, 6, 6)
            + '<ellipse cx="540" cy="290" rx="260" ry="40" fill="#FFF3C8" opacity=".55" filter="url(#glow)"/>')
    sink = (cel("M60 1520 L1020 1520 L1020 1600 L60 1600 Z", "#F4F6F7", "#C9D0D4", -1, 10, 7)
            + cel("M260 1600 Q540 1820 820 1600 Z", "#E9EEF0", "#B9C4C8", -1, 14, 7)
            + cel("M500 1440 L520 1380 L620 1380 L620 1410 L540 1410 L530 1520 L500 1520 Z", "#C9CDD2", "#8A9096", -1, 6, 5))
    return f'<rect width="{W}" height="{H}" fill="#DCE6E9"/>{tiles}{mirror}{lamp}{sink}'


def mirror_glass():
    """aynanın üstüne konan cam parlaması (yansıma katmanının üstünde)."""
    return ('<path d="M190 360 L360 360 L190 620 Z" fill="#fff" opacity=".22"/><path d="M420 360 L470 360 L190 790 L190 714 Z" fill="#fff" opacity=".14"/>'
            '<rect x="170" y="330" width="740" height="940" rx="10" fill="none" stroke="#1B1414" stroke-width="6"/>')
