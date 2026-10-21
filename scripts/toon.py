"""2D çizgi film karakter kütüphanesi (Osman'ın referansı: hf/assets/ref/stil-1.avif).

Stil kuralları:
- Koyu, sürekli dış kontur (INK), iç ayrıntılar daha ince çizgi.
- Düz renk + tek ton keskin gölge (cel shading): gölge, ışığın tersindeki kenarda sert sınırlı şerit.
- Büyük baş (boy/5), iri gözler: beyaz göz + koyu iris + ağır üst kapak (yarı kapalı bakış), kalın kaş.
- Eller beş parmaklı ve açık; kıyafette kıvrım çizgileri, dikiş, cep, kemer tokası; spor ayakkabıda taban, burun, bağcık.
Koordinat: ayak tabanı (0,0), boy ~175 birim (TOON_H). Varsayılan üç-çeyrek sağa bakar; flip=True sola.
"""
import itertools
import math

INK = "#1B1414"
TOON_H = 175
_ids = itertools.count()


def _uid(p="t"):
    return f"{p}{next(_ids)}"


def cel(d, base, shade, light=-1, depth=4.0, lw=1.15, ink=INK, extra=""):
    """Tek parça: düz renk + ışığın tersinde keskin gölge şeridi + kontur.
    light=-1: ışık soldan (gölge sağ kenarda). depth: gölge şeridi kalınlığı."""
    cid = _uid("c")
    return (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
            f'<path d="{d}" fill="{shade}"/>'
            f'<g clip-path="url(#{cid})"><path d="{d}" fill="{base}" transform="translate({light*depth:.2f} {-depth*.35:.2f})"/>{extra}</g>'
            f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{lw}" stroke-linejoin="round"/>')


def line(d, w=.7, op=1.0, col=INK):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="round" stroke-linejoin="round"/>'


def darker(hexc, f=.72):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (int(r * f), int(g * f * .97), int(b * f * 1.02 if b * f * 1.02 < 255 else 255))


# ---------------- el ----------------
def hand(x, y, ang=0, s=1.0, skin="#F2C9A0", light=-1, pose="open", mirror=False):
    """Beş parmaklı el. Bilek (x,y), ang: kolun yönü (derece, 0 = aşağı). pose: open (açık, hafif aralık) | fist | point | hold."""
    sh = darker(skin)
    if pose == "fist":
        d = "M-5 0 C-7 6 -7 12 -4 15 L5 15 C8 12 8 5 5 0 Z"
        body = cel(d, skin, sh, light, 2) + line("M-4 9 H5 M-4 12 H5", .5)
    else:
        fingers = {"open": [(-3.6, 14.2, 10), (-1.3, 15.6, 3), (1.0, 15.2, -3), (3.2, 13.2, -10)],
                   "point": [(-1.3, 16.5, 0), (-3.4, 9.5, 4), (1.0, 9, -2), (3.2, 8.5, -6)],
                   "hold": [(-3.6, 10, 4), (-1.3, 11, 1), (1.0, 11, -1), (3.2, 10, -4)]}[pose]
        parts = []
        for fx, ln, a in fingers:
            fd = f"M{fx-1.1:.2f} 5 L{fx-1.0:.2f} {ln-1:.2f} Q{fx:.2f} {ln+.5:.2f} {fx+1.0:.2f} {ln-1:.2f} L{fx+1.1:.2f} 5 Z"
            parts.append(f'<g transform="rotate({a} {fx:.2f} 5)">{cel(fd, skin, sh, light, .7, .7)}{line(f"M{fx-.8:.2f} {5+(ln-5)*.5:.2f} H{fx+.8:.2f}", .35, .5)}</g>')
        thumb = cel("M-4.2 1.5 C-6.6 3.4 -7.6 6.6 -7.2 8.8 C-6.9 10 -5.6 10 -5.2 8.8 C-4.8 7 -4 5.8 -3 5 Z", skin, sh, light, .7, .7)
        palm = cel("M-4.6 0 C-5 2 -5 4.4 -4.6 6.2 C-1.6 7.2 1.6 7.2 4.4 6.2 C4.8 4.4 4.8 2 4.3 0 Z", skin, sh, light, 1.1, .8)
        body = "".join(parts) + palm + thumb
    m = " scale(-1 1)" if mirror else ""
    return f'<g transform="translate({x:.2f} {y:.2f}) rotate({ang:.1f}) scale({s}){m}">{body}</g>'


# ---------------- ayakkabı ----------------
def sneaker(x, y, s=1.0, col="#7FA9D6", light=-1, toward=1):
    """Kanvas spor ayakkabı, yandan-üç-çeyrek; toward=1 burun sağa."""
    up = "M-7 -9 C-8 -5 -8 -2 -7 0 L12 0 C16 0 18 -2 17 -4 C14 -6 8 -6 4 -9 C1 -11 -4 -11 -7 -9 Z"
    sole = "M-8 -1 L18 -1 C19 1 18 3 16 3 L-7 3 C-9 3 -9 0 -8 -1 Z"
    toe = "M9 -5.6 C13 -6 17 -5 17.4 -3 C17 -1.6 15 -1.2 12 -1.2 C10 -1.2 9 -3 9 -5.6 Z"
    laces = line("M1 -9 L6 -6 M2.6 -10 L7.4 -6.8 M0 -8 L5 -9.6 M2 -6.2 L6 -8.4", .45)
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s*toward} {s})">'
            + cel(up, col, darker(col), light * toward, 1.6, .9) + cel(toe, "#F4F1EA", "#CFCAC0", light, .8, .7)
            + cel(sole, "#F4F1EA", "#CFCAC0", light, .6, .9) + line("M-8 1 H18", .4, .6) + laces
            + f'<circle cx="-4.5" cy="-6" r=".9" fill="#E9E4DA" stroke="{INK}" stroke-width=".4"/></g>')


