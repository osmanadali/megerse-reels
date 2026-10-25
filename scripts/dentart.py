"""Diş / reklam seti çizimleri (toon dili: koyu kontur + düz renk + keskin gölge).

tooth(kind, h): azı ya da kesici diş, önden; taban (0,0) diş eti çizgisi, yukarı doğru kron. Sınıf .enamel (parlaklık animasyonu).
paste_tube(label, col, w, h): diş macunu tüpü, kapak altta; taban (0,0) ortada. Gerçek marka adı YOK: BRANDS'teki taklit adlar ya da "?".
BRANDS: taklit marka adı → (gövde, şerit) renkleri (Osman: Colgate hiç geçmez; diğerleri farklı yazılır).
gavel(), magnifier(r), boom_mic(), clapper(), director_chair(), cable(d): mahkeme/inceleme/stüdyo parçaları (taban 0,0).
studio_camera(), softbox(), set_flat(w, h): reklam çekim seti parçaları (taban 0,0).
mouth_corridor(cam, sid): depth.Scene ile ağız içi: iki yanda dişler, zeminde diş eti, tavanda damak (kamera dişlerin arasından ilerler).
"""
from toon import INK, cel, darker, lighter, line

ENAMEL, ENAMEL_SH = "#F7F4EC", "#D9D2C2"
GUM, GUM_SH = "#E98A93", "#C9636E"


BRANDS = {"NARVİS": ("#2F7FD8", "#FFFFFF"), "SENSODAYN": ("#E8577A", "#FFE3EA"), "İPENA": ("#1FA37A", "#FFFFFF"),
          "ORAL-P": ("#1F5FB8", "#E8423A"), "SİNYAL": ("#F2F2F2", "#E8423A"), "DENTİKS": ("#7A4FD0", "#FFFFFF"), "?": ("#B9C2CC", "#FFFFFF")}


def brand_tube(name, w=120, h=300):
    col, st = BRANDS[name]
    return paste_tube(name, col, w, h, st)


def tooth(kind="molar", h=200, col=ENAMEL, glow=False):
    s = h / 200
    if kind == "molar":
        crown = ("M-62 0 C-66 -40 -70 -90 -64 -140 C-60 -176 -40 -190 -22 -178 C-12 -192 12 -192 22 -178 C40 -190 60 -176 64 -140 "
                 "C70 -90 66 -40 62 0 Z")
        groove = "M-30 -176 Q-8 -150 0 -168 Q8 -150 30 -176"
    else:
        crown = "M-40 0 C-44 -60 -46 -130 -36 -180 C-28 -198 28 -198 36 -180 C46 -130 44 -60 40 0 Z"
        groove = "M-18 -176 Q0 -184 18 -176"
    hl = '<path d="M-38 -150 C-44 -110 -42 -60 -36 -20" stroke="#fff" stroke-width="10" stroke-linecap="round" fill="none" opacity=".85"/>'
    g = '<ellipse cx="0" cy="-90" rx="120" ry="130" fill="#FFF6C8" opacity=".55" filter="url(#glow)"/>' if glow else ""
    return (f'<g transform="scale({s:.3f})">{g}<g class="enamel">' + cel(crown, col, darker(col, .86), -1, 10, 4)
            + line(groove, 2.2, .45) + hl + '</g></g>')


