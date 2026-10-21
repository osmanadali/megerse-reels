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


def lighter(hexc, f=.35):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(c + (255 - c) * f) for c in (r, g, b))


def _fringe(pts):
    """Saç çizgisi tutamları: (taban, uç, taban, uç...) noktalarından yumuşak sivri kıvrımlar."""
    d = ""
    for i in range(1, len(pts) - 1, 2):
        (bx, by), (tx, ty), (nx, ny) = pts[i - 1], pts[i], pts[i + 1]
        d += f" Q{(bx+tx)/2:.1f} {(by+ty)/2-1.2:.1f} {tx:.1f} {ty:.1f} Q{(tx+nx)/2+.6:.1f} {(ty+ny)/2-1.6:.1f} {nx:.1f} {ny:.1f}"
    return d


HAIR_STYLES = ("short", "fade", "quiff", "balding", "long", "bob")


def hair_parts(style, col, L=-1):
    """Saç: (arka, ön) döndürür. arka: gövdenin arkasına (uzun saç), ön: başın üstüne; kulak önün üstüne çizilir.
    Baş üç-çeyrek sağa; ense/arka solda (x<0), yüz sağda."""
    hl, sh = lighter(col, .28), darker(col, .6) if col != "#16110F" else "#000000"
    back, strands, shine = "", "", ""
    if style == "short":        # referans 1: düz üst, öne yatık kısa perçem, favoriler, ense
        d = ("M-17.2 -141 C-21.4 -146 -22.8 -156 -21.2 -163.5 C-19.4 -172.6 -11 -181 0 -181.2 C10.4 -181.6 18.6 -177 19.8 -169 "
             "C20.6 -165 19.8 -161 18.4 -158.2"
             + _fringe([(18.4, -158.2), (15.6, -157.4), (13.4, -161.6), (11.2, -157.8), (8.4, -162.2), (5.4, -158.6), (2.2, -162.6), (-1.4, -159.4), (-5.4, -162)])
             + " C-8.6 -161.4 -10.8 -159.6 -11.8 -156.4 L-12.2 -150 L-14.8 -148.6 C-15.4 -151 -16 -153.4 -16.6 -153.6 Z")
        strands = line("M-3 -178.6 Q6 -173 10.6 -162.6 M-9 -176 Q-2 -170 1.4 -163.4 M5 -180 Q14 -175.6 15.6 -163 M-15 -171 Q-20 -162 -19.2 -150 M-12 -174 Q-15 -166 -14 -156", .55, .8)
        shine = f'<path d="M-15.6 -167 Q-9 -177.6 4 -178.6 Q-2 -176 -4 -173.6 L-6.6 -175 L-8 -171.4 L-11 -172.6 L-12 -168.6 Z" fill="{hl}"/>'
    elif style == "fade":       # referans 2: kafaya yakın kısa üst, net saç çizgisi + şakak köşesi, yanlar açık (fade)
        d = ("M-16.8 -143 C-20.4 -148 -21 -158 -19.4 -165 C-17 -173.6 -9 -178.6 1 -178.6 C10 -178.6 17 -174.6 18.6 -167 "
             "C19 -164 18.8 -161.6 18 -160 L14.6 -160.4 C12 -162.4 6 -163 0 -162.6 C-5 -162.4 -9 -161.4 -10.4 -159.4 "
             "L-11.6 -156 L-12.4 -150 L-14.8 -148.6 C-15.4 -151 -16 -153.4 -16.6 -153.6 Z")
        fade = (f'<path d="M-12.4 -156 L-12.4 -150 L-14.8 -148.6 C-15.4 -151 -16 -153.4 -16.6 -153.6 L-16.8 -143 C-20.4 -148 -21 -156 -20.4 -160 Z" '
                f'fill="{col}" opacity=".5"/>')
        strands = fade + "".join(f'<circle cx="{x}" cy="{y}" r=".45" fill="{hl}"/>' for x, y in [(-8, -172), (-4, -175), (2, -176), (8, -174), (12, -170), (-12, -168), (-2, -170), (5, -168.6), (10, -165.4), (-6, -166)])
        shine = f'<path d="M-14 -169 Q-6 -177 4 -176.8 Q-4 -174.6 -8 -172 Z" fill="{hl}" opacity=".8"/>'
    elif style == "quiff":      # yukarı ve geriye taranmış hacimli ön (1950'ler)
        d = ("M-17.2 -141 C-21.6 -146 -23 -157 -21.4 -165 C-19.6 -174 -12 -181.4 -2 -183 C6 -186 15 -187 21.4 -182 "
             "C24 -179.4 22.6 -175.4 19.4 -174.6 C21 -171 20.6 -165 18.6 -160.4 C15 -163 9 -164.6 2 -164.2 C-4 -164 -9 -162.4 -11.2 -159 "
             "L-12.2 -150 L-14.8 -148.6 C-15.4 -151 -16 -153.4 -16.6 -153.6 Z")
        strands = line("M-14 -168 Q-4 -180 14 -184 M-12 -163 Q0 -176 19 -178 M-8 -164 Q4 -172 18 -170 M-16 -158 Q-20 -152 -19 -146", .55, .8)
        shine = f'<path d="M-10 -174 Q2 -183.4 16 -184 Q6 -181 -2 -177.6 L-4 -179 L-6 -175 Z" fill="{hl}"/>'
    elif style == "balding":    # yaşlı: tepe açık, yanlarda ve ensede saç
        d = ("M-17.2 -141 C-19.6 -145 -19.8 -152 -18.8 -158 C-18 -162 -16.4 -164.4 -15.2 -163.4 C-14.2 -160 -13 -155 -12.2 -150 "
             "L-14.8 -148.6 C-15.4 -151 -16 -153.4 -16.6 -153.6 Z")
        strands = line("M-17.6 -158 Q-18.4 -151 -17.4 -145 M-15.6 -160 Q-16 -154 -14.8 -150", .5, .7) + \
            cel("M16.4 -164 C18.6 -162 19 -158 18 -154 L16.8 -155 Z", col, sh, L, .6, .9)
        shine = ""
    elif style == "long":       # kadın: yandan ayrık, yüzü çerçeveleyen, omuz arkasına uzun
        back = cel("M-21 -160 C-26 -140 -26 -112 -23 -96 L-18 -100 L-15 -94 L-10 -99 L4 -99 L10 -95 L14 -100 L19 -97 C22 -112 23 -140 20 -160 Z", col, sh, L, 2.4, 1.1)
        d = ("M-19.4 -150 C-22.6 -166 -12 -182 2 -182 C15.6 -182 22.6 -170 21.4 -156 C21 -146 22 -134 20.4 -122 "
             "L18.4 -116.6 L17 -122.6 L14.8 -118.6 C15.8 -132 16.6 -146 15.4 -156 C12.6 -161.6 7 -163.6 2.4 -163.4 "
             "Q-5 -163 -9.8 -157 C-12 -151 -12.6 -144 -13.4 -136 C-14 -128 -14 -120 -15 -113 L-17.4 -117.6 L-19.6 -111.6 L-20.6 -120 "
             "C-21.6 -132 -20.2 -142 -19.4 -150 Z")
        strands = line("M3 -181 Q1.6 -172 2 -163.6 M-3 -179 Q-14 -170 -17 -150 Q-18 -130 -17.4 -118 M-8 -170 Q-13 -160 -14 -140 "
                       "M9 -180 Q18 -172 18.6 -150 Q19 -132 18.2 -120 M6 -177 Q14 -168 15.8 -158", .55, .8)
        shine = f'<path d="M-16 -166 Q-8 -179 2 -180 Q-4 -177 -8 -173 L-10.6 -174.4 L-12 -170.4 L-14.6 -171 Z" fill="{hl}"/>'
    elif style == "bob":        # kadın kısa küt
        back = cel("M-21 -160 C-25 -146 -24 -132 -21 -126 L18 -126 C22 -134 22 -148 20 -160 Z", col, sh, L, 2, 1.1)
        d = ("M-19.6 -150 C-22.6 -167 -12 -182 2 -182 C15.6 -182 22.6 -170 21.4 -156 C21.2 -146 21.6 -136 20 -128 L15.4 -128 "
             "C16 -140 16.4 -150 15.2 -156 C11 -160 4 -161 -2 -160.4 Q-8 -160 -10.6 -156 C-12.4 -148 -12.8 -138 -13.4 -128 L-19.4 -128 "
             "C-21 -136 -20.4 -144 -19.6 -150 Z")
        strands = line("M-2 -181 Q-10 -172 -16 -150 Q-17.6 -138 -17 -130 M8 -180 Q17 -170 18 -150 Q18.6 -138 18 -130", .55, .8)
        shine = f'<path d="M-16 -166 Q-8 -179 2 -180 Q-4 -177 -8 -173 L-10.6 -174.4 L-12 -170.4 L-14.6 -171 Z" fill="{hl}"/>'
    front = cel(d, col, sh, L, 1.4, 1.1) + shine + strands
    return back, front


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


