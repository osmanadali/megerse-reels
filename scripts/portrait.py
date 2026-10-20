"""Yakın plan karakter (büst) kütüphanesi: omuz üstü çekim, yüz ifadesi, göz teması, el, kumaş, metal.

Görsel terim → vektör tekniği (ayrıntı: hf/art/DERINLIK.md §8-10):
  micro-expressions        → expr: kaş kaldırma/çatma, gülümseme, dudak gerginliği, göz kapağı açıklığı
  skin pores / texture     → #skin filtresi (ince fraktal gürültü yalnızca ten içinde) + yanak kızarıklığı
  wrinkles around eyes     → dış köşede ince kaz ayağı çizgileri, alt kapak çizgisi (age ile artar)
  iris texture, tear duct  → limbus halkalı radyal iris + ışınsal lif çizgileri, ışık yönünde parıltı, iç köşede pembe göz pınarı
  subsurface scattering    → kulak ve burun kenarında ışığa bakan tarafta sıcak kırmızı geçirgenlik
  articulated fingers      → boğum çizgili ayrı parmak segmentleri, tırnak, kavrama pozu (hand_cup)
  fabric texture / folds   → #tweed dokusu, gerilme noktalarından çıkan kıvrım çizgileri, dikiş (kesik çizgi)
  metallic luster          → #metalB (parlak) ve #brushed (fırçalanmış) gradyanları; düğme, kravat iğnesi
  ambient occlusion        → birleşim yerlerinde (yaka-boyun, burun altı, çene altı, el-fincan) koyu yumuşak gölge
Koordinat: baş merkezi (0,0), yüz yüksekliği ~270 birim. turn: 0 kameraya, + sağa, - sola (≤ .8).
gaze=(gx, gy): -1..1, iris sapması (göz teması için hedefe bakar).
"""
import math

DEFS_P = """
<filter id="skin" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="1.6" numOctaves="2" seed="5" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 .35  0 0 0 0 .16  0 0 0 0 .1  0 0 0 .22 0" result="d"/><feComposite in="d" in2="SourceGraphic" operator="in" result="d2"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>
<filter id="tweed" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9 .35" numOctaves="3" seed="3" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .45 -.05" result="d"/><feComposite in="d" in2="SourceGraphic" operator="in" result="d2"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="d2"/></feMerge></filter>
<filter id="soft3" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="soft8" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="dofFG" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="dofBG" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>
<radialGradient id="metalB" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".25" stop-color="#E8E2D2"/><stop offset=".6" stop-color="#9A927E"/><stop offset="1" stop-color="#3E3A30"/></radialGradient>
<linearGradient id="brushed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2EFE8"/><stop offset=".35" stop-color="#B9B4A8"/><stop offset=".5" stop-color="#E9E6DE"/><stop offset=".75" stop-color="#8E897C"/><stop offset="1" stop-color="#C9C4B8"/></linearGradient>
<radialGradient id="blush" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#D9605A" stop-opacity=".35"/><stop offset="1" stop-color="#D9605A" stop-opacity="0"/></radialGradient>
<radialGradient id="aoR" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#000" stop-opacity=".5"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<linearGradient id="ceramic" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="#F2EEE6"/><stop offset=".8" stop-color="#B9B2A4"/><stop offset="1" stop-color="#8A8274"/></linearGradient>
"""


def _iris_defs(pid, color):
    return (f'<radialGradient id="{pid}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#0A0706"/><stop offset=".32" stop-color="#0A0706"/>'
            f'<stop offset=".36" stop-color="{color}"/><stop offset=".78" stop-color="{color}" stop-opacity=".85"/><stop offset=".9" stop-color="#1A120C"/><stop offset="1" stop-color="#0A0706"/></radialGradient>')


