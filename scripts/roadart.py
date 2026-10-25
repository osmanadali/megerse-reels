"""Yol çizgisi reeli çizimleri (toon dili). Dünya birimi cm (depth.py ile aynı): şerit 375, çizgi genişliği 15.

highway(cam, sid, ...): depth.Scene ile gerçek ölçülü otoyol (şeritler, kesik şerit çizgileri dash:gap, devamlı kenar çizgileri, banket, çim).
car_side(col): yandan otomobil, uzunluk 450 (taban 0,0 ortada, boy ~150).
car_top(col): kuş bakışı otomobil 450×180 (merkez 0,0, burun +x).
road_top(...): kuş bakışı yol şeridi (ölçekli svg), çizgi + boşluk ölçüsüyle.
tape(x0, x1, y, label): ölçü bandı (iki ucu çentikli çizgi + etiket), düz svg.
"""
from toon import INK, cel, darker, line

ASPHALT, ASPHALT_SH, SHOULDER, GRASS = "#3E4046", "#2E3036", "#55575C", "#5E7A3E"
PAINT, YELLOW = "#F4F1E6", "#F2C230"


NIGHT = dict(asphalt="#15171C", shoulder="#1E2026", grass=("#070A06", "#0C1209"))


def highway(cam, sid="hw", lanes=3, lane_w=375, dash=600, gap=900, z0=None, z1=30000, x0=0.0, paint=PAINT, sky=False, edge=True, night=False):
    """Tek yönlü otoyol: şeritler x0 etrafında; kesik şerit çizgileri dash:gap, kenarlarda devamlı çizgi.
    Kamera ortadaki şeritte (x≈0) ilerler: Scene.camera_js(t, dur, dz=...)."""
    from depth import Scene
    asphalt, shoulder, grass = (NIGHT["asphalt"], NIGHT["shoulder"], NIGHT["grass"]) if night else (ASPHALT, SHOULDER, (GRASS, "#7A9450"))
    sc = Scene(cam, sid, ground=grass, sky=sky)
    z0 = z0 if z0 is not None else -2000
    W = lanes * lane_w
    L, R = x0 - W / 2, x0 + W / 2
    sc.add_ground([(L - 300, z0), (R + 300, z0), (R + 300, z1), (L - 300, z1)], f'fill="{shoulder}"')
    sc.add_ground([(L, z0), (R, z0), (R, z1), (L, z1)], f'fill="{asphalt}"')
    if edge:
        for ex in (L + 20, R - 20):
            sc.add_ground([(ex - 7.5, z0), (ex + 7.5, z0), (ex + 7.5, z1), (ex - 7.5, z1)], f'fill="{paint}"')
    cyc = dash + gap
    for k in range(1, lanes):
        lx = L + k * lane_w
        z = z0 - (z0 % cyc)
        while z < z1:
            sc.add_ground([(lx - 7.5, z), (lx + 7.5, z), (lx + 7.5, z + dash), (lx - 7.5, z + dash)], f'fill="{paint}" class="{sid}-dash"')
            z += cyc
    return sc


def car_side(col="#2F6FD0", glass="#2A3A48"):
    """yandan otomobil, burun +x, uzunluk 450, taban (0,0) ortada."""
    body = "M-225 -30 C-228 -60 -220 -78 -200 -84 L-120 -92 C-96 -128 -70 -142 -20 -144 L60 -144 C98 -142 118 -128 140 -96 L200 -88 C220 -84 228 -70 226 -44 L224 -30 Z"
    win = "M-102 -96 C-84 -124 -64 -134 -24 -136 L-24 -98 Z"
    win2 = "M-12 -136 L56 -136 C88 -134 104 -122 122 -98 L-12 -98 Z"
    wheel = lambda cx: (f'<circle cx="{cx}" cy="-34" r="34" fill="#1A1A1E" stroke="{INK}" stroke-width="5"/>'
                        f'<circle cx="{cx}" cy="-34" r="16" fill="#9AA0A8" stroke="{INK}" stroke-width="3"/>')
    return (f'<ellipse cx="0" cy="0" rx="230" ry="10" fill="#000" opacity=".35"/>'
            + cel(body, col, darker(col), -1, 10, 4) + cel(win, glass, darker(glass), -1, 3, 3) + cel(win2, glass, darker(glass), -1, 3, 3)
            + line("M-20 -92 L-20 -40 M-150 -60 H200", 2, .5)
            + cel("M206 -78 L224 -74 L224 -62 L208 -64 Z", "#FFF4C8", "#D8C890", -1, 1, 2)
            + cel("M-224 -72 L-210 -74 L-210 -60 L-224 -58 Z", "#E8423A", "#A8221A", -1, 1, 2)
            + wheel(-140) + wheel(140))