def oxford(x, y, s=1.0, col="#2A1C14", light=-1):
    """Deri klasik ayakkabı (takım elbise)."""
    d = "M-6 -6 C-6.6 -3 -6.4 -1 -6 0 L13 0 C16.4 0 17.4 -1.6 16.4 -3.2 C13.6 -5.4 8 -5.6 4 -7 C1 -8 -4 -8 -6 -6 Z"
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s})">' + cel(d, col, darker(col, .6), light, 1.4, .9)
            + f'<path d="M7 -5.2 Q11 -5.6 14.6 -3.6" stroke="#fff" stroke-opacity=".35" stroke-width=".9" fill="none"/>' + line("M-6.4 -.6 H16", .6, .8) + "</g>")


def boot(x, y, s=1.0, col="#141010", light=-1):
    """Uzun konçlu asker çizmesi (dizin altına kadar)."""
    d = "M-5.2 -30 L-5 -6 C-6 -3 -6 -1 -5.6 0 L13 0 C16 0 17 -1.6 16 -3.2 C13.4 -5.2 8 -5.6 5 -7 L5.4 -30 Z"
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s})">' + cel(d, col, "#000", light, 1.6, 1.0)
            + f'<path d="M-3.6 -28 L-3.2 -10" stroke="#fff" stroke-opacity=".22" stroke-width="1.4"/>' + line("M-5.8 -.6 H15.6", .6, .8) + "</g>")


