"""Derinlik kütüphanesi (v3 sahne standardı). Kurallar ve kontrol listesi: hf/art/DERINLIK.md

Dünya koordinatı: x sağa, y yukarı (yer = 0), z kameradan uzaklık; birim ≈ cm (insan boyu 175).
Ekran: tek kaçış noktalı perspektif. Aynı Cam ile yerleştirilen her şey otomatik olarak:
  1. çizgisel perspektif: k = f/z ölçeği, yer çizgileri kaçış noktasında birleşir
  2. üst üste bindirme: Scene uzaktan yakına sıralar (yakın olan uzaktakini örter)
  3. ışık/gölge: tek güneş (sun, alt); düşen gölge yere perspektifle izdüşürülür, nesnelerde lsh örtüsü
  4. hava perspektifi: uzaklık bandına göre pus rengine karışım + doygunluk/ netlik kaybı; çizgiler k ile incelir
  5. mekânsal sıkışma: eşit dünya aralığı (row/road) ekranda uzağa doğru otomatik daralır
Kamera: Scene.camera_js() kamerayı dünyada hareket ettirir; JS her karede yeniden izdüşürür (gerçek parallax).
"""
import math
import re

W, H = 960, 1080


class Cam:
    def __init__(self, horizon=430, vpx=480, f=800, eye=160, sun=(-1.0, 0.35), alt=38, haze="#CFDAE0", zfar=9000, focus=None):
        self.horizon, self.vpx, self.f, self.eye = horizon, vpx, f, eye
        n = math.hypot(*sun)
        self.sun = (sun[0] / n, sun[1] / n)            # ışığın GELDİĞİ yön (x, z); x<0: soldan
        self.alt, self.haze, self.zfar = alt, haze, zfar
        self.lit_left = self.sun[0] <= 0
        self.focus = focus                              # odak uzaklığı: bunun çok önündekiler bulanık (alan derinliği)

    def k(self, z):
        return self.f / z

    def pt(self, x, z, y=0.0):
        k = self.f / z
        return (self.vpx + x * k, self.horizon + (self.eye - y) * k)

    def band(self, z):
        """0 (yakın, net) .. 5 (en uzak, puslu)"""
        t = (math.log(max(z, self.f)) - math.log(self.f)) / (math.log(self.zfar) - math.log(self.f))
        return max(0, min(5, round(t * 5)))