# ---------------- karakter ----------------
def toon_figure(flip=False, pose="stand", look=(1, 0), expr=None, skin="#F2C9A0", hair="#16110F",
                shirt="#7A1E22", sleeve="#F4F1EA", pants="#8A7A5A", shoes="#7FA9D6", socks=True, shorts=True,
                vest=None, earring=False, light_from_left=True, female=False, hair_style="short"):
    """Tam boy üç-çeyrek karakter (referans stil). look=(gx,gy): göz bebeği yönü (-1..1, yüz yönüne göre).
    expr: lid (0 açık .. 1 kapalı; .45 ağır kapak), smile (-1..1), talk (0..1 ağız açık), brow (-1..1).
    pose: stand (eller açık yanda) | talk (yakın el jest) | point | walk | hands_pockets."""
    e = dict(lid=.42, smile=.5, talk=0, brow=0)
    e.update(expr or {})
    L = (-1 if light_from_left else 1) * (-1 if flip else 1)     # yansıtılmış grupta ışık dünyaya göre sabit
    sk, skS = skin, darker(skin, .8)
    out = []

    # --- bacaklar, çorap, ayakkabı (uzak bacak önce)
    walk = pose == "walk"
    far_x, near_x = (9, -4) if not walk else (14, -10)
    leg_col = pants if not shorts else sk
    for lx, far in ((far_x, True), (near_x, False)):
        knee_y = -42
        top = -78 if not shorts else -50
        d = f"M{lx-5:.1f} {top} L{lx-4.4:.1f} -10 L{lx+4.4:.1f} -10 L{lx+5.4:.1f} {top} Z"
        g = cel(d, leg_col, darker(leg_col), L, 2.2, 1.0)
        if not shorts:
            g += line(f"M{lx-1:.1f} {knee_y-3} q2 3 0 6 M{lx+2:.1f} -22 q-1 3 1 5", .5, .6)
        if socks:
            sd = f"M{lx-4.6:.1f} -24 L{lx-4.4:.1f} -9 L{lx+4.4:.1f} -9 L{lx+4.6:.1f} -24 Z"
            g += cel(sd, "#F4F1EA", "#CFCAC0", L, 1.4, .9) + f'<path d="M{lx-4.6:.1f} -22 H{lx+4.6:.1f} M{lx-4.6:.1f} -19.6 H{lx+4.6:.1f}" stroke="#8A1E22" stroke-width="1.1"/>'
        g += sneaker(lx - 2 + (3 if far else 0), 0 if not walk or far else -1, .95 if far else 1.0, shoes, L, 1)
        out.append(f'<g style="filter:brightness({.9 if far else 1})">{g}</g>')

    # --- şort / pantolon üst kısmı + kemer
    if shorts:
        sd = "M-11 -84 L-12 -48 L1 -46 L3 -62 L5 -46 L17 -48 L16 -84 Z"
        out.append(cel(sd, pants, darker(pants), L, 3, 1.1) + line("M3 -80 L3 -62 M-8 -60 q4 2 8 0 M8 -58 q4 2 7 -1", .5, .7)
                   + cel("M6 -72 H15 V-58 H6 Z", pants, darker(pants), L, 1.2, .7) + line("M6 -69.5 H15", .5) + line("M7 -66 h7", .35, .5, "#000"))
    else:
        out.append(cel("M-11 -84 L-11 -74 L17 -74 L16 -84 Z", pants, darker(pants), L, 3, 1.1))
    out.append(cel("M-11.4 -86 L16.4 -86 L16.2 -82 L-11.2 -82 Z", "#8A6A3A", "#6A4E28", L, 1, .8)
               + '<rect x="0.5" y="-86.6" width="5" height="5.2" rx=".6" fill="#D9B14A" stroke="#1B1414" stroke-width=".6"/>')

    # --- uzak kol (gövde arkasında)
    hx_far = 18
    far_arm = cel("M13 -120 C17 -118 19 -112 19 -104 L20 -84 L16.6 -84 L15 -104 Z", sk, skS, L, 1.4, 1.0)
    out.append(f'<g style="filter:brightness(.88)">{far_arm}{hand(hx_far - 1.6, -85, -8, .95, sk, L, "open")}</g>')

    # --- gövde: tişört/atlet + kollar
    torso = "M-14 -121 C-16 -110 -14 -96 -12 -84 L16 -84 C17 -96 17 -110 14 -121 C8 -124 -8 -124 -14 -121 Z"
    out.append(cel(torso, shirt, darker(shirt), L, 3.2, 1.15)
               + line("M-10 -98 q2 3 1 6 M10 -100 q-2 4 0 8 M-4 -86 q3 -2 6 0", .5, .55)
               + line("M-12.5 -112 L-11 -103 M12 -110 l1 4", .4, .35, "#000"))
    if vest:
        out.append(cel("M-12 -118 L-2 -100 L5 -118 L13 -119 L15 -86 L-11 -86 Z", vest, darker(vest), L, 3, 1.0))
    out.append(cel("M-3 -122 Q2 -117 7 -122 L6 -124 Q2 -121 -2 -124 Z", sleeve, "#CFCAC0", L, .6, .8))   # yaka
    # yakın kol
    nsl = cel("M-14 -121 C-21 -120 -24 -112 -24 -104 L-15 -102 Z", sleeve, "#CFCAC0", L, 1.6, 1.05)
    if pose == "talk":
        arm = cel("M-21 -104 L-24 -92 C-22 -88 -17 -88 -12 -92 L-2 -98 L-4 -101 L-14 -96 L-17 -104 Z", sk, skS, L, 1.4, 1.0)
        out.append(arm + nsl + hand(-1, -99.5, -125, 1.0, sk, L, "open"))
    elif pose == "point":
        arm = cel("M-21 -104 L-6 -112 L-5 -108 L-17 -100 Z", sk, skS, L, 1.2, 1.0)
        out.append(arm + nsl + hand(-4, -111, -112, 1.0, sk, L, "point"))
    elif pose == "hands_pockets":
        arm = cel("M-21 -104 L-20 -86 L-13 -82 L-15 -102 Z", sk, skS, L, 1.4, 1.0)
        out.append(arm + nsl)
    else:
        sw = 6 if walk else 0
        arm = cel(f"M-22.5 -104 L{-25-sw*.3:.1f} -86 L{-21-sw*.3:.1f} -86 L-16 -103 Z", sk, skS, L, 1.4, 1.0)
        out.append(arm + nsl + hand(-23 - sw * .3, -87, 12 + sw, 1.0, sk, L, "open"))

    # --- boyun + baş (üç-çeyrek sağa)
    out.append(cel("M-3.5 -132 L-3.4 -121 Q1 -119 5.6 -121 L5.2 -132 Z", sk, skS, L, 1.6, 1.0))
    head = ("M-16 -158 C-17 -150 -16.6 -142 -13.5 -137 C-10 -131 -4 -127.6 2.5 -127.4 C8 -127.6 13 -131 15.4 -137 "
            "C17.4 -142 18 -150 17.4 -158 C16 -170 8 -175 0 -174.6 C-9 -174 -15 -168 -16 -158 Z")
    out.append(cel(head, sk, skS, L, 2.6, 1.15))
    # kulak (yakın taraf)
    ear = cel("M-15.6 -152 C-20.6 -153.6 -21.6 -144 -16.8 -141.4 C-15.6 -141 -14.6 -142 -14.6 -143 Z", sk, skS, L, 1, .9) + line("M-17 -149.5 q-2.2 2 .3 5", .5, .7)
    if earring:
        ear += f'<circle cx="-17.4" cy="-140.6" r="1.4" fill="none" stroke="#C9C4B8" stroke-width=".8"/><circle cx="-17.4" cy="-140.6" r="1.4" fill="none" stroke="{INK}" stroke-width=".3"/>'
    out.append(ear)
    # saç
    if female:
        hp = ("M-18 -150 C-21 -166 -10 -178 2 -177 C14 -177 21 -168 19 -152 C18 -140 20 -128 16 -118 L10 -122 C13 -132 14 -146 12 -156 "
              "C8 -160 0 -162 -6 -160 C-10 -158 -12 -152 -13 -146 C-14 -136 -12 -126 -14 -118 L-20 -122 C-17 -132 -17 -142 -18 -150 Z")
    elif hair_style == "short":
        hp = ("M-16.6 -152 C-18.6 -166 -10 -177 2 -176.6 C13 -176.4 19 -168 18 -156 C16.6 -158.6 14 -160 11 -160 "
              "C6 -160.4 0 -160 -5 -159 C-9 -158.4 -11.6 -156 -12.6 -151 C-13 -148 -13.4 -146 -14.2 -145 C-15.8 -147 -16.4 -149.6 -16.6 -152 Z")
    else:
        hp = "M-16.6 -152 C-18.6 -168 -8 -178 2 -177 C14 -177 20 -168 18 -156 C14 -160 4 -162 -6 -160 C-10 -158 -13 -152 -14.2 -145 Z"
    out.append(cel(hp, hair, "#000000", L, 1.4, 1.1) + line("M-6 -172 Q2 -175 10 -171", 1.6, .5, "#5A5050"))
    # gözler: beyaz + iris + ağır üst kapak + kaş
    gx, gy = look
    lid = e["lid"]
    for cx, w, far in ((-3.0, 4.6, False), (9.6, 3.9, True)):
        cy = -150
        sc = f"M{cx-w:.2f} {cy:.2f} C{cx-w*.7:.2f} {cy-4.6:.2f} {cx+w*.7:.2f} {cy-4.6:.2f} {cx+w:.2f} {cy:.2f} C{cx+w*.7:.2f} {cy+4.2:.2f} {cx-w*.7:.2f} {cy+4.2:.2f} {cx-w:.2f} {cy:.2f} Z"
        cid = _uid("e")
        ix, iy = cx + gx * w * .35, cy + .4 + gy * 1.2
        lid_y = cy - 3.6 + lid * 6.4
        out.append(f'<clipPath id="{cid}"><path d="{sc}"/></clipPath><path d="{sc}" fill="#FBF9F4"/>'
                   f'<g clip-path="url(#{cid})"><circle cx="{ix:.2f}" cy="{iy:.2f}" r="{w*.5:.2f}" fill="#2A1C14"/><circle cx="{ix:.2f}" cy="{iy:.2f}" r="{w*.24:.2f}" fill="#0A0606"/>'
                   f'<circle cx="{ix-w*.18:.2f}" cy="{iy-w*.2:.2f}" r="{w*.12:.2f}" fill="#fff"/>'
                   f'<path d="M{cx-w-1:.2f} {cy-6:.2f} H{cx+w+1:.2f} V{lid_y:.2f} Q{cx:.2f} {lid_y+1.4:.2f} {cx-w-1:.2f} {lid_y:.2f} Z" fill="{sk}"/>'
                   f'<path d="M{cx-w-1:.2f} {lid_y:.2f} Q{cx:.2f} {lid_y+1.4:.2f} {cx+w+1:.2f} {lid_y:.2f}" stroke="{skS}" stroke-width="1.6" fill="none"/></g>'
                   f'<path d="{sc}" fill="none" stroke="{INK}" stroke-width=".7"/>'
                   + line(f"M{cx-w-.4:.2f} {lid_y-.2:.2f} Q{cx:.2f} {lid_y+1.2:.2f} {cx+w+.4:.2f} {lid_y-.4:.2f}", 1.3)               # ağır kapak çizgisi
                   + line(f"M{cx-w*.8:.2f} {cy-6.2:.2f} Q{cx:.2f} {cy-7.4:.2f} {cx+w*.9:.2f} {cy-5.8:.2f}", .5, .5)                 # kapak kıvrımı
                   + line(f"M{cx-w*.6:.2f} {cy+5.2:.2f} Q{cx:.2f} {cy+6:.2f} {cx+w*.6:.2f} {cy+5:.2f}", .45, .45))                # göz altı
        by = cy - 8.4 - e["brow"] * 1.6
        bw = w * 1.15
        out.append(f'<path d="M{cx-bw:.2f} {by+1.2:.2f} Q{cx:.2f} {by-1.8:.2f} {cx+bw:.2f} {by+.6:.2f} L{cx+bw:.2f} {by+2:.2f} Q{cx:.2f} {by-.2:.2f} {cx-bw:.2f} {by+2.6:.2f} Z" fill="{hair}"/>')
    # burun (üç-çeyrek: yüz yönüne çıkıntı) + ağız
    out.append(line("M7.4 -147 C9.4 -143.6 10.6 -141.8 9.6 -140.6 C8.6 -139.8 7.2 -140.2 6.4 -140.8", .75))
    sm, tk = e["smile"], e["talk"]
    if tk > .05:
        md = f"M-.4 {-134.6-sm:.2f} Q4 {-133.6+tk*3:.2f} 8.6 {-135.2-sm:.2f} Q4 {-134+tk*1.2:.2f} -.4 {-134.6-sm:.2f} Z"
        out.append(f'<path d="{md}" fill="#5A1E1A" stroke="{INK}" stroke-width=".6"/>')
    else:
        out.append(line(f"M-.4 {-134.8-sm*.6:.2f} Q4 {-133.2+sm*1.6:.2f} 8.6 {-135.6-sm*1.4:.2f}", .75))
    out.append(line(f"M8.6 {-135.6-sm*1.4:.2f} q1 -.2 1.4 -1", .5, .7))

    body = "".join(out)
    return f'<g transform="scale(-1 1)">{body}</g>' if flip else f'<g>{body}</g>'