def hat_parts(hat, L):
    if hat == "fedora":
        return (cel("M-24 -170.6 C-22 -173.6 22 -174.6 26 -171 C24 -168.4 -20 -167.4 -24 -170.6 Z", "#3A3430", "#221E1B", L, 1, 1.0)
                + cel("M-15 -171 C-15.6 -182 -10 -188.6 2 -188.6 C14 -188.6 18.6 -182 18.4 -171.6 C10 -170 -6 -170 -15 -171 Z", "#4A423C", "#2A2420", L, 2, 1.1)
                + cel("M-15.2 -174.6 C-6 -173.4 10 -173.4 18.6 -175 L18.5 -171.8 C10 -170.4 -6 -170.4 -15.1 -171.4 Z", "#1E1A18", "#000", L, .5, .8)
                + line("M-2 -187.4 Q2 -184 6 -187.6", .6, .6))
    if hat == "officer":
        return (cel("M-16.4 -172 C-19 -178 -14 -186 2 -187 C18 -187.6 24 -182 22 -176 C14 -173 -6 -172.4 -16.4 -172 Z", "#5E6450", "#3E4334", L, 2, 1.1)
                + cel("M-15.6 -175.4 C-6 -173.8 10 -173.8 20 -175.6 L19.6 -170.8 C10 -169.6 -6 -169.6 -15.4 -170.6 Z", "#2A2C24", "#121410", L, .6, .9)
                + cel("M8 -171 C14 -171.4 22 -170 26 -167 C20 -165.6 12 -166.4 6 -168.4 Z", "#0E0E0E", "#000", L, .4, .9)
                + '<rect x="0" y="-174.2" width="3.6" height="2.6" rx=".4" fill="#C9C4B8" stroke="#1B1414" stroke-width=".4"/>')
    return ""