def _hex(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def defs(cam):
    """Sayfada bir kez (reelkit.page(defs=artlib2.DEFS2 + depth.defs(cam)))."""
    hr, hg, hb = _hex(cam.haze)
    out = []
    for b in range(6):
        t = [0, .12, .26, .42, .58, .72][b]
        a, sat, blur = 1 - t, 1 - .55 * t, [0, 0, .5, .9, 1.4, 2.0][b]
        bl = f'<feGaussianBlur stdDeviation="{blur}"/>' if blur else ""
        out.append(f'<filter id="atm{b}" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">'
                   f'<feColorMatrix type="saturate" values="{sat:.2f}"/>'
                   f'<feColorMatrix type="matrix" values="{a:.2f} 0 0 0 {t*hr:.3f}  0 {a:.2f} 0 0 {t*hg:.3f}  0 0 {a:.2f} 0 {t*hb:.3f}  0 0 0 1 0"/>{bl}</filter>')
    lx1, lx2 = ("0", "1") if cam.lit_left else ("1", "0")
    out.append(f'''<filter id="dofNear" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="shblur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>
<linearGradient id="lsh" x1="{lx1}" y1="0" x2="{lx2}" y2=".25"><stop offset="0" stop-color="#FFF6E2" stop-opacity=".28"/><stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></linearGradient>
<linearGradient id="lshR" x1="{lx2}" y1="0" x2="{lx1}" y2=".25"><stop offset="0" stop-color="#FFF6E2" stop-opacity=".28"/><stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".42"/></linearGradient>
<linearGradient id="ao" x1="0" y1="0" x2="0" y2="1"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient>
<linearGradient id="skyD" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3D79AE"/><stop offset=".7" stop-color="#9CC2DB"/><stop offset="1" stop-color="{cam.haze}"/></linearGradient>''')
    return "".join(out)


# ---------------- sahne: dünya koordinatında, her karede yeniden izdüşen kamera ----------------
def shadow_polys(cam, x, z, w, h):
    """Düşen gölge (güneşin tersine uzanan dörtgen) + temas gölgesi (yerde daire) — dünya koordinatında yer poligonları."""
    L = h / math.tan(math.radians(cam.alt))
    dx, dz = -cam.sun[0] * L, -cam.sun[1] * L
    px, pz = -dz / max(L, 1) * w / 2, dx / max(L, 1) * w / 2
    tip = .55
    cast = [(x - px, z - pz), (x + px, z + pz), (x + dx + px * tip, z + dz + pz * tip), (x + dx - px * tip, z + dz - pz * tip)]
    r = w * .32
    contact = [(x + r * math.cos(a * math.pi / 8), z + r * .9 * math.sin(a * math.pi / 8)) for a in range(16)]
    return cast, contact


class Scene:
    """Tek <svg> sahne. Nesneler dünya koordinatında tutulur; kamera (cx, cz, cy) hareket edince
    JS her karede tüm nesneleri, yolları ve gölgeleri yeniden izdüşürür → gerçek parallax, katman yırtılması yok.
    Çizim sırası uzaktan yakına (üst üste bindirme)."""

    def __init__(self, cam, sid, ground=("#6F7F45", "#A9AE7C"), sky=True):
        self.cam, self.sid, self.ground, self.sky = cam, sid, ground, sky
        self.items, self.polys = [], []        # polys: (z_sıra, [(x,z)...], stil)

    def add(self, x, z, art, art_h, h, w=None, shadow=True, focus=True, y=0.0):
        """art: tabanı (0,0)'da, art_h birim boyunda çizim; h: dünyadaki gerçek boy; w: gölge tabanı genişliği."""
        w = w if w is not None else h * .35
        self.items.append(dict(x=x, z=z, y=y, art=art, s=h / art_h, focus=focus))
        if shadow:
            cast, contact = shadow_polys(self.cam, x, z, w, h)
            self.polys.append((z + 1e5, cast, 'fill="#1A1410" opacity=".38" filter="url(#shblur)"'))
            self.polys.append((z + 1e5, contact, 'fill="#000" opacity=".45" filter="url(#shblur)"'))

    def add_figure(self, x, z, look_at=None, h=175, cheat=.6, **kw):
        """Karakter: look_at=(x, z) verilirse o noktaya döner (konuştuğu kişi, baktığı nesne).
        Yan yana duran iki kişi birbirine ~üç-çeyrek döner (cheat: sinemadaki gibi kameraya hafif açılır)."""
        if look_at:
            dx, dz = look_at[0] - x, look_at[1] - z
            ang = math.atan2(abs(dx), -dz)              # 0: kameraya doğru, π/2: yana, π: kameradan uzağa
            kw.setdefault("turn", ang / (math.pi / 2) * cheat if ang <= math.pi / 2 else cheat + (ang / (math.pi / 2) - 1) * (.85 - cheat))
            kw.setdefault("flip", dx < 0)
        kw.setdefault("lit_left", self.cam.lit_left)
        self.add(x, z, figure(**kw), FIG_H, h, w=h * .3)

    def add_toon(self, x, z, look_at=None, h=175, **kw):
        """2D çizgi film karakteri (scripts/toon.py). look_at=(x, z): o yöne döner ve gözü oraya bakar."""
        from toon import TOON_H, toon_figure
        if look_at:
            dx, dz = look_at[0] - x, look_at[1] - z
            kw.setdefault("flip", dx < 0)
            kw.setdefault("look", (1, max(-.6, min(.6, dz / 400))))
        kw.setdefault("light_from_left", self.cam.lit_left)
        self.add(x, z, toon_figure(**kw), TOON_H, h, w=h * .3)

    def row(self, x, z0, dz, n, art, art_h, h, w=None, jitter=0):
        """Eşit dünya aralığı → mekânsal sıkışma kendiliğinden."""
        for i in range(n):
            self.add(x + jitter * ((i * 37) % 7 - 3), z0 + i * dz, art(i), art_h, h, w)

    def add_ground(self, pts, style):
        """Yere yatık düz şekil (yol, kaldırım, gölge alanı) — dünya (x, z) noktaları."""
        self.polys.append((1e9, pts, style))

    def add_road(self, x0, width, z0=None, z1=None, color="#5B5A57", line="#E8E2CC", dash=260):
        z0, z1 = z0 or self.cam.f * .12, z1 or self.cam.zfar
        self.add_ground([(x0 - width / 2, z0), (x0 + width / 2, z0), (x0 + width / 2, z1), (x0 - width / 2, z1)], f'fill="{color}"')
        z = math.ceil(z0 / dash) * dash
        while z < z1:
            self.add_ground([(x0 - 6, z), (x0 + 6, z), (x0 + 6, z + dash * .5), (x0 - 6, z + dash * .5)], f'fill="{line}" opacity=".85"')
            z += dash

    def _poly_d(self, pts, cx=0, cz=0):
        c, out = self.cam, []
        for x, z in pts:
            zz = max(z - cz, 8)
            k = c.f / zz
            out.append(f"{c.vpx + (x - cx) * k:.1f} {c.horizon + c.eye * k:.1f}")
        return "M" + " L".join(out) + " Z"

    def svg(self):
        c, sid = self.cam, self.sid
        g0, g1 = self.ground
        parts = [f'<linearGradient id="{sid}-gr" gradientUnits="userSpaceOnUse" x1="0" y1="{c.horizon}" x2="0" y2="{H}">'
                 f'<stop offset="0" stop-color="{c.haze}"/><stop offset=".1" stop-color="{g1}"/><stop offset="1" stop-color="{g0}"/></linearGradient>']
        if self.sky:
            parts.append(f'<rect x="-600" y="-600" width="{W+1200}" height="{c.horizon+601}" fill="url(#skyD)"/>')
        parts.append(f'<rect x="-600" y="{c.horizon}" width="{W+1200}" height="{H+600}" fill="url(#{sid}-gr)"/>')
        for i, (_, pts, st) in enumerate(sorted(self.polys, key=lambda p: -p[0])):
            parts.append(f'<path id="{sid}-p{i}" d="{self._poly_d(pts)}" {st}/>')
        self._psorted = sorted(self.polys, key=lambda p: -p[0])
        self._isorted = sorted(self.items, key=lambda it: -it["z"])
        for i, it in enumerate(self._isorted):
            sx, sy = c.pt(it["x"], it["z"], it["y"])
            k = c.k(it["z"]) * it["s"]
            near_blur = c.focus and it["z"] < c.focus * .55
            filt = f"atm{c.band(it['z'])}" if it["focus"] and not near_blur else "dofNear"
            parts.append(f'<g filter="url(#{filt})"><g id="{sid}-i{i}" transform="translate({sx:.1f} {sy:.1f}) scale({k:.4f})">{it["art"]}</g></g>')
        return f'<svg class="fill" id="{sid}" viewBox="0 0 {W} {H}" style="overflow:visible">{"".join(parts)}</svg>'

    def js(self):
        """Sahne verisi + izdüşüm fonksiyonu (svg()'den sonra çağır). Kamera: window.CAM_{sid} = {cx, cz, cy}."""
        c, sid = self.cam, self.sid
        items = ",".join(f'[{it["x"]},{it["z"]},{it["y"]},{it["s"]:.5f}]' for it in self._isorted)
        polys = ",".join("[" + ",".join(f"{x:.1f},{z:.1f}" for x, z in pts) + "]" for _, pts, _ in self._psorted)
        return (f'(function(){{const C={{f:{c.f},h:{c.horizon},vx:{c.vpx},e:{c.eye}}},I=[{items}],P=[{polys}];'
                f'const cam=window.CAM_{sid}={{cx:0,cz:0,cy:0}};const ie=I.map((_,i)=>document.getElementById("{sid}-i"+i)),pe=P.map((_,i)=>document.getElementById("{sid}-p"+i));'
                f'window.PROJ_{sid}=function(){{const e=C.e+cam.cy;'
                f'I.forEach((it,i)=>{{const z=it[1]-cam.cz;if(z<20){{ie[i].setAttribute("visibility","hidden");return;}}const k=C.f/z;'
                f'ie[i].setAttribute("visibility","visible");ie[i].setAttribute("transform","translate("+(C.vx+(it[0]-cam.cx)*k).toFixed(1)+" "+(C.h+(e-it[2])*k).toFixed(1)+") scale("+(k*it[3]).toFixed(4)+")");}});'
                f'P.forEach((p,i)=>{{let d="M";for(let j=0;j<p.length;j+=2){{const k=C.f/Math.max(p[j+1]-cam.cz,8);d+=(j?" L":"")+(C.vx+(p[j]-cam.cx)*k).toFixed(1)+" "+(C.h+e*k).toFixed(1);}}pe[i].setAttribute("d",d+" Z");}});}};}})();')

    def camera_js(self, t0, dur, dx=0.0, dz=0.0, dy=0.0, ease="sine.inOut"):
        """Kamera hareketi (dünya birimi): dx yana (truck), dz ileri (dolly), dy yukarı (pedestal). Seek-güvenli (onUpdate)."""
        s = self.sid
        return f'tl.to(window.CAM_{s},{{cx:"+={dx}",cz:"+={dz}",cy:"+={dy}",duration:{dur},ease:"{ease}",onUpdate:window.PROJ_{s}}},{t0});'


# ---------------- karakter ----------------
def figure(turn=0.5, flip=False, pose="stand", coat="#2E3B4E", pants="#2A2C33", skin="#C98B63", hair="#2B1D14",
           shoes="#1A1512", shirt="#E9E2D0", hat=None, female=False, mouth=0, lit_left=True):
    """Tam boy insan, tabanı (0,0), boy 175 birim. turn: 0 önden, .5 üç-çeyrek (sağa bakar), .8 neredeyse profil.
    flip=True sola bakar. Konuşan iki kişi birbirine üç-çeyrek döner (izleyiciye değil).
    pose: stand | talk (yakın kol jest) | walk. Işık yönü dünyaya göre sabit kalır (flip edilse de)."""
    t = turn
    sh = "lshR" if (flip == lit_left) else "lsh"    # yansıtılmış grupta ışığın doğru tarafta kalması
    nearW, farW = 22 * (1 - .12 * t), 22 * (1 - .6 * t)
    cx = 3 * t                                        # gövde merkezi bakış yönüne hafif kayar
    dark = 'style="filter:brightness(.72)"'

    # bacaklar
    if pose == "walk":
        nl, fl = (-14, 10), (12, -6)                  # (ayak x, diz öne) yakın bacak geride, uzak bacak önde
    else:
        nl, fl = (-8 + 2 * t, 0), (7 - 2 * t, 0)
    def leg(fx, knee, col, shade):
        hipx = fx * .55 + cx
        return (f'<path d="M{hipx-8:.1f} -92 Q{hipx+knee*.6-9:.1f} -50 {fx-6:.1f} -8 L{fx+6:.1f} -8 Q{hipx+knee*.6+9:.1f} -50 {hipx+8:.1f} -92 Z" fill="{col}"/>'
                f'<path d="M{hipx-8:.1f} -92 Q{hipx+knee*.6-9:.1f} -50 {fx-6:.1f} -8 L{fx+6:.1f} -8 Q{hipx+knee*.6+9:.1f} -50 {hipx+8:.1f} -92 Z" fill="url(#{shade})"/>'
                f'<path d="M{fx-7:.1f} -9 Q{fx:.1f} -13 {fx+7+9*t:.1f} -7 Q{fx+12+10*t:.1f} -3 {fx+11+10*t:.1f} 0 L{fx-8:.1f} 0 Z" fill="{shoes}"/>'
                f'<path d="M{fx-8:.1f} -1.2 H{fx+11+10*t:.1f}" stroke="#000" stroke-opacity=".5" stroke-width="2"/>')
    legcol = skin if female else pants
    far_leg = f'<g {dark}>{leg(fl[0], fl[1], legcol, sh)}</g>'
    near_leg = leg(nl[0], nl[1], legcol, sh)

    # kollar (kalın tüp + gölge şeridi = hacim)
    so = 1.6 if lit_left != flip else -1.6
    def arm(path, w, col, hand):
        return (f'<path d="{path}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
                f'<path d="{path}" stroke="#000" stroke-opacity=".22" stroke-width="{w*.38:.1f}" stroke-linecap="round" fill="none" transform="translate({so*1.6:.1f} 0)"/>'
                f'<circle cx="{hand[0]:.1f}" cy="{hand[1]:.1f}" r="{w*.42:.1f}" fill="{skin}"/>')
    fsx, nsx = cx + farW - 4, cx - nearW + 4
    if pose == "walk":
        far_arm = arm(f"M{fsx:.1f} -140 Q{fsx-4:.1f} -112 {fsx-12:.1f} -90", 11, coat, (fsx - 12, -86))
        near_arm = arm(f"M{nsx:.1f} -140 Q{nsx+4:.1f} -112 {nsx+16:.1f} -92", 12.5, coat, (nsx + 17, -88))
    elif pose == "talk":
        far_arm = arm(f"M{fsx:.1f} -140 Q{fsx+2:.1f} -112 {fsx-2:.1f} -88", 11, coat, (fsx - 2, -84))
        near_arm = arm(f"M{nsx:.1f} -140 Q{nsx-2:.1f} -110 {nsx+10:.1f} -102 Q{nsx+24:.1f} -108 {nsx+34:.1f} -118", 12.5, coat, (nsx + 37, -120))
    else:
        far_arm = arm(f"M{fsx:.1f} -140 Q{fsx+3:.1f} -112 {fsx+1:.1f} -88", 11, coat, (fsx + 1, -84))
        near_arm = arm(f"M{nsx:.1f} -140 Q{nsx-3:.1f} -112 {nsx+1:.1f} -87", 12.5, coat, (nsx + 1, -83))

    # gövde
    L, R = cx - nearW, cx + farW
    if female:
        torso = (f'<path d="M{L+2:.1f} -142 Q{cx:.1f} -150 {R-2:.1f} -142 L{R-4:.1f} -104 Q{R+4:.1f} -80 {R+10:.1f} -52 L{L-10:.1f} -52 Q{L-4:.1f} -80 {L+4:.1f} -104 Z" fill="{coat}"/>'
                 f'<path d="M{L+2:.1f} -142 Q{cx:.1f} -150 {R-2:.1f} -142 L{R-4:.1f} -104 Q{R+4:.1f} -80 {R+10:.1f} -52 L{L-10:.1f} -52 Q{L-4:.1f} -80 {L+4:.1f} -104 Z" fill="url(#{sh})"/>'
                 f'<path d="M{L+4:.1f} -104 Q{cx:.1f} -100 {R-4:.1f} -104" stroke="#000" stroke-opacity=".25" stroke-width="3" fill="none"/>'
                 f'<path d="M{cx-6+4*t:.1f} -146 L{cx+4*t:.1f} -132 L{cx+6+4*t:.1f} -146" fill="{skin}"/>')
    else:
        torso = (f'<path d="M{L:.1f} -142 Q{cx:.1f} -150 {R:.1f} -142 L{R-2:.1f} -84 Q{cx:.1f} -80 {L+1:.1f} -84 Z" fill="{coat}"/>'
                 f'<path d="M{cx-7+9*t:.1f} -146 L{cx+9*t:.1f} -118 L{cx+7+9*t:.1f} -146 Z" fill="{shirt}"/><path d="M{cx-2+9*t:.1f} -140 L{cx+9*t:.1f} -116 L{cx+2+9*t:.1f} -140 Z" fill="#6A2A24"/>'
                 f'<path d="M{cx-8+9*t:.1f} -146 L{cx-2+9*t:.1f} -116 L{cx+9*t:.1f} -96 M{cx+8+9*t:.1f} -146 L{cx+3+9*t:.1f} -118" stroke="#000" stroke-opacity=".35" stroke-width="2" fill="none"/>'
                 f'<circle cx="{cx+1+9*t:.1f}" cy="-104" r="1.6" fill="#111"/><circle cx="{cx+1+9*t:.1f}" cy="-94" r="1.6" fill="#111"/>'
                 f'<path d="M{L:.1f} -142 Q{cx:.1f} -150 {R:.1f} -142 L{R-2:.1f} -84 Q{cx:.1f} -80 {L+1:.1f} -84 Z" fill="url(#{sh})"/>'
                 f'<path d="M{L+1:.1f} -86 Q{cx:.1f} -82 {R-2:.1f} -86" stroke="#000" stroke-opacity=".3" stroke-width="3" fill="none"/>')

    # baş (üç-çeyrek: yüz özellikleri bakış yönüne kayar, uzak göz daralır, burun çıkıntı yapar, yakın kulak görünür)
    hx = cx + 4 * t
    fo = 7.5 * t
    ear = f'<ellipse cx="{hx-9+2*t:.1f}" cy="-162" rx="{2.2+1.2*t:.1f}" ry="4" fill="{skin}"/><ellipse cx="{hx-9+2*t:.1f}" cy="-162" rx="1.2" ry="2.4" fill="#000" opacity=".2"/>' if t > .15 else \
        f'<ellipse cx="{hx-11:.1f}" cy="-162" rx="2.2" ry="4" fill="{skin}"/><ellipse cx="{hx+11:.1f}" cy="-162" rx="2.2" ry="4" fill="{skin}"/>'
    eyeN, eyeF = hx - 4.2 * (1 - .15 * t) + fo, hx + 4.2 * (1 - .55 * t) + fo
    mouth_d = (f'<path d="M{hx-2.6+fo:.1f} -155.5 Q{hx+fo:.1f} {-154.6 + mouth*.9:.1f} {hx+2.8+fo:.1f} -155.5" stroke="#5A2A22" stroke-width="1.2" fill="{"#3A1410" if mouth else "none"}"/>')
    head = ((ear if t <= .15 else '') + f'<path d="M{hx-4:.1f} -152 V-144 H{hx+4:.1f} V-152 Z" fill="{skin}"/><path d="M{hx-4:.1f} -150 H{hx+4:.1f} V-146 H{hx-4:.1f}Z" fill="#000" opacity=".2"/>'
            f'<path d="M{hx-10.5:.1f} -165 Q{hx-11:.1f} -177 {hx:.1f} -177 Q{hx+11:.1f} -177 {hx+10.5+t:.1f} -164 Q{hx+10.5+2*t:.1f} -156 {hx+4+3*t:.1f} -151.5 Q{hx:.1f} -149.5 {hx-4+t:.1f} -151.5 Q{hx-10:.1f} -156 {hx-10.5:.1f} -165 Z" fill="{skin}"/>'
            f'<path d="M{hx-10.5:.1f} -165 Q{hx-11:.1f} -177 {hx:.1f} -177 Q{hx+11:.1f} -177 {hx+10.5+t:.1f} -164 Q{hx+10.5+2*t:.1f} -156 {hx+4+3*t:.1f} -151.5 Q{hx:.1f} -149.5 {hx-4+t:.1f} -151.5 Q{hx-10:.1f} -156 {hx-10.5:.1f} -165 Z" fill="url(#{sh})"/>'
            f'<ellipse cx="{eyeN:.1f}" cy="-164" rx="1.5" ry="1.15" fill="#1A120E"/><ellipse cx="{eyeF:.1f}" cy="-164" rx="{1.5*(1-.35*t):.2f}" ry="1.15" fill="#1A120E"/>'
            f'<path d="M{eyeN-2.4:.1f} -167.6 Q{eyeN:.1f} -168.8 {eyeN+2.2:.1f} -167.6 M{eyeF-1.8:.1f} -167.6 Q{eyeF:.1f} -168.6 {eyeF+1.8*(1-.3*t):.1f} -167.4" stroke="{hair}" stroke-width="1.3" fill="none"/>'
            f'<path d="M{hx+fo*.95:.1f} -165.5 Q{hx+fo+1.2+2.5*t:.1f} -161 {hx+fo+1.4+3.2*t:.1f} -158.8 Q{hx+fo:.1f} -157.8 {hx+fo-1.6:.1f} -158.9" fill="{skin}" stroke="#000" stroke-opacity=".28" stroke-width="1"/>'
            f'<ellipse cx="{hx+fo-.3:.1f}" cy="-158.6" rx=".8" ry=".5" fill="#3A1A10" opacity=".6"/>'
            f'{mouth_d}')
    if female:
        hair_d = (f'<path d="M{hx-12:.1f} -150 Q{hx-15:.1f} -170 {hx-8:.1f} -178 Q{hx+2:.1f} -184 {hx+10:.1f} -177 Q{hx+14:.1f} -168 {hx+12+t:.1f} -158 '
                  f'Q{hx+8:.1f} -170 {hx-2:.1f} -172 Q{hx-7:.1f} -166 {hx-7:.1f} -158 Q{hx-9:.1f} -152 {hx-12:.1f} -150 Z" fill="{hair}"/>')
    else:
        hair_d = (f'<path d="M{hx-11-1.5*t:.1f} -158 Q{hx-13-1.5*t:.1f} -179 {hx:.1f} -180 Q{hx+12:.1f} -180 {hx+11.5:.1f} -168 Q{hx+5+3*t:.1f} -175 {hx-1+5*t:.1f} -172 '
                  f'Q{hx-7+4*t:.1f} -170 {hx-8+5*t:.1f} -163 Q{hx-9+3*t:.1f} -158 {hx-11-1.5*t:.1f} -158 Z" fill="{hair}"/>')
    hat_d = ""
    if hat:
        hat_d = (f'<ellipse cx="{hx+1:.1f}" cy="-175" rx="{17-2*t:.1f}" ry="{4-1.9*t:.1f}" fill="{hat}"/>'
                 f'<path d="M{hx-10:.1f} -175 Q{hx-10:.1f} -190 {hx+1:.1f} -191 Q{hx+12:.1f} -190 {hx+11:.1f} -175 Z" fill="{hat}"/>'
                 f'<path d="M{hx-10:.1f} -178 H{hx+11:.1f}" stroke="#000" stroke-opacity=".5" stroke-width="2.4"/>'
                 f'<path d="M{hx-10:.1f} -175 Q{hx-10:.1f} -190 {hx+1:.1f} -191 Q{hx+12:.1f} -190 {hx+11:.1f} -175 Z" fill="url(#{sh})"/>')
    body = far_leg + f'<g {dark}>{far_arm}</g>' + near_leg + torso + head + hair_d + (ear if t > .15 else '') + hat_d + near_arm
    tf = ' transform="scale(-1 1)"' if flip else ""
    return f'<g{tf}>{body}</g>'


FIG_H = 175   # figure() çizim yüksekliği (Scene.add art_h)


def pole(i=0):
    """Elektrik direği, taban (0,0), 900 birim."""
    return ('<rect x="-7" y="-900" width="14" height="900" fill="#5A4433"/><rect x="-7" y="-900" width="5" height="900" fill="#fff" opacity=".12"/>'
            '<rect x="-60" y="-860" width="120" height="10" fill="#4A3628"/><g fill="#D8D2C4"><rect x="-54" y="-874" width="6" height="14"/><rect x="48" y="-874" width="6" height="14"/></g>')


def tree_simple(i=0):
    """Yuvarlak taçlı ağaç, taban (0,0), 700 birim; gövdede ve taçta ışık yönlü gölge."""
    s = (i * 47) % 5
    blobs = "".join(f'<circle cx="{((j*71+s*13)%300)-150}" cy="{-420-((j*53+s*7)%260)}" r="{90+(j*29)%50}" fill="{["#4F6A2E","#5E7A34","#41592A","#6E8A3C"][j%4]}"/>' for j in range(9))
    hl = "".join(f'<circle cx="{((j*59+s*11)%180)-150}" cy="{-500-((j*41)%200)}" r="{40+(j*17)%30}" fill="#8FA650" opacity=".7"/>' for j in range(5))
    return (f'<path d="M-22 0 Q-14 -200 -16 -380 L16 -380 Q14 -200 24 0 Z" fill="#4A3426"/><path d="M4 0 Q8 -200 6 -380 L16 -380 Q14 -200 24 0 Z" fill="#000" opacity=".3"/>'
            f'<g>{blobs}{hl}{re.sub(r"fill=.#[0-9A-F]+.", "fill=\"url(#lsh)\"", blobs)}</g>')