def paste_tube(label="MARKA A", col="#2F7FD8", w=120, h=300, stripe="#FFFFFF"):
    """dik duran tüp: kapak altta (taban 0,0), kıvrık uç yukarıda."""
    hw = w / 2
    body = f"M{-hw} {-40} L{-hw*0.92} {-h+20} L{hw*0.92} {-h+20} L{hw} {-40} Z"
    crimp = f"M{-hw*0.95} {-h+20} L{-hw*0.95} {-h} L{hw*0.95} {-h} L{hw*0.95} {-h+20} Z"
    cap = f"M{-hw*0.55} 0 L{-hw*0.55} -40 L{hw*0.55} -40 L{hw*0.55} 0 Z"
    stripes = "".join(f'<path d="M{-hw*0.95} {-h+4+k*5} H{hw*0.95}" stroke="{darker(col, .7)}" stroke-width="1.6"/>' for k in range(3))
    return (cel(body, col, darker(col, .75), -1, 8, 4) + cel(crimp, lighter(col, .3), col, -1, 3, 3) + stripes
            + f'<path d="M{-hw*0.7} {-h*0.62} H{hw*0.7}" stroke="{stripe}" stroke-width="14" stroke-linecap="round"/>'
            + f'<rect x="{-hw*0.78}" y="{-h*0.5}" width="{w*0.78}" height="{h*0.2}" rx="8" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            + f'<text x="0" y="{-h*0.5 + h*0.13:.0f}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="{w*min(.17, 1.05/max(len(label), 1)):.0f}" fill="{darker(col, .6)}">{label}</text>'
            + cel(cap, "#F4F1EA", "#CFCAC0", -1, 4, 3))


def studio_camera():
    """tripod üstünde sinema kamerası (taban 0,0, boy ~420)."""
    return (line("M0 -230 L-70 0 M0 -230 L70 0 M0 -230 L0 0", 7, 1, "#2A2C33")
            + cel("M-90 -330 L70 -330 L70 -232 L-90 -232 Z", "#2E3440", "#1E232B", -1, 8, 4)
            + cel("M70 -312 L130 -330 L130 -232 L70 -250 Z", "#1E232B", "#14181E", -1, 4, 4)
            + '<circle cx="134" cy="-281" r="34" fill="#0B0E12" stroke="#1B1414" stroke-width="5"/><circle cx="128" cy="-290" r="10" fill="#5AB8FF" opacity=".7"/>'
            + cel("M-60 -380 L0 -380 L0 -330 L-60 -330 Z", "#2E3440", "#1E232B", -1, 4, 3)
            + '<circle cx="-70" cy="-280" r="8" fill="#FF4D4D"/>')


def softbox():
    """ışık: tripod + parlayan kutu (taban 0,0, boy ~520)."""
    return (line("M0 -380 L-60 0 M0 -380 L60 0 M0 -380 L0 0", 6, 1, "#2A2C33")
            + '<ellipse cx="0" cy="-450" rx="150" ry="110" fill="#FFF6D8" opacity=".35" filter="url(#glow)"/>'
            + cel("M-90 -520 L90 -520 L70 -380 L-70 -380 Z", "#3A3F48", "#262A31", -1, 6, 4)
            + '<path d="M-72 -505 L72 -505 L56 -395 L-56 -395 Z" fill="#FFF8E6"/>')


def set_flat(w=900, h=900):
    """reklam dekoru (ön yüz): parlak banyo fayansı + ayna + lavabo; taban (0,0) alt orta."""
    hw = w / 2
    tiles = "".join(f'<rect x="{-hw + c*90 + (r % 2)*45 - 45}" y="{-h + r*60}" width="86" height="56" rx="6" fill="#EAF6FA" stroke="#B9D8E4" stroke-width="3"/>'
                    for r in range(int(h / 60)) for c in range(int(w / 90) + 2))
    return (f'<defs><clipPath id="setclip"><rect x="{-hw}" y="{-h}" width="{w}" height="{h}"/></clipPath></defs>'
            f'<g clip-path="url(#setclip)"><rect x="{-hw}" y="{-h}" width="{w}" height="{h}" fill="#DDF0F6"/>{tiles}</g>'
            + cel(f"M{-hw*0.45} {-h*0.86} L{hw*0.45} {-h*0.86} L{hw*0.45} {-h*0.42} L{-hw*0.45} {-h*0.42} Z", "#CFE4EC", "#A9C6D2", -1, 10, 6)
            + cel(f"M{-hw*0.55} {-h*0.3} L{hw*0.55} {-h*0.3} L{hw*0.45} {-h*0.2} L{-hw*0.45} {-h*0.2} Z", "#FFFFFF", "#D9DEE2", -1, 6, 5)
            + f'<rect x="{-hw}" y="{-h}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="8"/>')