def car_top(col="#2F6FD0", glass="#2A3A48"):
    """kuş bakışı otomobil, 450×180, merkez (0,0), burun +x."""
    return (f'<rect x="-225" y="-90" width="450" height="180" rx="60" fill="{col}" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-60 -78 L90 -78 C110 -60 110 60 90 78 L-60 78 C-80 60 -80 -60 -60 -78 Z" fill="{darker(col, .85)}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M40 -72 L88 -72 C102 -50 102 50 88 72 L40 72 Z" fill="{glass}" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-50 -70 L-80 -70 C-90 -40 -90 40 -80 70 L-50 70 Z" fill="{glass}" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="200" y="-80" width="18" height="34" rx="6" fill="#FFF4C8" stroke="{INK}" stroke-width="3"/><rect x="200" y="46" width="18" height="34" rx="6" fill="#FFF4C8" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="-220" y="-76" width="14" height="30" rx="5" fill="#E8423A" stroke="{INK}" stroke-width="3"/><rect x="-220" y="46" width="14" height="30" rx="5" fill="#E8423A" stroke="{INK}" stroke-width="3"/>')


def road_top(length, dash, gap, s=.1, lane_w=375, lanes=2, paint=PAINT, offset=0.0, idp="rt"):
    """kuş bakışı yol (soldan sağa), ölçek s px/cm. (0,0) sol üst; yükseklik lanes*lane_w*s. Kesik çizgiler class idp-d."""
    H = lanes * lane_w
    out = [f'<rect x="0" y="0" width="{length*s:.1f}" height="{H*s:.1f}" fill="{ASPHALT}"/>',
           f'<rect x="0" y="{-30*s:.1f}" width="{length*s:.1f}" height="{30*s:.1f}" fill="{SHOULDER}"/><rect x="0" y="{H*s:.1f}" width="{length*s:.1f}" height="{30*s:.1f}" fill="{SHOULDER}"/>',
           f'<rect x="0" y="{12*s:.1f}" width="{length*s:.1f}" height="{max(15*s, 1.5):.1f}" fill="{paint}"/>',
           f'<rect x="0" y="{(H-27)*s:.1f}" width="{length*s:.1f}" height="{max(15*s, 1.5):.1f}" fill="{paint}"/>']
    for k in range(1, lanes):
        y = k * lane_w * s
        x = -offset
        while x < length:
            if x + dash > 0:
                out.append(f'<rect class="{idp}-d" x="{max(x, 0)*s:.1f}" y="{y - 7.5*s:.1f}" width="{(min(x+dash, length)-max(x, 0))*s:.1f}" height="{max(15*s, 1.5):.1f}" fill="{paint}"/>')
            x += dash + gap
    return "".join(out)


def tape(x0, x1, y, label, col=YELLOW, fs=40, below=False):
    """ölçü bandı: x0→x1 arası çentikli çizgi + ortada etiket (svg, sayfa koordinatı)."""
    ty = y + (fs + 18 if below else -18)
    return (f'<path d="M{x0} {y} H{x1} M{x0} {y-16} V{y+16} M{x1} {y-16} V{y+16}" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M{x0} {y} H{x1} M{x0} {y-16} V{y+16} M{x1} {y-16} V{y+16}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>'
            f'<text x="{(x0+x1)/2}" y="{ty}" text-anchor="middle" font-family="Mont" font-weight="800" font-size="{fs}" fill="{col}" stroke="{INK}" stroke-width="8" paint-order="stroke">{label}</text>')


def car_rear_world(sc, cars=((-375, 2600, "#C8402F"), (375, 4200, "#E8E4DA"), (0, 7600, "#2F6FD0"), (-375, 11000, "#3A3A40"))):
    """otoyola önde giden birkaç araç (arkadan) ekler; depth.Scene.add ile."""
    from toonprops import CAR_H, car_rear
    for i, (x, z, col) in enumerate(cars):
        sc.add(x, z, car_rear(col, seed=i), CAR_H, 150, w=180)


def cone(h=75):
    """trafik konisi (taban 0,0), boy h (cm)."""
    s = h / 75
    return (f'<g transform="scale({s:.3f})">' + cel("M-22 0 L22 0 L22 -6 L-22 -6 Z", "#2A2A2A", "#111", -1, 1, 2)
            + cel("M-16 -6 L-4 -75 L4 -75 L16 -6 Z", "#FF7A1A", "#C85A0A", -1, 4, 2)
            + '<path d="M-12.5 -26 L12.5 -26 L11 -34 L-11 -34 Z M-8.5 -48 L8.5 -48 L7.2 -55 L-7.2 -55 Z" fill="#F4F1EA"/></g>')


def guard_post():
    """bariyer dikmesi + ray parçası (taban 0,0, boy ~75)."""
    return ('<rect x="-4" y="-75" width="8" height="75" fill="#8A8E96" stroke="#1B1414" stroke-width="2"/>'
            '<rect x="-120" y="-72" width="240" height="26" rx="4" fill="#B9BEC6" stroke="#1B1414" stroke-width="3"/>'
            '<rect x="-120" y="-66" width="240" height="6" fill="#fff" opacity=".35"/>')
