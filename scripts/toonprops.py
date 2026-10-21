"""Çizgi film stilinde yol ve araç parçaları (toon.py ile aynı kontur + keskin gölge dili).
Hepsi tabanı (0,0) olan, dünya birimiyle (cm) ölçeklenecek çizimler; depth.Scene.add ile yerleştirilir."""
from toon import cel, darker, line

CAR_H = 150


def car_rear(col="#C8402F", brake=False, seed=0):
    """Arkadan araba (kuyrukta bekleyen), genişlik ~180, yükseklik 150."""
    tl = "#FF3A2A" if brake else "#9A2A22"
    glow = '<ellipse cx="-62" cy="-70" rx="26" ry="14" fill="#FF5A3A" opacity=".55" filter="url(#glow)"/><ellipse cx="62" cy="-70" rx="26" ry="14" fill="#FF5A3A" opacity=".55" filter="url(#glow)"/>' if brake else ""
    rack = cel("M-60 -152 L60 -152 L56 -146 L-56 -146 Z", "#3A3A3A", "#1A1A1A", -1, 1, 3) if seed % 3 == 0 else ""
    bag = cel("M-40 -168 L36 -168 L40 -152 L-44 -152 Z", ["#2E6A9A", "#C89048", "#6A3A6A"][seed % 3], "#1A1A1A", -1, 3, 3) if seed % 3 == 0 else ""
    return (cel("M-86 -20 L-90 -86 C-88 -96 -80 -100 -70 -100 L-56 -140 C-52 -146 52 -146 56 -140 L70 -100 C80 -100 88 -96 90 -86 L86 -20 Z", col, darker(col), -1, 12, 4)
            + cel("M-50 -134 L50 -134 L62 -104 L-62 -104 Z", "#2A3A48", "#1A242E", -1, 6, 3)
            + '<path d="M-44 -128 L-20 -128 L-34 -108 L-52 -108 Z" fill="#fff" opacity=".18"/>'
            + cel("M-84 -84 L-46 -84 L-46 -58 L-84 -60 Z", tl, darker(tl), -1, 3, 3) + cel("M84 -84 L46 -84 L46 -58 L84 -60 Z", tl, darker(tl), -1, 3, 3)
            + '<rect x="-28" y="-62" width="56" height="16" rx="2" fill="#F4F1EA" stroke="#1B1414" stroke-width="3"/><rect x="-28" y="-62" width="8" height="16" fill="#2A4A9A"/>'
            + line("M-16 -54 H18", 2, .8)
            + cel("M-90 -22 L90 -22 L88 -6 L-88 -6 Z", "#2A2A2A", "#121212", -1, 2, 4)
            + cel("M-84 -6 L-56 -6 L-56 0 L-84 0 Z", "#141414", "#000", -1, 1, 3) + cel("M56 -6 L84 -6 L84 0 L56 0 Z", "#141414", "#000", -1, 1, 3)
            + glow + rack + bag)


def heat_shimmer(y, w=960):
    """Asfalt üstü sıcak hava dalgası (yarı saydam)."""
    return "".join(f'<path class="heat" d="M0 {y+i*10} Q120 {y+i*10-6} 240 {y+i*10} T480 {y+i*10} T720 {y+i*10} T960 {y+i*10}" stroke="#fff" stroke-opacity=".12" stroke-width="3" fill="none"/>' for i in range(4))


def toll_booth(lanes=6):
    """Otoyol gişesi: kanopi + kabinler, taban (0,0), genişlik lanes*400."""
    W = lanes * 400
    canopy = cel(f"M{-W/2-60} -620 L{W/2+60} -620 L{W/2+40} -540 L{-W/2-40} -540 Z", "#E9E4DA", "#B9B2A4", -1, 30, 6)
    sign = "".join(f'<rect x="{-W/2+i*400+120}" y="-605" width="160" height="50" rx="8" fill="{"#2A9A5A" if i % 2 else "#2A5AB0"}" stroke="#1B1414" stroke-width="5"/>'
                   f'<text x="{-W/2+i*400+200}" y="-568" text-anchor="middle" font-family="Mont" font-weight="800" font-size="32" fill="#fff">{"HGS" if i % 2 else "OGS"}</text>' for i in range(lanes))
    cabins = "".join(cel(f"M{-W/2+i*400-40} 0 L{-W/2+i*400-40} -300 L{-W/2+i*400+40} -300 L{-W/2+i*400+40} 0 Z", "#D9D2C2", "#A8A08E", -1, 10, 5)
                     + cel(f"M{-W/2+i*400-30} -280 L{-W/2+i*400+30} -280 L{-W/2+i*400+30} -200 L{-W/2+i*400-30} -200 Z", "#7AA8C8", "#4A7898", -1, 4, 4)
                     + f'<rect x="{-W/2+i*400-14}" y="-540" width="28" height="240" fill="#B9B2A4" stroke="#1B1414" stroke-width="5"/>'
                     + f'<circle cx="{-W/2+i*400}" cy="-320" r="14" fill="{"#3AD06A" if i % 2 else "#FFB02A"}" stroke="#1B1414" stroke-width="4"/>' for i in range(lanes + 1))
    lights = "".join(f'<ellipse cx="{-W/2+i*200}" cy="-536" rx="40" ry="10" fill="#FFF3C8" opacity=".85"/>' for i in range(lanes * 2 + 1))
    return cabins + canopy + sign + lights


def tunnel_portal(w=1400, h=900):
    """Dağ yamacında tünel ağzı (iki tüp), taban (0,0)."""
    hill = cel(f"M{-w*1.4} 0 C{-w} {-h*1.6} {-w*.3} {-h*2} 0 {-h*1.9} C{w*.4} {-h*2} {w} {-h*1.5} {w*1.4} 0 Z", "#6A8A4A", "#4A6A34", -1, 60, 6)
    portal = "".join(cel(f"M{cx-280} 0 L{cx-280} -420 Q{cx} -700 {cx+280} -420 L{cx+280} 0 Z", "#D9D2C2", "#A8A08E", -1, 20, 6)
                     + cel(f"M{cx-220} 0 L{cx-220} -390 Q{cx} -620 {cx+220} -390 L{cx+220} 0 Z", "#141414", "#000", -1, 2, 5)
                     + "".join(f'<circle cx="{cx-150+j*100}" cy="-430" r="10" fill="#FFE08A"/>' for j in range(4)) for cx in (-320, 320))
    return hill + portal


def viaduct(span=1200, n=4, h=700):
    """Vadi üstü viyadük: tabliye + ayaklar, taban (0,0) = ayak dibi; tabliye y=-h."""
    W = span * n
    piers = "".join(cel(f"M{-W/2+i*span-50} 0 L{-W/2+i*span-70} {-h} L{-W/2+i*span+70} {-h} L{-W/2+i*span+50} 0 Z", "#D9D2C2", "#A8A08E", -1, 16, 6) for i in range(n + 1))
    deck = cel(f"M{-W/2-100} {-h-60} L{W/2+100} {-h-60} L{W/2+100} {-h} L{-W/2-100} {-h} Z", "#E9E4DA", "#B9B2A4", -1, 6, 6)
    rail = f'<path d="M{-W/2-100} {-h-80} H{W/2+100}" stroke="#1B1414" stroke-width="8"/>' + "".join(f'<path d="M{x} {-h-80} V{-h-60}" stroke="#1B1414" stroke-width="5"/>' for x in range(int(-W/2-100), int(W/2+100), 120))
    return piers + deck + rail