def set_back(w=900, h=900):
    """dekorun arkası: ahşap çıta iskelet, kablolar, bant (taban 0,0 alt orta)."""
    hw = w / 2
    wood, wsh = "#C9A46A", "#A07E48"
    bars = "".join(cel(f"M{-hw + k*w/4 - 14} {-h} L{-hw + k*w/4 + 14} {-h} L{-hw + k*w/4 + 14} 0 L{-hw + k*w/4 - 14} 0 Z", wood, wsh, -1, 4, 3) for k in range(5))
    rails = "".join(cel(f"M{-hw} {-h + k*h/3 - 12} L{hw} {-h + k*h/3 - 12} L{hw} {-h + k*h/3 + 12} L{-hw} {-h + k*h/3 + 12} Z", wood, wsh, -1, 3, 3) for k in range(1, 3))
    return (f'<rect x="{-hw}" y="{-h}" width="{w}" height="{h}" fill="#7A6A56" stroke="{INK}" stroke-width="8"/>' + rails + bars
            + line(f"M{-hw*0.8} -10 C{-hw*0.5} -200 {-hw*0.1} -40 {hw*0.3} -260 S {hw*0.7} -120 {hw*0.9} -30", 6, 1, "#1B1414")
            + f'<rect x="{hw*0.2}" y="{-h*0.62}" width="120" height="34" fill="#E8C94A" transform="rotate(-8 {hw*0.2} {-h*0.62})"/>')


def mouth_corridor(cam, sid="mc", n=14, gap=170, z0=260, dz=210):
    """ağız içi koridor: iki yanda azı dişleri, ortada boşluk; zemin diş eti, tavan damak (svg arkasında degrade ile verilir)."""
    from depth import Scene
    sc = Scene(cam, sid, ground=(GUM_SH, GUM), sky=False)
    for k in range(n):
        z = z0 + k * dz
        for side in (-1, 1):
            art = (f'<path d="M-90 30 C-90 -10 -70 -24 0 -24 C70 -24 90 -10 90 30 Z" fill="{GUM}" stroke="{INK}" stroke-width="4"/>'
                   + tooth("molar", 200) + f'<path d="M-74 4 C-60 -14 60 -14 74 4" stroke="{GUM_SH}" stroke-width="10" fill="none" stroke-linecap="round"/>')
            sc.add(side * (gap + (k % 2) * 10), z, art, 230, 150, shadow=False)
    return sc


def gavel():
    """yandan hakim tokmağı + ses tablası (taban 0,0). Tokmak (.gvh) vuruş anında: baş tablaya değer.
    Kaldırmak için .gvh'yi sapın ucu (230,-79) etrafında döndür (svgOrigin "230 -79", rotation -35)."""
    base = cel("M-110 0 L110 0 L96 -34 L-96 -34 Z", "#7A4A2A", "#5A3218", -1, 6, 4)
    head = ('<g class="gvh">' + cel("M30 -86 L232 -86 L232 -72 L30 -72 Z", "#9A6A3A", "#6A4220", -1, 3, 3)
            + cel("M-46 -124 L46 -124 L46 -34 L-46 -34 Z", "#8A5A2E", "#5A3218", -1, 8, 4)
            + cel("M-50 -112 L50 -112 L50 -100 L-50 -100 Z", "#C9A46A", "#A07E48", -1, 2, 3)
            + cel("M-50 -58 L50 -58 L50 -46 L-50 -46 Z", "#C9A46A", "#A07E48", -1, 2, 3) + "</g>")
    return base + head