# ---------------- karakter ----------------
def toon_figure(flip=False, pose="stand", look=(1, 0), expr=None, skin="#F2C9A0", hair="#16110F",
                shirt="#7A1E22", sleeve="#F4F1EA", pants="#8A7A5A", shoes="#7FA9D6", socks=True, shorts=True,
                vest=None, earring=False, light_from_left=True, female=False, hair_style=None,
                outfit="tee", jacket="#2E3440", tie="#7A1E22", hat=None, prop=None):
    """Tam boy üç-çeyrek karakter (referans stil). look=(gx,gy): göz bebeği yönü (-1..1, yüz yönüne göre).
    expr: lid (0 açık .. 1 kapalı; .45 ağır kapak), smile (-1..1), talk (0..1 ağız açık), brow (-1..1).
    pose: stand (eller açık yanda) | talk (yakın el jest) | point | walk | hands_pockets | offer (eli ileri uzatır: prop=paper ile liste).
    outfit: tee | suit (ceket, gömlek, kravat, deri ayakkabı) | uniform (gri subay ceketi, kemer, cepler, çizme; simgesiz) | dress (kadın elbise).
    hat: fedora | officer. prop: paper | suitcase."""
    e = dict(lid=.42, smile=.5, talk=0, brow=0)
    e.update(expr or {})
    L = (-1 if light_from_left else 1) * (-1 if flip else 1)     # yansıtılmış grupta ışık dünyaya göre sabit
    sk, skS = skin, darker(skin, .8)
    hs = hair_style or ("long" if female else "short")
    hair_back, hair_front = hair_parts(hs, hair, L)
    out = [hair_back]
    long_sl = outfit in ("suit", "uniform")
    if outfit in ("suit", "uniform", "dress"):
        shorts, socks = False, False
    if outfit in ("uniform", "suit"):
        pants = jacket
    arm_col, arm_sh = (jacket, darker(jacket)) if long_sl else (sk, skS)
    sleeve_col = jacket if long_sl else (shirt if outfit == "dress" else sleeve)

    # --- bacaklar, çorap, ayakkabı (uzak bacak önce)
    walk = pose == "walk"
    far_x, near_x = (9, -4) if not walk else (14, -10)
    leg_col = pants if not (shorts or outfit == "dress") else sk
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
        fx_, fs_ = lx - 2 + (3 if far else 0), .95 if far else 1.0
        if outfit == "uniform":
            g += boot(fx_, 0, fs_, "#141010", L)
        elif outfit in ("suit", "dress"):
            g += oxford(fx_, 0, fs_, shoes if outfit == "dress" else "#2A1C14", L)
        else:
            g += sneaker(fx_, 0 if not walk or far else -1, fs_, shoes, L, 1)
        out.append(f'<g style="filter:brightness({.9 if far else 1})">{g}</g>')

    # --- şort / pantolon üst kısmı + kemer
    if shorts:
        sd = "M-11 -84 L-12 -48 L1 -46 L3 -62 L5 -46 L17 -48 L16 -84 Z"
        out.append(cel(sd, pants, darker(pants), L, 3, 1.1) + line("M3 -80 L3 -62 M-8 -60 q4 2 8 0 M8 -58 q4 2 7 -1", .5, .7)
                   + cel("M6 -72 H15 V-58 H6 Z", pants, darker(pants), L, 1.2, .7) + line("M6 -69.5 H15", .5) + line("M7 -66 h7", .35, .5, "#000"))
    else:
        out.append(cel("M-11 -84 L-11 -74 L17 -74 L16 -84 Z", pants, darker(pants), L, 3, 1.1))
    if outfit == "tee":
        out.append(cel("M-11.4 -86 L16.4 -86 L16.2 -82 L-11.2 -82 Z", "#8A6A3A", "#6A4E28", L, 1, .8)
                   + '<rect x="0.5" y="-86.6" width="5" height="5.2" rx=".6" fill="#D9B14A" stroke="#1B1414" stroke-width=".6"/>')

    # --- uzak kol (gövde arkasında)
    hx_far = 18
    far_arm = cel("M13 -120 C17 -118 19 -112 19 -104 L20 -84 L16.6 -84 L15 -104 Z", arm_col, arm_sh, L, 1.4, 1.0)
    if outfit == "suit":
        far_arm += cel("M16.4 -87 L20.2 -87 L20.1 -84.4 L16.6 -84.4 Z", "#F4F1EA", "#CFCAC0", L, .4, .6)
    out.append(f'<g style="filter:brightness(.88)">{far_arm}{hand(hx_far - 1.6, -85, -8, .95, sk, L, "open")}</g>')

    # --- gövde: tişört/atlet + kollar
    torso = "M-14 -121 C-16 -110 -14 -96 -12 -84 L16 -84 C17 -96 17 -110 14 -121 C8 -124 -8 -124 -14 -121 Z"
    coat = "M-14.6 -121 C-16.6 -108 -15.4 -88 -14.4 -71 L18.2 -71 C18.2 -88 17.6 -108 14.6 -121 C8 -124 -8 -124 -14.6 -121 Z"
    if outfit == "suit":
        out.append(cel(coat, jacket, darker(jacket), L, 3.2, 1.15)
                   + cel("M-3.4 -123 L1.6 -103 L6.8 -123 Z", "#F4F1EA", "#CFCAC0", L, .6, .8)
                   + cel("M.8 -121 L3.6 -121 L4.4 -104.6 L2.3 -100.6 L.2 -104.6 Z", tie, darker(tie), L, .6, .7)
                   + line("M-3.4 -123 L-2 -110 L1.6 -100 M6.8 -123 L5.4 -111 L1.6 -100", .8)
                   + line("M1.6 -100 L1.8 -71", .6, .8)
                   + '<circle cx="3.2" cy="-92" r=".9" fill="#1B1414"/><circle cx="3.2" cy="-82" r=".9" fill="#1B1414"/>'
                   + line("M-11.6 -96 q2 3 .6 6 M11 -98 q-2 4 0 8 M8.6 -114 h4", .5, .55)
                   + cel("M9 -114.6 L12.6 -114.6 L12.4 -112.6 L9 -112.8 Z", "#F4F1EA", "#CFCAC0", L, .3, .4))
    elif outfit == "uniform":
        out.append(cel(coat, jacket, darker(jacket), L, 3.2, 1.15)
                   + line("M2.4 -119 L2.6 -71", .6, .8) + "".join(f'<circle cx="3.6" cy="{y}" r=".8" fill="#B9B4A8" stroke="#1B1414" stroke-width=".3"/>' for y in (-114, -106, -98, -80))
                   + cel("M-11 -114 L-3 -114 L-3 -108 L-11 -108 Z", jacket, darker(jacket), L, .6, .6) + cel("M7 -114 L14 -114 L14 -108 L7 -108 Z", jacket, darker(jacket), L, .6, .6)
                   + cel("M-12 -82 L-3 -82 L-3 -74 L-12 -74 Z", jacket, darker(jacket), L, .6, .6) + cel("M7 -82 L16 -82 L16 -74 L7 -74 Z", jacket, darker(jacket), L, .6, .6)
                   + cel("M-14.8 -90 L18 -90 L18 -86.2 L-14.8 -86.2 Z", "#2A1E16", "#120C08", L, .6, .8)
                   + '<rect x="0" y="-90.6" width="5" height="5" rx=".6" fill="#8E8A7E" stroke="#1B1414" stroke-width=".5"/>'
                   + cel("M-4.4 -125 L-3.6 -119 L8 -119 L8.6 -125 Q2 -122.6 -4.4 -125 Z", darker(jacket, .8), darker(jacket, .6), L, .6, .8)
                   + '<rect x="-3" y="-123.4" width="3" height="2.4" fill="#C9C4B8" stroke="#1B1414" stroke-width=".3"/><rect x="4" y="-123.4" width="3" height="2.4" fill="#C9C4B8" stroke="#1B1414" stroke-width=".3"/>'
                   + cel("M-15 -121.6 L-8 -123 L-8 -120.4 L-15.4 -119 Z", darker(jacket, .8), darker(jacket, .6), L, .4, .6))
    elif outfit == "dress":
        dress = "M-14 -121 C-16 -110 -14 -98 -12 -88 C-16 -72 -19 -58 -20 -46 L24 -46 C22 -58 19 -72 16 -88 C17 -98 17 -110 14 -121 C8 -124 -8 -124 -14 -121 Z"
        out.append(cel(dress, shirt, darker(shirt), L, 3.6, 1.15)
                   + cel("M-13 -90 L16.2 -90 L16 -86.6 L-12.6 -86.6 Z", darker(shirt, .6), darker(shirt, .45), L, .5, .7)
                   + line("M-8 -70 q1 10 -2 22 M4 -72 L5 -48 M14 -70 q2 10 4 22", .5, .55)
                   + cel("M-5 -123 Q2 -116 9 -123 L8 -125 Q2 -120 -4 -125 Z", "#F4F1EA", "#CFCAC0", L, .5, .8))
    else:
        out.append(cel(torso, shirt, darker(shirt), L, 3.2, 1.15)
                   + line("M-10 -98 q2 3 1 6 M10 -100 q-2 4 0 8 M-4 -86 q3 -2 6 0", .5, .55)
                   + line("M-12.5 -112 L-11 -103 M12 -110 l1 4", .4, .35, "#000"))
    if vest:
        out.append(cel("M-12 -118 L-2 -100 L5 -118 L13 -119 L15 -86 L-11 -86 Z", vest, darker(vest), L, 3, 1.0))
    if outfit == "tee":
        out.append(cel("M-3 -122 Q2 -117 7 -122 L6 -124 Q2 -121 -2 -124 Z", sleeve, "#CFCAC0", L, .6, .8))   # yaka
    # yakın kol
    nsl = cel("M-14 -121 C-21 -120 -24 -112 -24 -104 L-15 -102 Z", sleeve_col, darker(sleeve_col, .8), L, 1.6, 1.05)
    cuff = (lambda x, y, a: f'<g transform="translate({x:.2f} {y:.2f}) rotate({a:.1f})">' + cel("M-2.6 -1.4 L2.6 -1.4 L2.4 1.4 L-2.4 1.4 Z", "#F4F1EA", "#CFCAC0", L, .3, .5) + "</g>") if outfit == "suit" else (lambda x, y, a: "")
    if pose == "talk":
        arm = cel("M-21 -104 L-24 -92 C-22 -88 -17 -88 -12 -92 L-2 -98 L-4 -101 L-14 -96 L-17 -104 Z", arm_col, arm_sh, L, 1.4, 1.0)
        out.append(arm + nsl + hand(-1, -99.5, -125, 1.0, sk, L, "open"))
    elif pose == "point":
        arm = cel("M-21 -104 L-6 -112 L-5 -108 L-17 -100 Z", arm_col, arm_sh, L, 1.2, 1.0)
        out.append(arm + nsl + hand(-4, -111, -112, 1.0, sk, L, "point"))
    elif pose == "hands_pockets":
        arm = cel("M-21 -104 L-20 -86 L-13 -82 L-15 -102 Z", arm_col, arm_sh, L, 1.4, 1.0)
        out.append(arm + nsl)
    elif pose == "offer":
        arm = cel("M-22 -106 L-19 -96 L8 -101 L8 -106 L-12 -104 L-16 -108 Z", arm_col, arm_sh, L, 1.2, 1.0)
        paper = ""
        if prop == "paper":
            paper = ('<g transform="translate(13 -112) rotate(-8)">' + cel("M0 0 L13 0 L13 17 L0 17 Z", "#F7F2E2", "#D9D0B8", L, .8, .7)
                     + "".join(line(f"M2 {3+i*2.2:.1f} H{9+(i*3)%4}", .35, .7) for i in range(6)) + "</g>")
        out.append(arm + nsl + cuff(8, -103.5, -95) + paper + hand(9.4, -103.4, -95, 1.0, sk, L, "hold"))
    else:
        sw = 6 if walk else 0
        arm = cel(f"M-22.5 -104 L{-25-sw*.3:.1f} -86 L{-21-sw*.3:.1f} -86 L-16 -103 Z", arm_col, arm_sh, L, 1.4, 1.0)
        ha = (-23 - sw * .3, -87)
        if prop == "suitcase":
            case = (f'<g transform="translate({ha[0]-1:.1f} {ha[1]+15:.1f})">' + line("M-3 -5 L-3 -12 Q0 -14 3 -12 L3 -5", 1.2)
                    + cel("M-12 -5 L12 -5 L12 13 L-12 13 Z", "#7A4A2A", "#5A3218", L, 1.6, 1.0) + line("M-12 1 H12", .5, .6) + "</g>")
            out.append(arm + nsl + cuff(ha[0], ha[1] + 1, 12) + case + hand(ha[0], ha[1], 0, 1.0, sk, L, "fist"))
        else:
            out.append(arm + nsl + cuff(ha[0], ha[1] + 1, 12 + sw) + hand(ha[0], ha[1], 12 + sw, 1.0, sk, L, "open"))

    # --- boyun + baş (üç-çeyrek sağa)
    out.append(cel("M-3.5 -132 L-3.4 -121 Q1 -119 5.6 -121 L5.2 -132 Z", sk, skS, L, 1.6, 1.0))
    head = ("M-16 -158 C-17 -150 -16.6 -142 -13.5 -137 C-10 -131 -4 -127.6 2.5 -127.4 C8 -127.6 13 -131 15.4 -137 "
            "C17.4 -142 18 -150 17.4 -158 C16 -170 8 -175 0 -174.6 C-9 -174 -15 -168 -16 -158 Z")
    out.append(cel(head, sk, skS, L, 2.6, 1.15))
    # saç (ön kütle), sonra kulak saçın üstüne (uzun/küt saçta kulak örtülü)
    out.append(hair_front)
    if hs not in ("long", "bob"):
        ear = cel("M-15.6 -152 C-20.6 -153.6 -21.6 -144 -16.8 -141.4 C-15.6 -141 -14.6 -142 -14.6 -143 Z", sk, skS, L, 1, .9) + line("M-17 -149.5 q-2.2 2 .3 5", .5, .7)
        if earring:
            ear += f'<circle cx="-17.4" cy="-140.6" r="1.4" fill="none" stroke="#C9C4B8" stroke-width=".8"/><circle cx="-17.4" cy="-140.6" r="1.4" fill="none" stroke="{INK}" stroke-width=".3"/>'
        out.append(ear)
    out.append(hat_parts(hat, L))
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
