"""İzometrik arsa / bina çizimleri (toon dili: koyu kontur, düz renk, yüz başına ışık tonu).

Dünya: x doğu (ekranda sağ-aşağı), y güney (ekranda sol-aşağı), z yukarı. Görünen yüzler: üst, güney (sol), doğu (sağ).
Işık sol-üstten: üst en açık, güney orta, doğu koyu. Çizim sırası: arkadan öne (x + y küçükten büyüğe).
Animasyon için katlar ayrı <g> (sınıf: {cls} ve {cls}-k{i}); her öğe isteğe bağlı id alır.
"""
import math

from toon import INK, darker, lighter

C30, S30 = math.cos(math.pi / 6), .5


def _rnd(i, a=1.0):
    return ((i * 9301 + 49297) % 233280) / 233280 * a


class Iso:
    def __init__(self, ox=540, oy=700, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def pt(self, x, y, z=0.0):
        return self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * S30 * self.s - z * self.s

    def d(self, pts):
        return "M" + " L".join("%.1f %.1f" % self.pt(*p) for p in pts) + " Z"

    def poly(self, pts, fill, sw=4, stroke=INK, extra=""):
        return f'<path d="{self.d(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'

    # ---- zemin ----
    def tile(self, x, y, w, dd, fill, z=0.0, sw=4, extra=""):
        return self.poly([(x, y, z), (x + w, y, z), (x + w, y + dd, z), (x, y + dd, z)], fill, sw, extra=extra)

    def slab(self, x, y, w, dd, h, col, sw=4, idn=""):
        """kalın zemin plakası (arsa kesiti gibi): üst + güney + doğu yüz."""
        i = f' id="{idn}"' if idn else ""
        return (f'<g{i}>' + self.poly([(x, y + dd, -h), (x + w, y + dd, -h), (x + w, y + dd, 0), (x, y + dd, 0)], darker(col, .82), sw)
                + self.poly([(x + w, y, -h), (x + w, y + dd, -h), (x + w, y + dd, 0), (x + w, y, 0)], darker(col, .66), sw)
                + self.tile(x, y, w, dd, col, sw=sw) + '</g>')

    def grass(self, x, y, w, dd, n=120, col="#5E8A3A", seed=0):
        out = []
        for k in range(n):
            px, py = x + _rnd(k + seed, w), y + _rnd(k * 7 + 3 + seed, dd)
            X, Y = self.pt(px, py)
            out.append(f'<path d="M{X:.1f} {Y:.1f} l-3 -9 M{X:.1f} {Y:.1f} l4 -8" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>')
        return "".join(out)

    def road(self, x, y, w, dd, along="x", col="#4A4C52", line="#F2E6C2"):
        out = [self.tile(x, y, w, dd, col, sw=3)]
        if along == "x":
            k = x
            while k < x + w - 20:
                out.append(self.poly([(k, y + dd / 2 - 3, 0), (k + 34, y + dd / 2 - 3, 0), (k + 34, y + dd / 2 + 3, 0), (k, y + dd / 2 + 3, 0)], line, 0))
                k += 70
        else:
            k = y
            while k < y + dd - 20:
                out.append(self.poly([(x + w / 2 - 3, k, 0), (x + w / 2 + 3, k, 0), (x + w / 2 + 3, k + 34, 0), (x + w / 2 - 3, k + 34, 0)], line, 0))
                k += 70
        return "".join(out)

    # ---- hacimler ----
    def box(self, x, y, z, w, dd, h, col, sw=4, top=None):
        top = top or lighter(col, .22)
        return (self.poly([(x, y + dd, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x, y + dd, z + h)], col, sw)
                + self.poly([(x + w, y, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x + w, y, z + h)], darker(col, .74), sw)
                + self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + dd, z + h), (x, y + dd, z + h)], top, sw))

    def ghost(self, x, y, z, w, dd, h, col="#FFD23F", idn=""):
        """kesikli çizgili, yarı saydam hacim (yapılabilecek bina)."""
        i = f' id="{idn}"' if idn else ""
        st = f'stroke-dasharray="14 10" fill-opacity=".16"'
        return (f'<g{i}>' + self.poly([(x, y + dd, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x, y + dd, z + h)], col, 4, col, st)
                + self.poly([(x + w, y, z), (x + w, y + dd, z), (x + w, y + dd, z + h), (x + w, y, z + h)], col, 4, col, st)
                + self.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + dd, z + h), (x, y + dd, z + h)], col, 4, col, st) + '</g>')

    def windows(self, x, y, z, w, dd, h, cols_s=3, cols_e=2, col="#BFE3F2", lit=()):
        """güney ve doğu yüzlerde pencere sırası (tek kat)."""
        out, wh, m = [], h * .45, h * .28
        for k in range(cols_s):
            a = x + w * (k + .25) / cols_s
            b = a + w * .5 / cols_s
            c = "#FFE08A" if ("s", k) in lit else col
            out.append(self.poly([(a, y + dd, z + m), (b, y + dd, z + m), (b, y + dd, z + m + wh), (a, y + dd, z + m + wh)], c, 2.5))
        for k in range(cols_e):
            a = y + dd * (k + .25) / cols_e
            b = a + dd * .5 / cols_e
            c = "#FFE08A" if ("e", k) in lit else darker(col, .78)
            out.append(self.poly([(x + w, a, z + m), (x + w, b, z + m), (x + w, b, z + m + wh), (x + w, a, z + m + wh)], c, 2.5))
        return "".join(out)

    def building(self, x, y, w, dd, floors, fh=34, col="#E9E2D3", cls="kat", idn="", roof="#B8B0A0", lit_floors=()):
        """kat kat bina; her kat <g class="{cls} {cls}-k{i}">: zemin kat dahil alttan üste."""
        i = f' id="{idn}"' if idn else ""
        out = [f'<g{i}>']
        for k in range(floors):
            z = k * fh
            lit = {("s", 0), ("e", 1)} if k in lit_floors else ()
            out.append(f'<g class="{cls} {cls}-k{k}">' + self.box(x, y, z, w, dd, fh, col)
                       + self.windows(x, y, z, w, dd, fh, max(2, int(w / 40)), max(2, int(dd / 40)), lit=lit) + '</g>')
        zt = floors * fh
        out.append(f'<g class="{cls} {cls}-cati">' + self.box(x - 4, y - 4, zt, w + 8, dd + 8, 8, roof) + '</g>')
        return "".join(out) + '</g>'

    def house(self, x, y, w=90, dd=80, h=46, col="#F2E6D0", roof="#C2563A", idn=""):
        """tek katlı müstakil ev, beşik çatı."""
        i = f' id="{idn}"' if idn else ""
        r = h * .7
        return (f'<g{i}>' + self.box(x, y, 0, w, dd, h, col)
                + self.windows(x, y, 0, w, dd, h, 2, 2)
                + self.poly([(x - 6, y + dd + 6, h), (x + w + 6, y + dd + 6, h), (x + w + 6, y + dd / 2, h + r), (x - 6, y + dd / 2, h + r)], roof, 4)
                + self.poly([(x + w + 6, y - 6, h), (x + w + 6, y + dd + 6, h), (x + w + 6, y + dd / 2, h + r)], darker(col, .74), 4)
                + self.poly([(x - 6, y - 6, h), (x + w + 6, y - 6, h), (x + w + 6, y + dd / 2, h + r), (x - 6, y + dd / 2, h + r)], darker(roof, .8), 4)
                + '</g>')

    def tree(self, x, y, s=1.0, col="#4E8A3E"):
        X, Y = self.pt(x, y)
        k = s * self.s
        return (f'<g transform="translate({X:.1f} {Y:.1f}) scale({k:.3f})"><ellipse cx="0" cy="0" rx="20" ry="9" fill="#000" opacity=".22"/>'
                f'<path d="M-5 0 L-4 -40 L4 -40 L5 0 Z" fill="#7A5232" stroke="{INK}" stroke-width="3"/>'
                f'<circle cx="0" cy="-62" r="30" fill="{col}" stroke="{INK}" stroke-width="3.5"/><circle cx="-12" cy="-72" r="12" fill="{lighter(col, .3)}"/></g>')

    def stake(self, x, y, s=1.0, flag="#E8423A"):
        X, Y = self.pt(x, y)
        k = s * self.s
        return (f'<g transform="translate({X:.1f} {Y:.1f}) scale({k:.3f})"><path d="M-2 0 V-46" stroke="{INK}" stroke-width="5"/>'
                f'<path d="M-2 0 V-46" stroke="#F4EEDC" stroke-width="2.4"/><path d="M0 -46 L22 -39 L0 -32 Z" fill="{flag}" stroke="{INK}" stroke-width="2.5"/></g>')

    def label_pt(self, x, y, z=0.0):
        """HTML etiketleri konumlamak için ekran noktası."""
        return tuple(round(v) for v in self.pt(x, y, z))