def magnifier(r=150):
    """büyüteç: mercek merkezi (0,0), sap sağ alta."""
    return (f'<path d="M{r*.7:.0f} {r*.7:.0f} L{r*1.6:.0f} {r*1.6:.0f}" stroke="#1B1414" stroke-width="{r*.3:.0f}" stroke-linecap="round"/>'
            + f'<path d="M{r*.75:.0f} {r*.75:.0f} L{r*1.55:.0f} {r*1.55:.0f}" stroke="#3A2A20" stroke-width="{r*.2:.0f}" stroke-linecap="round"/>'
            + f'<circle r="{r}" fill="#CFEFFF" fill-opacity=".12" stroke="#1B1414" stroke-width="{r*.16:.0f}"/>'
            + f'<circle r="{r*.92:.0f}" fill="none" stroke="#9AA6B2" stroke-width="{r*.06:.0f}"/>'
            + f'<path d="M{-r*.55:.0f} {-r*.35:.0f} A{r*.65:.0f} {r*.65:.0f} 0 0 1 {-r*.1:.0f} {-r*.62:.0f}" stroke="#fff" stroke-width="{r*.07:.0f}" fill="none" stroke-linecap="round" opacity=".8"/>')


def boom_mic(reach=480, h=900):
    """direk (taban 0,0, boy h) + sola uzanan kol + aşağı bakan tüylü mikrofon (mikrofon ucu ~(-reach, -h+40))."""
    mx, my = -reach, -h + 10
    return (line(f"M0 0 L0 {-h} M-50 0 L0 -60 L50 0 M0 {-h} L{mx} {my}", 7, 1, "#2A2C33")
            + f'<g transform="translate({mx} {my})">' + cel("M-26 0 C-26 -10 26 -10 26 0 L26 90 C26 104 -26 104 -26 90 Z", "#6A6E78", "#4A4E56", -1, 6, 4)
            + "".join(line(f"M-26 {10 + k*11} l-9 3 M26 {10 + k*11} l9 3", 2, .7, "#8A8E98") for k in range(8)) + "</g>")


def clapper():
    """klaket (taban 0,0; ~200 geniş)."""
    stripes = "".join(f'<path d="M{-100 + k*40} -150 L{-80 + k*40} -150 L{-100 + k*40 + 30} -190 L{-120 + k*40 + 30} -190 Z" fill="#fff"/>' for k in range(5))
    return (cel("M-100 0 L100 0 L100 -140 L-100 -140 Z", "#1E232B", "#14181E", -1, 6, 4)
            + '<g transform="rotate(-14 -100 -146)">' + cel("M-100 -146 L100 -146 L100 -194 L-100 -194 Z", "#1E232B", "#14181E", -1, 3, 3) + stripes + "</g>"
            + line("M-90 -96 H90 M-90 -56 H90", 2, .7, "#9AA6B2")
            + '<text x="-84" y="-108" font-family="Mont" font-weight="800" font-size="22" fill="#fff">SAHNE 1</text>'
            + '<text x="-84" y="-70" font-family="Mont" font-weight="800" font-size="22" fill="#fff">ÇEKİM 9</text>')


def director_chair(label="YÖNETMEN"):
    """yönetmen sandalyesi (taban 0,0)."""
    return (line("M-70 0 L60 -150 M70 0 L-60 -150", 9, 1, "#7A4A2A")
            + cel("M-80 -150 L80 -150 L80 -120 L-80 -120 Z", "#1E232B", "#14181E", -1, 3, 3)
            + line("M-70 -150 L-70 -260 M70 -150 L70 -260", 9, 1, "#7A4A2A")
            + cel("M-80 -260 L80 -260 L80 -205 L-80 -205 Z", "#1E232B", "#14181E", -1, 3, 3)
            + f'<text x="0" y="-222" text-anchor="middle" font-family="Mont" font-weight="800" font-size="24" fill="#FFD23F">{label}</text>')


def cable(d, w=7):
    return f'<path d="{d}" stroke="#0B0D12" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