def eye(x, y, w, flip_in, gaze, iris_col, lid=1.0, age=.3, lit_left=True, pid="ir"):
    """Tek göz. flip_in: iç köşe (burun tarafı) solda mı. lid: 1 normal, <1 kısık, >1 şaşkın."""
    h = w * .42 * lid
    inner, outer = (x - w / 2, x + w / 2) if flip_in else (x + w / 2, x - w / 2)
    gx, gy = gaze
    ir = w * .27
    ix, iy = x + gx * w * .2, y + gy * h * .25 + h * .05
    sclera = f"M{inner:.1f} {y+2:.1f} Q{x:.1f} {y-h:.1f} {outer:.1f} {y-1:.1f} Q{x:.1f} {y+h*.75:.1f} {inner:.1f} {y+2:.1f} Z"
    fibers = "".join(f'<path d="M{ix+math.cos(a)*ir*.38:.1f} {iy+math.sin(a)*ir*.38:.1f} L{ix+math.cos(a)*ir*.92:.1f} {iy+math.sin(a)*ir*.92:.1f}" stroke="#F4E2B8" stroke-opacity=".28" stroke-width=".7"/>' for a in [i * math.pi / 9 for i in range(18)])
    cl = -1 if lit_left else 1
    def lid(f):
        return ((1-f)**2*inner + 2*f*(1-f)*x + f*f*outer, (1-f)**2*(y+2) + 2*f*(1-f)*(y-h) + f*f*(y-1))
    lashes = "".join(f'<path d="M{lid(f)[0]:.1f} {lid(f)[1]:.1f} q{(outer-inner)*.03*(1+f):.1f} {-2.5-2*f:.1f} {(outer-inner)*.07*(1+f):.1f} {-3.5-2*f:.1f}" stroke="#1A100C" stroke-width="1.1" fill="none" stroke-linecap="round"/>' for f in [.45, .55, .65, .74, .82, .9, .96])
    crow = "".join(f'<path d="M{outer+(outer-inner)*.08:.1f} {y-4+k*6:.1f} q{(outer-inner)*.12:.1f} {1+k*2:.1f} {(outer-inner)*.22:.1f} {k*5:.1f}" stroke="#7A4A36" stroke-opacity="{.18+age*.3:.2f}" stroke-width="1" fill="none"/>' for k in (-1, 0, 1))
    return (f'<defs><clipPath id="{pid}c"><path d="{sclera}"/></clipPath></defs>'
            f'<path d="M{inner-4:.1f} {y+4:.1f} Q{x:.1f} {y-h*1.45:.1f} {outer+4:.1f} {y:.1f}" stroke="#6A3A28" stroke-opacity=".35" stroke-width="2" fill="none"/>'   # kapak kıvrımı
            f'<path d="M{inner:.1f} {y+6:.1f} Q{x:.1f} {y+h*1.35:.1f} {outer:.1f} {y+4:.1f}" stroke="#6A3A28" stroke-opacity="{.15+age*.25:.2f}" stroke-width="1.6" fill="none"/>'  # alt kapak/göz altı
            f'<path d="{sclera}" fill="#F3EEE6"/>'
            f'<g clip-path="url(#{pid}c)"><path d="{sclera}" fill="#B8A898" opacity=".55" transform="translate(0 {-h*.35:.1f})"/>'                       # üst kapağın gölgesi
            f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{ir:.1f}" fill="url(#{pid})"/>{fibers}'
            f'<circle cx="{ix+cl*ir*.35:.1f}" cy="{iy-ir*.4:.1f}" r="{ir*.22:.1f}" fill="#fff" opacity=".95"/><circle cx="{ix-cl*ir*.3:.1f}" cy="{iy+ir*.35:.1f}" r="{ir*.1:.1f}" fill="#fff" opacity=".45"/></g>'
            f'<ellipse cx="{inner+(outer-inner)*.04:.1f}" cy="{y+1.5:.1f}" rx="{w*.06:.1f}" ry="{h*.22:.1f}" fill="#D98A86"/>'                            # göz pınarı
            f'<path d="M{inner:.1f} {y+2:.1f} Q{x:.1f} {y-h:.1f} {outer:.1f} {y-1:.1f}" stroke="#1A100C" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
            f'{lashes}{crow}')


def brow(x, y, w, flip_in, raise_=0, knit=0, col="#2B1D14"):
    inner, outer = (x - w / 2, x + w / 2) if flip_in else (x + w / 2, x - w / 2)
    yi, yo = y - raise_ * 8 + knit * 5, y - raise_ * 4 - 2
    hairs = []
    for i in range(16):
        f = i / 15
        px = inner + (outer - inner) * f
        py = yi + (yo - yi) * f - math.sin(math.pi * f) * 9
        th = 6 * (1 - .6 * f)
        ang = (-1.2 if outer > inner else -1.94) + f * (.6 if outer > inner else -.6)
        hairs.append(f'<path d="M{px:.1f} {py+th/2:.1f} l{math.cos(ang)*9:.1f} {math.sin(ang)*th:.1f}" stroke="{col}" stroke-width="1.6" stroke-linecap="round"/>')
    base = f'<path d="M{inner:.1f} {yi+3:.1f} Q{(inner+outer)/2:.1f} {min(yi,yo)-10:.1f} {outer:.1f} {yo:.1f}" stroke="{col}" stroke-width="5" stroke-opacity=".55" fill="none" stroke-linecap="round"/>'
    return base + "".join(hairs)


def head(turn=.4, gaze=(.6, 0), expr=None, skin="#C98B63", hair="#2B1D14", iris="#5A3A1E", age=.35, female=False, lit_left=True, pid="h", split=False):
    """Ayrıntılı baş, açı tabanlı üç-çeyrek yapı (sağa bakar; sola için dışarıda scale(-1 1) + lit_left ters).
    θ = turn·80°: yüz orta hattı c = 62·sinθ'ya kayar, uzak yarı cosθ ile daralır, burun ucu sinθ ile kontur dışına çıkar,
    kulak başın ortasına doğru gelir, kafatasının arkası görünür olur."""
    e = dict(smile=0, brow=0, knit=0, lid=1.0, open=0)
    e.update(expr or {})
    th = math.radians(max(0, min(.85, turn)) * 80)
    sn, cs = math.sin(th), math.cos(th)
    c = 62 * sn
    fw = 74 if female else 80                          # yanak yarı genişliği
    jw = 46 if female else 56                          # çene köşesi
    back = -96 - 14 * sn
    face = (f"M{c*.3:.1f} -150 C{c+fw*cs*.9+10*sn:.1f} -150 {c+fw*cs+8*sn:.1f} -100 {c+fw*cs+6*sn:.1f} -50 "      # alın → şakak (uzak)
            f"C{c+(fw+6)*cs+10*sn:.1f} -14 {c+(fw+4)*cs+8*sn:.1f} 10 {c+(fw-6)*cs+6*sn:.1f} 40 "                    # elmacık
            f"C{c+(fw-14)*cs+6*sn:.1f} 80 {c+jw*cs+10*sn:.1f} 112 {c+16*sn+16*cs:.1f} 138 "                         # yanak → çene
            f"C{c+8*sn:.1f} 148 {c-16*cs:.1f} 148 {c-30*cs-6*sn:.1f} 136 "                                          # çene ucu
            f"C{c-jw*cs-30*sn:.1f} 112 {c-(fw-6)*cs-46*sn:.1f} 90 {c-(fw+4)*cs-52*sn:.1f} 50 "                       # yakın çene hattı → çene köşesi
            f"C{back+6:.1f} 30 {back:.1f} -10 {back:.1f} -50 C{back:.1f} -120 {-40-10*sn:.1f} -150 {c*.3:.1f} -150 Z")
    lshG = "pl" if lit_left else "pr"
    ey = -14
    nearx, farx = c - 34 * cs - 2 * sn, c + 34 * cs - 4 * sn
    ew = 40
    eyes = (f'<g transform="translate({nearx:.1f} 0) scale({1-.12*sn:.2f} 1) translate({-nearx:.1f} 0)">{eye(nearx, ey, ew, False, gaze, iris, e["lid"], age, lit_left, pid + "a")}</g>'
            + f'<g transform="translate({farx:.1f} 0) scale({1-.5*sn:.2f} 1) translate({-farx:.1f} 0)">{eye(farx, ey, ew, True, gaze, iris, e["lid"], age, lit_left, pid + "b")}</g>')
    bcol = hair if not female else "#4A2E1C"
    brows = (f'<g transform="translate({nearx:.1f} 0) scale({1-.1*sn:.2f} 1) translate({-nearx:.1f} 0)">{brow(nearx - 2, ey - 30, 50, False, e["brow"], e["knit"], bcol)}</g>'
             f'<g transform="translate({farx:.1f} 0) scale({1-.5*sn:.2f} 1) translate({-farx:.1f} 0)">{brow(farx + 2, ey - 30, 50, True, e["brow"], e["knit"], bcol)}</g>')
    tipx = c + 6 + 26 * sn
    nose = (f'<path d="M{c-8:.1f} -30 C{c-10+4*sn:.1f} 0 {tipx-20:.1f} 24 {tipx-16:.1f} 40" stroke="#6A3420" stroke-opacity=".3" stroke-width="5" fill="none" filter="url(#soft3)"/>'
            f'<path d="M{c+2+4*sn:.1f} -28 C{c+6+10*sn:.1f} 0 {tipx+2:.1f} 26 {tipx+3:.1f} 40" fill="none" stroke="#6A3420" stroke-opacity="{.1+.3*sn:.2f}" stroke-width="2"/>'
            f'<path d="M{tipx-6:.1f} 32 Q{tipx+4:.1f} 32 {tipx+3:.1f} 42 Q{tipx+2:.1f} 52 {tipx-12:.1f} 52" fill="none" stroke="#6A3420" stroke-opacity="{.15+.35*sn:.2f}" stroke-width="1.8"/>'
            f'<ellipse cx="{tipx-6:.1f}" cy="50" rx="16" ry="7" fill="#5A2A18" opacity=".2" filter="url(#soft3)"/><ellipse cx="{tipx-3:.1f}" cy="38" rx="4" ry="3" fill="#fff" opacity=".22" filter="url(#soft3)"/>'
            f'<path d="M{tipx-28:.1f} 47 Q{tipx-32:.1f} 34 {tipx-20:.1f} 36" stroke="#6A3420" stroke-opacity=".45" stroke-width="2.2" fill="none"/>'
            f'<path d="M{tipx-20:.1f} 51 Q{tipx-15:.1f} 55 {tipx-9:.1f} 52" stroke="#3A1A10" stroke-width="3" fill="none" stroke-linecap="round" opacity=".7"/>'
            f'<ellipse cx="{tipx-10:.1f}" cy="62" rx="22" ry="7" fill="url(#aoR)" opacity=".55"/>')
    my, mx, sm = 86, c + 4 * sn, e["smile"]
    mw = (44 if female else 50) * (1 - .3 * sn)
    ml, mr = mx - mw * (.5 + .1 * sn), mx + mw * (.5 - .1 * sn)
    opn = e["open"] * 10
    lip = "#B4564C" if female else "#A4544A"
    mouth = (f'<path d="M{mx-3:.1f} 58 Q{mx:.1f} 70 {mx+1:.1f} 74" stroke="#6A3420" stroke-opacity=".22" stroke-width="5" fill="none" filter="url(#soft3)"/>'
             f'<path d="M{ml:.1f} {my-sm*5:.1f} Q{mx-10:.1f} {my-9:.1f} {mx-2:.1f} {my-6:.1f} Q{mx+3:.1f} {my-9:.1f} {mx+10:.1f} {my-8:.1f} Q{mr-4:.1f} {my-5:.1f} {mr:.1f} {my-sm*5:.1f} '
             f'Q{mx:.1f} {my+2+opn:.1f} {ml:.1f} {my-sm*5:.1f} Z" fill="{lip}"/>'
             + (f'<path d="M{ml+6:.1f} {my-sm*4:.1f} Q{mx:.1f} {my+opn*.6:.1f} {mr-6:.1f} {my-sm*4:.1f} Q{mx:.1f} {my+opn:.1f} {ml+6:.1f} {my-sm*4:.1f} Z" fill="#2A0E0A"/>' if opn else "")
             + f'<path d="M{ml:.1f} {my-sm*5:.1f} Q{mx:.1f} {my+opn+3:.1f} {mr:.1f} {my-sm*5:.1f}" stroke="#4A1A14" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
             f'<path d="M{ml+6:.1f} {my+opn+2:.1f} Q{mx:.1f} {my+opn+17:.1f} {mr-6:.1f} {my+opn+2:.1f} Q{mx:.1f} {my+opn+6:.1f} {ml+6:.1f} {my+opn+2:.1f} Z" fill="{lip}" opacity=".9"/>'
             f'<ellipse cx="{mx+2:.1f}" cy="{my+opn+8:.1f}" rx="9" ry="2.5" fill="#fff" opacity=".26"/>'
             f'<ellipse cx="{mx:.1f}" cy="{my+opn+24:.1f}" rx="20" ry="6" fill="url(#aoR)" opacity=".4"/>'
             f'<path d="M{ml-6:.1f} {my-26-sm*3:.1f} Q{ml-14:.1f} {my-8:.1f} {ml-4:.1f} {my+6-sm*4:.1f}" stroke="#6A3420" stroke-opacity="{.1+age*.25+sm*.15:.2f}" stroke-width="2" fill="none"/>')
    earx = c - 92 * cs - 6 * sn
    ear = (f'<path d="M{earx+8:.1f} -24 C{earx-18:.1f} -40 {earx-24:.1f} 20 {earx-2:.1f} 36 C{earx+6:.1f} 40 {earx+10:.1f} 20 {earx+8:.1f} -24 Z" fill="{skin}"/>'
           f'<path d="M{earx+3:.1f} -16 C{earx-12:.1f} -24 {earx-14:.1f} 14 {earx:.1f} 24" stroke="#7A4030" stroke-opacity=".55" stroke-width="3" fill="none"/>'
           f'<path d="M{earx-18:.1f} -16 C{earx-22:.1f} 0 {earx-16:.1f} 20 {earx-4:.1f} 32" stroke="#E2624E" stroke-opacity="{.55 if lit_left else .15}" stroke-width="4" fill="none" filter="url(#soft3)"/>') if (sn > .15 and not female) else ""
    sss = f'<path d="M{tipx+3:.1f} 30 Q{tipx+8:.1f} 42 {tipx:.1f} 50" stroke="#E2624E" stroke-opacity=".3" stroke-width="3" fill="none" filter="url(#soft3)"/>'
    shade = f'<path d="{face}" fill="url(#{lshG})"/>'
    cheek = f'<path d="M{c+(fw-4)*cs+6*sn:.1f} 0 C{c+(fw-14)*cs:.1f} 40 {c+(fw-30)*cs:.1f} 70 {c+(fw-40)*cs:.1f} 90" stroke="#6A3420" stroke-opacity="{.25*sn:.2f}" stroke-width="10" fill="none" filter="url(#soft8)"/>'
    blush = f'<ellipse cx="{nearx-6:.1f}" cy="40" rx="34" ry="22" fill="url(#blush)"/><ellipse cx="{farx+4:.1f}" cy="40" rx="{26*(1-.4*sn):.1f}" ry="20" fill="url(#blush)"/>'
    nw = 44 if female else 54
    neck = (f'<path d="M{c-nw-14*sn:.1f} 70 C{c-nw-16*sn:.1f} 130 {c-nw-20:.1f} 170 {c-nw-34:.1f} 205 L{c+nw+30:.1f} 205 C{c+nw+10:.1f} 170 {c+nw+4:.1f} 130 {c+nw-6*sn:.1f} 70 Z" fill="{skin}"/>'
            f'<path d="M{c-nw-14*sn:.1f} 70 C{c-nw-16*sn:.1f} 130 {c-nw-20:.1f} 170 {c-nw-34:.1f} 205 L{c+nw+30:.1f} 205 C{c+nw+10:.1f} 170 {c+nw+4:.1f} 130 {c+nw-6*sn:.1f} 70 Z" fill="url(#{lshG})"/>'
            f'<path d="M{c-nw:.1f} 128 Q{c:.1f} 170 {c+nw:.1f} 124" stroke="#2A1008" stroke-opacity=".35" stroke-width="26" fill="none" filter="url(#soft8)"/>')
    if female:
        hair_back = (f'<path d="M{back-14:.1f} -60 C{back-34:.1f} 40 {back-30:.1f} 150 {back+10:.1f} 210 C{back+40:.1f} 240 {back+80:.1f} 226 {c-40:.1f} 200 '
                     f'L{c+70:.1f} 200 C{c+fw*cs+50:.1f} 190 {c+fw*cs+40:.1f} 120 {c+fw*cs+30:.1f} 40 C{c+fw*cs+30:.1f} -40 {c+fw*cs+20:.1f} -100 {c*.3:.1f} -150 Z" fill="{hair}"/>'
                     f'<path d="M{back-6:.1f} 60 C{back-10:.1f} 140 {back+20:.1f} 200 {back+60:.1f} 214" stroke="#000" stroke-opacity=".25" stroke-width="16" fill="none" filter="url(#soft8)"/>')
        hair_top = (f'<path d="M{back-16:.1f} 20 C{back-26:.1f} -120 -30 -180 {30+c*.5:.1f} -170 C{c+fw*cs+30:.1f} -162 {c+fw*cs+22:.1f} -60 {c+fw*cs+12:.1f} 10 '
                    f'C{c+fw*cs-6*sn:.1f} -40 {c+20:.1f} -96 {c-30:.1f} -104 C{c-60:.1f} -96 {back+30:.1f} -70 {back+8:.1f} 0 C{back+2:.1f} 10 {back-6:.1f} 16 {back-16:.1f} 20 Z" fill="{hair}"/>')
    else:
        hair_back = ""
        hair_top = (f'<path d="M{back-6:.1f} -10 C{back-16:.1f} -120 -40 -176 {16+c*.4:.1f} -168 C{c+fw*cs+34:.1f} -160 {c+fw*cs+26:.1f} -96 {c+fw*cs+10:.1f} -76 '
                    f'C{c+fw*cs-8:.1f} -110 {c+10:.1f} -122 {c-30:.1f} -118 C{c-60:.1f} -112 {earx+30:.1f} -84 {earx+16:.1f} -40 C{earx-4:.1f} -30 {earx-14:.1f} 40 {back+30:.1f} 74 C{back+6:.1f} 60 {back-4:.1f} 30 {back-6:.1f} -10 Z" fill="{hair}"/>')
    strands = "".join(f'<path d="M{back+i*16:.1f} {-60-abs(math.sin(i))*40:.1f} Q{-40+i*10+c*.3:.1f} -160 {20+i*7+c*.5:.1f} -152" stroke="#000" stroke-opacity=".12" stroke-width="2" fill="none"/>' for i in range(10))
    hair_hl = f'<path d="M{-50+c*.3:.1f} -146 Q{c*.4:.1f} -170 {50+c*.4:.1f} -150" stroke="#fff" stroke-opacity=".16" stroke-width="10" fill="none" filter="url(#soft3)"/>'
    chinAO = f'<ellipse cx="{c:.1f}" cy="150" rx="60" ry="14" fill="url(#aoR)"/>'
    back_part = f'<defs>{_iris_defs(pid+"a", iris)}{_iris_defs(pid+"b", iris)}</defs>{hair_back}{neck}'
    front = (f'<g filter="url(#skin)"><path d="{face}" fill="{skin}"/>{blush}{cheek}{shade}</g>{chinAO}{brows}{eyes}{nose}{sss}{mouth}{hair_top}{strands}{hair_hl}{ear}')
    return (back_part, front) if split else back_part + front


def jacket(turn=.4, coat="#3B4A62", shirt="#EDE7DA", tie="#7A2A24", female=False, lit_left=True):
    """Omuzlar + gövde üstü (boyun 210'dan aşağı). Kumaş dokusu, kıvrım, dikiş, metal düğme/iğne, yaka AO."""
    t = max(0, min(.8, turn))
    fx = 40 * t
    lshG = "pl" if lit_left else "pr"
    body = f"M-260 520 C-262 380 -230 270 -120 232 L{80+fx*.3:.1f} 232 C{200-60*t:.1f} 262 {250-80*t:.1f} 360 {250-70*t:.1f} 520 Z"
    folds = "".join(f'<path d="{d}" stroke="#000" stroke-opacity=".28" stroke-width="5" fill="none" stroke-linecap="round" filter="url(#soft3)"/>'
                    f'<path d="{d}" stroke="#fff" stroke-opacity=".1" stroke-width="2" fill="none" transform="translate(-4 -3)"/>'
                    for d in ["M-200 330 Q-170 400 -190 500", "M-150 300 Q-120 360 -135 430", f"M{150-40*t:.1f} 320 Q{130-40*t:.1f} 380 {150-40*t:.1f} 470", "M-60 420 Q-20 440 10 500"])
    if female:
        top = (f'<path d="{body}" fill="{coat}"/><path d="M-70 232 Q{fx:.1f} 330 {70+fx*.3:.1f} 232 Z" fill="#C98B63" opacity=".0"/>'
               f'<path d="M-90 232 Q{fx*.5:.1f} 300 {90+fx*.3:.1f} 232" stroke="#F2EADA" stroke-width="14" fill="none"/>'
               + "".join(f'<circle cx="{-70+i*22+fx*.4:.1f}" cy="{250+abs(i-3)*-6+40:.1f}" r="7" fill="url(#metalB)"/>' for i in range(7)))
        return f'<g filter="url(#tweed)">{top}{folds}</g><path d="{body}" fill="url(#{lshG})"/>'
    lap = (f'<path d="M-120 232 L{-30+fx*.5:.1f} 400 L{-10+fx*.5:.1f} 330 L-60 236 Z" fill="{coat}" stroke="#000" stroke-opacity=".35" stroke-width="2"/>'
           f'<path d="M{80+fx*.3:.1f} 232 L{-10+fx*.5:.1f} 400 L{14+fx*.5:.1f} 330 L{40+fx*.3:.1f} 236 Z" fill="{coat}" stroke="#000" stroke-opacity=".35" stroke-width="2"/>'
           f'<path d="M-112 240 L{-28+fx*.5:.1f} 392 M{74+fx*.3:.1f} 240 L{-8+fx*.5:.1f} 392" stroke="#D8D0BC" stroke-opacity=".45" stroke-width="1.4" stroke-dasharray="4 3" fill="none"/>')
    shirtV = (f'<path d="M-60 222 L{-20+fx*.5:.1f} 330 L{-10+fx*.5:.1f} 400 L{14+fx*.5:.1f} 330 L{40+fx*.3:.1f} 222 Z" fill="{shirt}"/>'
              f'<path d="M-60 222 L{-6+fx*.5:.1f} 262 L-40 268 Z M{40+fx*.3:.1f} 222 L{-6+fx*.5:.1f} 262 L{30+fx*.3:.1f} 270 Z" fill="{shirt}" stroke="#000" stroke-opacity=".2" stroke-width="2"/>'
              f'<path d="M{-14+fx*.5:.1f} 262 L{0+fx*.5:.1f} 262 L{12+fx*.5:.1f} 400 L{-8+fx*.5:.1f} 420 L{-24+fx*.5:.1f} 400 Z" fill="{tie}"/>'
              + "".join(f'<path d="M{-20+fx*.5:.1f} {290+i*22:.1f} L{6+fx*.5:.1f} {300+i*22:.1f}" stroke="#000" stroke-opacity=".15" stroke-width="3"/>' for i in range(5))
              + f'<rect x="{-30+fx*.5:.1f}" y="340" width="40" height="6" rx="2" fill="url(#brushed)"/>'                    # kravat iğnesi
              f'<ellipse cx="{-8+fx*.4:.1f}" cy="226" rx="70" ry="14" fill="url(#aoR)"/>')
    btn = "".join(f'<circle cx="{-4+fx*.5:.1f}" cy="{430+i*50}" r="8" fill="url(#metalB)"/><circle cx="{-4+fx*.5:.1f}" cy="{430+i*50}" r="8" fill="none" stroke="#2A2418" stroke-width="1.2"/>' for i in range(2))
    seams = f'<path d="M-180 250 Q-200 360 -205 520 M{170-50*t:.1f} 260 Q{190-50*t:.1f} 360 {195-55*t:.1f} 520" stroke="#000" stroke-opacity=".3" stroke-width="2" stroke-dasharray="5 3" fill="none"/>'
    return f'<g filter="url(#tweed)"><path d="{body}" fill="{coat}"/>{folds}{seams}</g>{shirtV}{lap}<path d="{body}" fill="url(#{lshG})" opacity=".9"/>{btn}'


def hand_cup(skin="#C98B63", lit_left=True, sleeve="#3B4A62", cuff="#EDE7DA"):
    """Fincanı kavrayan sağ el (parmak boğumları, tırnaklar, AO). Yerel: fincan merkezi (0,0), ~160 birim."""
    cup = ('<path d="M-60 -70 L60 -70 L50 70 Q0 86 -50 70 Z" fill="url(#ceramic)"/><ellipse cx="0" cy="-70" rx="60" ry="14" fill="#E9E4DA"/>'
           '<ellipse cx="0" cy="-67" rx="52" ry="10" fill="#3A2214"/><ellipse cx="-14" cy="-69" rx="20" ry="3" fill="#7A4A2A" opacity=".7"/>'
           '<path d="M-48 -50 Q-54 0 -44 60" stroke="#fff" stroke-opacity=".7" stroke-width="6" fill="none" filter="url(#soft3)"/>'
           '<path d="M58 -40 C110 -40 110 40 52 40" stroke="#EDE8DE" stroke-width="14" fill="none"/>')
    fingers = []
    for i, (y, ln) in enumerate([(-38, 1), (-8, 1.06), (22, 1), (50, .82)]):
        x0 = 20
        seg = f"M{x0} {y} q{-22*ln:.1f} -3 {-38*ln:.1f} 2 q{-12*ln:.1f} 4 {-20*ln:.1f} 11"
        fingers.append(f'<path d="{seg}" stroke="#000" stroke-opacity=".35" stroke-width="27" fill="none" stroke-linecap="round" transform="translate(1 3)" filter="url(#soft3)"/>'
                       f'<path d="{seg}" stroke="{skin}" stroke-width="21" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                       f'<path d="{seg}" stroke="#5A2A18" stroke-opacity=".22" stroke-width="7" fill="none" stroke-linecap="round" transform="translate(0 6)"/>'
                       f'<path d="M{x0-18*ln:.1f} {y-6:.1f} q2 6 0 11 M{x0-38*ln:.1f} {y-4:.1f} q2 6 0 11" stroke="#7A4630" stroke-opacity=".5" stroke-width="1.6" fill="none"/>'
                       f'<ellipse cx="{x0-56*ln:.1f}" cy="{y+11:.1f}" rx="5" ry="6" fill="#E8C0A8" stroke="#9A6A50" stroke-width="1"/>')
    palm = (f'<path d="M14 -52 C70 -60 110 -20 116 30 C120 70 80 90 40 82 C20 78 14 60 16 40 Z" fill="{skin}"/>'
            f'<path d="M14 -52 C70 -60 110 -20 116 30 C120 70 80 90 40 82 C20 78 14 60 16 40 Z" fill="url(#{"pl" if lit_left else "pr"})"/>'
            f'<path d="M26 -46 C-6 -64 -40 -72 -58 -60" stroke="{skin}" stroke-width="26" fill="none" stroke-linecap="round"/>'
            f'<path d="M-36 -68 q2 7 0 12" stroke="#7A4630" stroke-opacity=".5" stroke-width="1.6" fill="none"/><ellipse cx="-60" cy="-62" rx="7" ry="6" fill="#E8C0A8" stroke="#9A6A50" stroke-width="1"/>'
            f'<path d="M70 -20 Q60 20 74 60" stroke="#7A4630" stroke-opacity=".3" stroke-width="2" fill="none"/>')
    return cup + "".join(fingers[::-1]) + palm + '<rect x="96" y="-10" width="70" height="110" fill="' + sleeve + '" filter="url(#tweed)"/><rect x="92" y="-6" width="14" height="104" fill="' + cuff + '"/>'


def back_shoulder(coat="#2E3B4E", hair="#2B1D14", skin="#B97D58", lit_left=True):
    """Omuz üstü çekimin ön planı: kameraya sırtı dönük baş + omuz (yerel: baş merkezi 0,0)."""
    return (f'<path d="M-330 600 C-330 420 -260 300 -120 270 L120 270 C240 300 330 420 330 600 Z" fill="{coat}" filter="url(#tweed)"/>'
            f'<path d="M-330 600 C-330 420 -260 300 -120 270 L120 270 C240 300 330 420 330 600 Z" fill="url(#{"pl" if lit_left else "pr"})"/>'
            f'<path d="M-70 120 L-80 290 L80 290 L70 120 Z" fill="{skin}"/><path d="M-80 260 Q0 300 80 260 L90 300 L-90 300 Z" fill="#EDE7DA"/>'
            f'<path d="M100 -20 C122 -30 130 30 104 44 Z" fill="{skin}"/><path d="M106 -10 C118 -4 118 26 106 34" stroke="#E2624E" stroke-opacity=".6" stroke-width="4" fill="none" filter="url(#soft3)"/>'
            f'<ellipse cx="0" cy="-10" rx="112" ry="140" fill="{hair}"/><path d="M-90 80 Q0 140 90 80 L80 120 Q0 150 -80 120 Z" fill="{hair}"/>'
            + "".join(f'<path d="M{-90+i*18} -110 Q{-80+i*16} 0 {-60+i*12} 110" stroke="#fff" stroke-opacity=".07" stroke-width="3" fill="none"/>' for i in range(11)))


def defs_light(lit_left=True):
    a, b = ("0", "1") if lit_left else ("1", "0")
    return (f'<linearGradient id="pl" x1="{a}" y1="0" x2="{b}" y2=".2"><stop offset="0" stop-color="#FFE9C8" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset=".62" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1A0A04" stop-opacity=".55"/></linearGradient>'
            f'<linearGradient id="pr" x1="{b}" y1="0" x2="{a}" y2=".2"><stop offset="0" stop-color="#FFE9C8" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset=".62" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1A0A04" stop-opacity=".55"/></linearGradient>')


def light_shafts(x, y, angle=28, n=5, length=1400, spread=70, col="#FFE7B8", op=.22):
    """Hacimsel ışık (volumetric): pencereden giren, uca doğru açılıp sönen yumuşak huzmeler + toz zerreleri."""
    out = []
    for i in range(n):
        w0, w1 = 26 + (i * 13) % 20, 120 + (i * 37) % 90
        ox = x + i * spread
        out.append(f'<g transform="translate({ox} {y}) rotate({angle})"><path d="M{-w0/2} 0 L{w0/2} 0 L{w1/2} {length} L{-w1/2} {length} Z" fill="url(#shaftG)" opacity="{op*(.6+.4*((i*7)%3)/2):.2f}" filter="url(#soft8)"/></g>')
    dust = "".join(f'<circle cx="{x+((i*97)%(n*spread+200))}" cy="{y+((i*61)%700)+40}" r="{1.2+(i%3)*.8}" fill="#FFF4DA" opacity="{.25+(i%4)*.12:.2f}"/>' for i in range(40))
    return (f'<defs><linearGradient id="shaftG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity="1"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
            f'<g style="mix-blend-mode:screen">{"".join(out)}<g class="dust">{dust}</g></g>')


def chiaroscuro(cx, cy, r=700, dark=.72):
    """Yoğun ışık-gölge: anahtar ışığın dışı karanlığa düşer (sahnenin en üstüne)."""
    return (f'<defs><radialGradient id="chiG" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset=".55" stop-color="#000" stop-opacity="{dark*.35:.2f}"/><stop offset="1" stop-color="#05030A" stop-opacity="{dark}"/></radialGradient></defs>'
            f'<rect x="-200" y="-200" width="1400" height="1500" fill="url(#chiG)"/>')


def bust(turn=.4, flip=False, lit_left=True, coat="#3B4A62", female=False, skin="#C98B63", hair="#2B1D14", iris="#5A3A1E",
         gaze=(.7, 0), expr=None, age=.35, pid="b", tie="#7A2A24"):
    """Baş + omuzlar tek parça. flip=True sola bakar (ışık dünyaya göre sabit kalır)."""
    ll = lit_left != flip
    hb, hf = head(turn, gaze, expr, skin, hair, iris, age, female, ll, pid, split=True)
    inner = hb + f'<g transform="translate(0 -72)">{jacket(turn, coat=coat, female=female, lit_left=ll, tie=tie)}</g>' + hf
    return f'<g transform="scale(-1 1)">{inner}</g>' if flip else inner
