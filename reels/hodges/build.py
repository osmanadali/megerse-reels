"""Ann Hodges reel'i: hf/index.html üretir.

python3 reels/hodges/build.py && (cd hf && npx -y hyperframes@0.8.181 render -o renders/hodges-v1.mp4)
Gerçek görseller hf/assets/hodges/ altına konunca (REAL sözlüğü) vektör yerine onlar kullanılır.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from reelkit import HF, anchor, page  # noqa: E402
from artlib import DEFS, FIREBALL, ROCK, TREE, house, person  # noqa: E402

words = json.loads((ROOT / "reels/hodges/words.json").read_text(encoding="utf-8"))
mouth = json.loads((HF / "avatar/mouth-hodges.json").read_text())
VOICE_END = round(words[-1]["endMs"] / 1000 + 0.6, 2)
TOTAL = round(VOICE_END + 4, 2)
FADE = 0.45

# Osman'ın vereceği gerçek görseller (yoksa vektör)
REAL = {k: f"assets/hodges/{v}" for k, v in {"hookphoto": "ek-1.jpg", "bruise": "ek-2.jpg", "bed": "ann-yatak.jpg", "police": "cati-polis.jpg",
                                             "mckinney": "mckinney-aile.jpg", "museum": "muze.jpg"}.items()}
has = lambda k: (HF / REAL[k]).exists()

A = lambda p, after=0.0: anchor(words, p, after)
T = {
    "hook": 0.0,
    "town": A("30"),
    "room": A("Saat"),
    "bruise": A("Kalçasında"),
    "panic": A("Kasaba ayağa"),
    "police": A("Polis"),
    "door": A("Sonra ev"),
    "court": A("Bir yıl"),
    "nobody": A("Ama artık"),
    "meg": A("Meğerse"),
    "farmer": A("Çiftçi"),
    "end": A("Taş Ann'e çarptı"),
    "sources": VOICE_END,
}
keys = list(T)
S = {k: (T[k], T[keys[i + 1]] if i + 1 < len(keys) else TOTAL) for i, k in enumerate(keys)}
hit = A("Yaklaşık")      # taşın düşüş cümlesi
radio = A("radyoya")
hip = A("kalçasına")
stopper = A("kapı tutucu")
alive = A("Ama yaşıyor")
road = A("yolda")
house_car = A("bir ev")


def win(k):
    a, b = S[k]
    return a, round((b + FADE if b < TOTAL else b) - a, 2)


def scene(k, inner, style=""):
    a, d = win(k)
    return f'<div class="scene clip" id="s-{k}" data-start="{a}" data-duration="{d}" data-track-index="1" style="{style}"><div class="fill" id="{k}-in">{inner}</div></div>'


def real_or(k, fallback, pos="50% 50%"):
    return f'<div class="fill" id="{k}-kb"><img src="{REAL[k]}" alt="" style="object-position:{pos}"></div><div class="vign"></div>' if has(k) else fallback


# ---------- sahneler ----------
hook = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#sky)"/>
<path d="M0 860 Q240 800 480 840 T960 820 V1080 H0 Z" fill="#7FA35A"/><path d="M0 930 Q300 880 620 920 T960 900 V1080 H0 Z" fill="url(#lawn)"/>
{house(520, 830, .55, "hh")}
<g transform="translate(160 840) scale(.6)">{TREE}</g>
<g id="hookball" transform="translate(900 80)">{FIREBALL}</g>
<rect id="hookflash" width="960" height="1080" fill="#FFF6E0" opacity="0"/>
</svg><div class="chip red">GERÇEK OLAY · 1954</div>"""

town_fallback = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#sky)"/>
<path d="M0 760 Q240 700 480 740 T960 720 V1080 H0 Z" fill="#7FA35A"/><rect y="860" width="960" height="220" fill="url(#lawn)"/>
<g id="townhouse">{house(480, 650, 1.0, "th")}</g>
<g transform="translate(110 760) scale(.9)">{TREE}</g>
<path d="M0 880 H960" stroke="#E9E2D0" stroke-width="10" stroke-dasharray="30 20" opacity=".5"/>
</svg>"""
town = (real_or("roof", town_fallback) if False else town_fallback) + """
<div id="datecard" style="position:absolute; left:40px; top:40px; padding:22px 28px; border-radius:22px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA">
  <div style="font-weight:800; font-size:64px; color:#F5B82E; letter-spacing:.02em">30.11.1954</div>
  <div style="font-weight:600; font-size:32px; color:#C9D6E4; margin-top:6px">📍 SYLACAUGA, ALABAMA</div>
</div>"""

room = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<g id="roomcam">
<rect y="0" width="960" height="150" fill="#5B3A2E"/><path d="M0 150 H960" stroke="#2B1A12" stroke-width="10"/>
<rect y="150" width="960" height="690" fill="url(#wall)"/>
{''.join(f'<path d="M{x} 160 V830" stroke="#D9C49C" stroke-width="3" opacity=".6"/>' for x in range(40, 960, 60))}
<rect y="830" width="960" height="250" fill="url(#floor)"/>{''.join(f'<path d="M0 {y} H960" stroke="#4A2E1A" stroke-width="3" opacity=".6"/>' for y in range(870, 1080, 40))}
<g transform="translate(150 380)"><rect x="-90" y="-110" width="180" height="200" fill="#CFE6F5" stroke="#3A2A1E" stroke-width="10"/><path d="M0 -110 V90 M-90 -10 H90" stroke="#3A2A1E" stroke-width="7"/><path d="M-96 -116 Q-60 0 -96 96" fill="#C9675C"/><path d="M96 -116 Q60 0 96 96" fill="#C9675C"/><g id="winball" transform="translate(60 -80)"><circle r="18" fill="url(#fire)"/></g></g>
<g transform="translate(720 300)" id="clock"><circle r="62" fill="#F7F2E6" stroke="#5A3B26" stroke-width="10"/>{''.join(f'<rect x="-3" y="-54" width="6" height="12" fill="#3A2A1E" transform="rotate({a})"/>' for a in range(0, 360, 30))}<rect id="hourhand" x="-5" y="-34" width="10" height="38" rx="4" fill="#1F1A16"/><rect id="minhand" x="-3" y="-50" width="6" height="54" rx="3" fill="#1F1A16"/><circle r="6" fill="#B23A2E"/></g>
<g id="radio" transform="translate(760 700)"><rect x="-110" y="-150" width="220" height="250" rx="16" fill="url(#wood)" stroke="#3A2010" stroke-width="6"/><rect x="-80" y="-120" width="160" height="80" rx="10" fill="#E9D9A8" stroke="#3A2010" stroke-width="4"/><path d="M-60 -80 H60" stroke="#B23A2E" stroke-width="4"/>{''.join(f'<path d="M{x} -20 V80" stroke="#4A2A14" stroke-width="5"/>' for x in range(-70, 80, 20))}<circle cx="-50" cy="-60" r="0"/><g id="radiocrack" opacity="0"><path d="M-40 -110 L-10 -70 L-30 -40 L10 -10 M-10 -70 L30 -90" stroke="#1A0E06" stroke-width="5" fill="none"/></g></g>
<g id="couchg" transform="translate(400 760)">
  <rect x="-260" y="-150" width="520" height="130" rx="40" fill="url(#couch)" stroke="#1D3B3A" stroke-width="6"/>
  <rect x="-280" y="-40" width="560" height="110" rx="30" fill="url(#couch)" stroke="#1D3B3A" stroke-width="6"/>
  <rect x="-300" y="-120" width="70" height="190" rx="30" fill="#3B7372" stroke="#1D3B3A" stroke-width="6"/><rect x="230" y="-120" width="70" height="190" rx="30" fill="#3B7372" stroke="#1D3B3A" stroke-width="6"/>
  <path d="M-240 70 L-250 110 M240 70 L250 110" stroke="#3A2010" stroke-width="12" stroke-linecap="round"/>
  <ellipse cx="-180" cy="-62" rx="62" ry="34" fill="#F4EEE0" stroke="#9C9283" stroke-width="3"/>
  <g id="ann"><circle cx="-170" cy="-92" r="38" fill="#E8B48E" stroke="#5A3B26" stroke-width="3"/><path d="M-210 -96 Q-200 -140 -150 -132 Q-120 -126 -132 -90 Q-160 -118 -210 -96 Z" fill="#4A2E1E"/><path d="M-186 -88 q8 4 16 0" stroke="#3A2010" stroke-width="3" fill="none"/>
  <path d="M-140 -70 Q0 -110 210 -66 Q230 -40 200 -20 Q0 -14 -140 -26 Z" fill="#C9675C" stroke="#7A3530" stroke-width="4"/>{''.join(f'<path d="M{x} -96 l20 70" stroke="#E8958A" stroke-width="4" opacity=".6"/>' for x in range(-100, 200, 40))}</g>
  <circle id="hipmark" cx="40" cy="-80" r="0" fill="url(#bruise)"/>
</g>
<g id="hole" opacity="0"><path d="M460 140 L500 110 L540 150 L580 120 L560 170 L470 172 Z" fill="#10141C"/><path d="M450 150 l-20 30 M590 130 l25 25 M520 170 l5 30" stroke="#5B3A2E" stroke-width="8" stroke-linecap="round"/></g>
<path id="traj" d="M520 150 L740 560 L560 640 L440 690" fill="none" stroke="#FF8A1F" stroke-width="7" stroke-dasharray="18 14" opacity="0"/>
<g id="rock" transform="translate(520 60) scale(.8)" opacity="0">{ROCK}</g>
<g id="debris" opacity="0">{''.join(f'<rect x="{500+(i*37)%90}" y="{150+(i*23)%40}" width="{8+i%3*4}" height="{6+i%4*3}" fill="#5B3A2E" class="deb"/>' for i in range(12))}</g>
<circle id="impact" cx="520" cy="150" r="10" fill="url(#flash)" opacity="0"/>
<circle id="impact2" cx="440" cy="690" r="10" fill="url(#flash)" opacity="0"/>
</g>
<g id="kg" opacity="0"><rect x="600" y="40" width="300" height="86" rx="18" fill="#0B1220" stroke="#FF8A1F" stroke-width="4"/><text x="750" y="98" text-anchor="middle" font-family="Mont" font-weight="800" font-size="46" fill="#FF8A1F">≈ 4 KG</text></g>
</svg><div class="chip" id="timechip">SAAT 12:45</div>"""

bruise_fallback = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="#101826"/>
<rect x="120" y="120" width="720" height="840" rx="36" fill="#F4F1EA"/>
<text x="180" y="210" font-family="Mont" font-weight="800" font-size="40" fill="#0B1220">TIBBİ KAYIT · 1954</text>
<path d="M180 240 H780" stroke="#C9C2B2" stroke-width="4"/>
<path d="M330 320 C250 420 250 640 330 860 L630 860 C710 640 710 420 630 320 Z" fill="#E8C3A4" stroke="#8A6248" stroke-width="5"/>
<circle id="bruisespot" cx="560" cy="560" r="150" fill="url(#bruise)"/>
<text x="480" y="920" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#5A5248">sol kalça · büyük morluk</text>
</svg>"""
bruise = f"""<div class="fill" id="bruisekb"><img src="{REAL['bruise']}" alt="" style="object-position:62% 60%"></div>
<div class="fill" id="bedwrap" style="opacity:0"><div class="fill" id="bedkb"><img src="{REAL['bed']}" alt="" style="object-position:70% 40%"></div></div><div class="vign"></div>""" + """
<div id="stamp" style="position:absolute; left:120px; top:420px; width:720px; padding:20px; border:8px solid #E8524A; border-radius:18px; color:#E8524A; background:rgba(244,241,234,.92); text-align:center; font-weight:800; font-size:52px; line-height:1.1; transform:rotate(-8deg)">KAYITLARA GEÇEN<br>İLK İNSAN</div>"""

panic = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#sky)"/><rect y="760" width="960" height="320" fill="url(#lawn)"/>
{house(480, 600, .9, "ph")}
<g id="crowd">{''.join('<g>' + person(80 + i * 105, 1010 + (i % 2) * 30, .9 + (i % 3) * .08, ["#1F2733", "#2E3B4E", "#3A2A1E", "#22303F"][i % 4], i % 2 == 0) + '</g>' for i in range(9))}</g>
</svg>
<div class="qb" id="q1" style="left:60px; top:120px">UÇAK MI DÜŞTÜ?</div>
<div class="qb" id="q2" style="right:60px; top:260px; background:#E8524A; color:#fff">SOVYET SALDIRISI MI?</div>"""

police = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="#14202F"/>
{''.join(f'<path d="M0 {y} H960" stroke="#1C2B3D" stroke-width="2"/>' for y in range(0, 1080, 40))}
<g id="evbox"><g transform="translate(480 470)"><path d="M-260 -60 L0 -150 L260 -60 L0 30 Z" fill="#C9A26B" stroke="#5A3B1E" stroke-width="6"/><path d="M-260 -60 V160 L0 250 V30 Z" fill="#B08852" stroke="#5A3B1E" stroke-width="6"/><path d="M260 -60 V160 L0 250 V30 Z" fill="#9C7442" stroke="#5A3B1E" stroke-width="6"/>
<g transform="translate(0 -40) scale(1.3)">{ROCK}</g>
<g transform="translate(130 120) rotate(-12)"><rect x="-90" y="-36" width="180" height="72" rx="10" fill="#F4F1EA" stroke="#5A3B1E" stroke-width="4"/><text x="0" y="14" text-anchor="middle" font-family="Mont" font-weight="800" font-size="38" fill="#B23A2E">DELİL</text></g></g></g>
</svg>
<div id="afstamp" style="position:absolute; left:110px; top:760px; width:740px; padding:18px; border:8px solid #5BC0EB; border-radius:16px; color:#5BC0EB; text-align:center; font-weight:800; font-size:46px; transform:rotate(-6deg); background:rgba(11,18,32,.85)">ABD HAVA KUVVETLERİ</div>"""

door = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#siding)"/>{''.join(f'<path d="M0 {y} H960" stroke="#C9BFA6" stroke-width="3"/>' for y in range(20, 1080, 36))}
<g id="doorg" transform="translate(480 620)"><rect x="-200" y="-420" width="400" height="760" fill="#3A2A1E"/><rect x="-170" y="-390" width="340" height="730" rx="6" fill="#7A2E22" stroke="#2B1510" stroke-width="8"/>
<rect x="-130" y="-340" width="110" height="260" rx="8" fill="none" stroke="#5A1E16" stroke-width="7"/><rect x="20" y="-340" width="110" height="260" rx="8" fill="none" stroke="#5A1E16" stroke-width="7"/><rect x="-130" y="-20" width="260" height="300" rx="8" fill="none" stroke="#5A1E16" stroke-width="7"/>
<circle cx="120" cy="-20" r="16" fill="#E7C46A"/></g>
<g id="knock" opacity="0"><path d="M640 300 q30 30 0 60 M670 280 q48 50 0 100 M700 260 q66 70 0 140" stroke="#0B1220" stroke-width="8" fill="none" stroke-linecap="round"/></g>
</svg>
<div id="quote" style="position:absolute; left:40px; right:40px; top:60px; padding:30px 34px; border-radius:26px; background:#0B1220; border:4px solid #F5B82E">
  <div style="font-weight:800; font-size:50px; line-height:1.15; color:#F4F1EA">“Taş benim evime düştü, benimdir.”</div>
  <div style="font-weight:600; font-size:32px; color:#F5B82E; margin-top:14px">— Ev sahibi Birdie Guy</div>
</div>"""

court = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="#16202E"/>
<g id="scale" transform="translate(480 560)">
<rect x="-12" y="-360" width="24" height="560" fill="#C9A24A"/><rect x="-150" y="200" width="300" height="40" rx="10" fill="#A8842E"/><circle cy="-370" r="24" fill="#E7C46A"/>
<g id="beam"><rect x="-340" y="-370" width="680" height="18" rx="9" fill="#E7C46A"/>
<g id="panL" transform="translate(-320 -360)"><path d="M0 0 L-80 200 M0 0 L80 200" stroke="#C9A24A" stroke-width="5"/><path d="M-120 200 H120 Q100 250 0 250 Q-100 250 -120 200 Z" fill="#E7C46A"/><g transform="translate(0 160)">{ROCK}</g></g>
<g id="panR" transform="translate(320 -360)"><path d="M0 0 L-80 200 M0 0 L80 200" stroke="#C9A24A" stroke-width="5"/><path d="M-120 200 H120 Q100 250 0 250 Q-100 250 -120 200 Z" fill="#E7C46A"/>{''.join(f'<rect x="-70" y="{180-i*14}" width="140" height="22" rx="4" fill="url(#cash)" stroke="#3E5E30" stroke-width="3"/>' for i in range(5))}<text x="0" y="110" text-anchor="middle" font-family="Mont" font-weight="800" font-size="48" fill="#9CC48A">$500</text></g></g>
</g>
</svg>
<div id="cal" style="position:absolute; right:40px; top:40px; width:200px; border-radius:18px; overflow:hidden; text-align:center; background:#F4F1EA; color:#0B1220">
  <div style="background:#E8524A; color:#fff; font-weight:800; font-size:30px; padding:8px">DAVA</div><div style="font-weight:800; font-size:64px; padding:10px 0">1 YIL</div></div>"""

nobody = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#siding)"/>{''.join(f'<path d="M0 {y} H960" stroke="#C9BFA6" stroke-width="3"/>' for y in range(20, 1080, 36))}
<rect y="860" width="960" height="220" fill="url(#floor)"/>
<g id="ndoor" transform="translate(560 520)"><rect x="-240" y="-420" width="40" height="760" fill="#3A2A1E"/><path d="M-200 -420 L120 -380 L120 300 L-200 340 Z" fill="#7A2E22" stroke="#2B1510" stroke-width="8"/><circle cx="80" cy="-20" r="16" fill="#E7C46A"/></g>
<g id="stoprock" transform="translate(720 860) scale(1.5)">{ROCK}</g>
<g id="tag" transform="translate(300 300) rotate(-10)"><path d="M-160 -70 H130 L180 0 L130 70 H-160 Z" fill="#F5B82E" stroke="#7A5A10" stroke-width="5"/><circle cx="130" cy="0" r="12" fill="#7A5A10"/><text x="-20" y="18" text-anchor="middle" font-family="Mont" font-weight="800" font-size="52" fill="#0B1220">SATILIK</text><path id="nocross" d="M-150 -60 L120 60" stroke="#E8524A" stroke-width="14" stroke-linecap="round" stroke-dasharray="300" stroke-dashoffset="300"/></g>
</svg>
<div class="chip red" id="stopchip" style="opacity:0">KAPI TUTUCU</div>"""

meg = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="#05080E"/>
<circle cx="480" cy="560" r="300" fill="url(#fire)" opacity=".18"/>
<g id="frag1" transform="translate(480 600) scale(2.2)">{ROCK}</g>
<g id="frag2" transform="translate(480 600) scale(1.4)" opacity="0">{ROCK}<circle r="70" fill="url(#fire)" opacity=".35"/></g>
</svg>
<div id="megtxt" class="big" style="top:150px; font-size:140px; color:#F5B82E; text-shadow:0 10px 0 #000">MEĞERSE</div>
<div id="megsub" class="big" style="top:330px; font-size:44px; color:#C9D6E4">2. PARÇA</div>"""

farmer = f"""<svg class="fill" viewBox="0 0 960 1080">{DEFS}
<rect width="960" height="1080" fill="url(#sky)"/>
<path d="M0 560 Q480 500 960 560 V1080 H0 Z" fill="#B9A06A"/><path d="M0 560 L960 560 L960 1080 L0 1080 Z" fill="#C2A874" opacity=".5"/>
<path d="M400 560 L560 560 L900 1080 L60 1080 Z" fill="#9B8A6A"/><path d="M480 560 V1080" stroke="#E9E2D0" stroke-width="8" stroke-dasharray="40 40" opacity=".6"/>
{''.join(f'<path d="M{x} 560 L{x*2-480} 1080" stroke="#8A9A4C" stroke-width="10" opacity=".4"/>' for x in range(40, 400, 60))}
<g id="farmrock" transform="translate(470 880)">{ROCK}</g>
<g id="farmerman"><g transform="translate(300 900) scale(1.5)"><circle cx="0" cy="-112" r="26" fill="#C98B63"/><path d="M-40 -132 H40 L28 -148 H-28 Z" fill="#C9A24A" stroke="#7A5A1E" stroke-width="3"/><path d="M-40 -80 Q0 -96 40 -80 L50 20 H-50 Z" fill="#3B6EA5"/><rect x="-30" y="-80" width="60" height="70" fill="#2E5A8A"/><rect x="-36" y="18" width="26" height="90" rx="10" fill="#2E5A8A"/><rect x="10" y="18" width="26" height="90" rx="10" fill="#2E5A8A"/></g></g>
<g id="rich" opacity="0">
  <g id="newhouse" transform="translate(720 420) scale(.5)">{house(0, 0, 1, "nh")}</g>
  <g id="car"><g transform="translate(220 470)"><path d="M-150 0 Q-140 -60 -80 -70 L-40 -120 H60 L110 -70 Q160 -60 160 0 Z" fill="#E0503E" stroke="#5A1A12" stroke-width="5"/><path d="M-30 -110 H50 L90 -70 H-60 Z" fill="#CFE6F5" stroke="#5A1A12" stroke-width="4"/><circle cx="-80" cy="4" r="30" fill="#1A1A1A"/><circle cx="90" cy="4" r="30" fill="#1A1A1A"/><circle cx="-80" cy="4" r="12" fill="#BFC5CA"/><circle cx="90" cy="4" r="12" fill="#BFC5CA"/></g></g>
  {''.join(f'<rect class="bill" x="{380+(i*53)%220}" y="{200+(i*31)%120}" width="70" height="34" rx="4" fill="url(#cash)" stroke="#3E5E30" stroke-width="3"/>' for i in range(10))}
</g>
</svg>
<div class="chip" style="bottom:36px">ÇİFTÇİ JULIUS McKINNEY</div>
<div class="fill" id="mckwrap" style="background:#0B1220"><div class="fill" id="mckkb"><img src="{REAL['mckinney']}" alt="" style="object-position:62% 78%; filter:contrast(1.1)"></div><div class="vign"></div><div class="chip top">McKINNEY AİLESİ VE 2. PARÇA · 1954</div></div>"""

end_fallback_left = f"""<svg viewBox="0 0 480 1080" style="position:absolute; left:0; top:0; width:480px; height:1080px">{DEFS}
<rect width="480" height="1080" fill="#2A2420"/><path d="M60 180 L380 220 L380 860 L60 900 Z" fill="#7A2E22" stroke="#2B1510" stroke-width="8"/><g transform="translate(330 900) scale(1.3)">{ROCK}</g></svg>"""
end_left = f'<div style="position:absolute; left:0; top:0; width:480px; height:1080px; overflow:hidden"><img src="{REAL["museum"]}" style="width:100%; height:100%; object-fit:cover; object-position:44% 30%"></div>'
end = f"""{end_left}
<svg viewBox="0 0 480 1080" style="position:absolute; left:480px; top:0; width:480px; height:1080px">{DEFS}
<rect width="480" height="1080" fill="#BFD8EC"/><rect y="760" width="480" height="320" fill="url(#lawn)"/>
<g transform="translate(240 620) scale(.62)">{house(0, 0, 1, "eh")}</g>
<g transform="translate(240 900) scale(.8)"><path d="M-150 0 Q-140 -60 -80 -70 L-40 -120 H60 L110 -70 Q160 -60 160 0 Z" fill="#E0503E" stroke="#5A1A12" stroke-width="5"/><circle cx="-80" cy="4" r="30" fill="#1A1A1A"/><circle cx="90" cy="4" r="30" fill="#1A1A1A"/></g></svg>
<div style="position:absolute; left:476px; top:0; width:8px; height:1080px; background:#F4F1EA"></div>
<div class="endlab" style="left:24px">ANN<br><span>taş müzede, para yok</span></div>
<div class="endlab" style="left:504px">McKINNEY<br><span>ev + araba</span></div>"""

sources = """<div class="fill" style="padding:90px 70px; background:#0B1220">
<div style="font-weight:800; font-size:56px; color:#F5B82E; margin-bottom:40px">KAYNAKLAR</div>
<div class="src">Fotoğraflar: arşiv / basın, 1954<br>Encyclopedia of Alabama: Hodges Meteorite Strike<br>Wikipedia: Sylacauga (meteorite)<br>ScienceAlert (2024)<br>Smithsonian Magazine<br>Alabama Museum of Natural History</div></div>"""

hook_vector = hook  # artlib adayı: ateş topu + ev
hook = f"""<div class="fill" id="hookkb"><img src="{REAL['hookphoto']}" alt="" style="object-position:50% 35%; filter:contrast(1.08)"></div><div class="vign"></div>
<div class="chip red">GERÇEK FOTOĞRAF · 1954</div>"""
police = f"""<div class="fill" id="policekb"><img src="{REAL['police']}" alt="" style="object-position:60% 30%"></div><div class="vign"></div>
<div id="afstamp" style="position:absolute; left:110px; top:780px; width:740px; padding:18px; border:8px solid #5BC0EB; border-radius:16px; color:#5BC0EB; text-align:center; font-weight:800; font-size:46px; transform:rotate(-6deg); background:rgba(11,18,32,.85)">ABD HAVA KUVVETLERİ</div>
<div class="chip top">POLİS ŞEFİ VE ANN HODGES</div>"""
# ================= v2 sahneleri (artlib2: dokulu, ışıklı, alan derinliği; motion blur) =================
from artlib2 import DEFS2, car50s, cloud, farmer2, fireball2, gavel, house2, obj_svg, person2, rock2, svg, tree_autumn  # noqa: E402

MB = "data-hf-motion-blur"


def mover(idn, inner, w, h, extra=""):
    """motion blur'lü hareketli nesne: panel koordinatında x/y ile konumlanır (sol-üst 0,0)."""
    return f'<div id="{idn}" {MB} style="position:absolute; left:0; top:0; width:{w}px; height:{h}px; {extra}">{obj_svg(inner, w, h)}</div>'


town = svg(f'''<rect width="960" height="1080" fill="url(#sky2)"/>
<g id="tclouds">{cloud(200, 170, 1.1)}{cloud(760, 110, .9, .85)}{cloud(560, 260, .6, .7)}</g>
<g filter="url(#dof)">{tree_autumn(60, 640, 1.2, 1)}{tree_autumn(300, 620, .9, 5)}{tree_autumn(900, 640, 1.3, 3)}</g>
<rect y="600" width="960" height="80" fill="url(#hazeG)"/>
<rect y="640" width="960" height="440" fill="url(#grass2)" filter="url(#grainy)"/>
<path d="M380 1080 L450 760 L510 760 L600 1080 Z" fill="#B8AE98" opacity=".8" filter="url(#grainy)"/>
<g id="thouse">{house2(470, 520, .78, "th2")}</g>
{tree_autumn(790, 790, 1.15, 2)}
<g transform="translate(250 840)"><rect x="-6" y="-80" width="12" height="80" fill="#5A4030"/><rect x="-34" y="-112" width="68" height="40" rx="18" fill="#4A6A8A" stroke="#22303F" stroke-width="3"/><rect x="26" y="-108" width="6" height="24" fill="#C8402F"/></g>
<g id="tfence" filter="url(#dof2)">{''.join(f'<path d="M{x} 1080 V930 L{x+14} 912 L{x+28} 930 V1080 Z" fill="#F4F0E6" stroke="#B8AE98" stroke-width="3"/>' for x in range(-20, 980, 52))}<rect x="-20" y="960" width="1000" height="14" fill="#E9E2D0"/><rect x="-20" y="1030" width="1000" height="14" fill="#E9E2D0"/></g>''') + """
<div id="datecard" style="position:absolute; left:40px; top:40px; padding:22px 28px; border-radius:22px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA">
  <div style="font-weight:800; font-size:64px; color:#F5B82E; letter-spacing:.02em">30.11.1954</div>
  <div style="font-weight:600; font-size:32px; color:#C9D6E4; margin-top:6px">SYLACAUGA, ALABAMA</div>
</div>"""

couch = '''<g filter="url(#shadow)">
<rect x="-280" y="-160" width="560" height="140" rx="46" fill="#3F7A78"/><rect x="-280" y="-160" width="560" height="140" rx="46" fill="url(#clapboard)" opacity=".3"/>
<path d="M-280 -100 C-200 -120 200 -120 280 -100" stroke="#2C5A58" stroke-width="4" fill="none"/>
''' + "".join(f'<circle cx="{x}" cy="-110" r="5" fill="#2A5452"/>' for x in range(-200, 220, 100)) + '''
<rect x="-300" y="-46" width="600" height="116" rx="34" fill="#3B7372"/><path d="M-300 -10 H300" stroke="#2C5A58" stroke-width="3"/>
<rect x="-330" y="-130" width="76" height="200" rx="34" fill="#346866"/><rect x="254" y="-130" width="76" height="200" rx="34" fill="#346866"/>
<rect x="-330" y="-130" width="30" height="200" rx="14" fill="#000" opacity=".15"/>
<path d="M-250 70 L-262 116 M250 70 L262 116" stroke="#2A1A10" stroke-width="12" stroke-linecap="round"/></g>
<g id="ann2">
<ellipse cx="-190" cy="-72" rx="70" ry="36" fill="#F4EEE0" stroke="#B9AE95" stroke-width="3"/><path d="M-250 -80 Q-190 -96 -130 -80" stroke="#D9CFBC" stroke-width="3" fill="none"/>
<path d="M-160 -112 C-140 -104 -128 -86 -132 -70 L-170 -60 Z" fill="#E2A982"/>
<ellipse cx="-176" cy="-98" rx="34" ry="30" fill="#E8B48E"/><path d="M-196 -92 q10 6 20 0" stroke="#5A3020" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M-180 -84 q6 4 12 0" stroke="#B5655A" stroke-width="3" fill="none"/>
<path d="M-214 -100 C-214 -136 -170 -146 -146 -124 C-138 -112 -142 -100 -150 -96 C-160 -120 -190 -122 -214 -100 Z" fill="#4A2E1E"/>''' + "".join(f'<circle cx="{-206+i*12}" cy="{-118-(i%2)*8}" r="9" fill="#5A3826"/>' for i in range(6)) + '''
<path d="M-150 -84 C-60 -120 120 -112 236 -78 C252 -60 244 -30 222 -20 C80 -10 -60 -12 -150 -30 Z" fill="url(#quilt)" stroke="#8C7A5E" stroke-width="3"/>
<path d="M-150 -84 C-60 -120 120 -112 236 -78 C252 -60 244 -30 222 -20 C80 -10 -60 -12 -150 -30 Z" fill="#000" opacity=".08"/>
<path d="M-60 -104 C20 -116 120 -110 220 -80" stroke="#fff" stroke-width="4" opacity=".35" fill="none"/>
<path d="M-140 -60 C-120 -70 -100 -66 -84 -58" stroke="#E2A982" stroke-width="16" stroke-linecap="round" fill="none"/></g>
<circle id="hipmark2" cx="60" cy="-92" r="0" fill="#5A2E6E" opacity=".55" filter="url(#dof2)"/>'''

radio_svg = '''<g filter="url(#shadow)"><rect x="-120" y="-170" width="240" height="280" rx="18" fill="#7A4424" stroke="#3A1E0E" stroke-width="5" filter="url(#woodgrain)"/>
<rect x="-96" y="-142" width="192" height="86" rx="12" fill="#2A1A10"/><rect x="-86" y="-132" width="172" height="66" rx="8" fill="#E9C978"/><rect x="-86" y="-132" width="172" height="66" rx="8" fill="#FFE3A0" opacity=".5" filter="url(#glow)"/>
''' + "".join(f'<path d="M{x} -120 V-78" stroke="#7A5A1E" stroke-width="2"/>' for x in range(-70, 80, 14)) + '''<path d="M10 -128 V-70" stroke="#B23A2E" stroke-width="4"/>
<rect x="-96" y="-40" width="192" height="120" rx="10" fill="#C9B48A"/>''' + "".join(f'<path d="M-90 {y} H90" stroke="#9C845A" stroke-width="3"/>' for y in range(-32, 80, 10)) + '''
<circle cx="-50" cy="94" r="10" fill="url(#brass)"/><circle cx="50" cy="94" r="10" fill="url(#brass)"/>
<g id="radiocrack2" opacity="0"><path d="M-70 -130 L-30 -90 L-50 -60 L-10 -30 L-20 10 M-30 -90 L20 -110 M-50 -60 L-90 -40" stroke="#120A04" stroke-width="5" fill="none"/></g></g>'''

clock = '''<g filter="url(#shadow)"><circle r="70" fill="url(#brass)"/><circle r="58" fill="#F7F2E6"/>''' + "".join(f'<rect x="-3" y="-52" width="6" height="12" fill="#3A2A1E" transform="rotate({a})"/>' for a in range(0, 360, 30)) + '''
<rect id="hourhand2" x="-5" y="-32" width="10" height="36" rx="4" fill="#1F1A16"/><rect id="minhand2" x="-3" y="-48" width="6" height="52" rx="3" fill="#1F1A16"/><circle r="6" fill="#B23A2E"/></g>'''

room = svg(f'''<g id="roomcam2">
<rect width="960" height="170" fill="#EDE6D6" filter="url(#grainy)"/><rect y="160" width="960" height="18" fill="#D9CFBC"/><rect y="176" width="960" height="6" fill="#B9AE95"/>
<rect y="182" width="960" height="660" fill="url(#wallpaper)"/>
<rect y="182" width="960" height="660" fill="url(#wallShade)" opacity=".25"/>
<rect y="830" width="960" height="250" fill="#7A4A2A" filter="url(#woodgrain)"/>{''.join(f'<path d="M0 {y} H960" stroke="#4A2A14" stroke-width="3" opacity=".5"/>' for y in range(870, 1080, 42))}
<rect y="826" width="960" height="14" fill="#E9E2D0"/>
<path d="M150 1080 L250 900 L800 900 L900 1080 Z" fill="url(#rug)" opacity=".9" filter="url(#grainy)"/>
<g transform="translate(150 420)"><rect x="-100" y="-130" width="200" height="230" fill="#BFD8EC"/><rect x="-100" y="-130" width="200" height="230" fill="url(#glass2)" opacity=".5"/>
<g id="winball2" transform="translate(70 -110) scale(.18)">{fireball2(1)}</g>
<path d="M-100 -130 H100 V100 H-100 Z" fill="none" stroke="#F4F0E6" stroke-width="16"/><path d="M0 -130 V100 M-100 -15 H100" stroke="#F4F0E6" stroke-width="9"/>
<path d="M-124 -150 C-96 -40 -120 40 -96 120 L-140 120 Z" fill="#C9675C"/><path d="M-124 -150 C-110 -40 -130 40 -112 120" stroke="#9A4A40" stroke-width="5" fill="none"/>
<path d="M124 -150 C96 -40 120 40 96 120 L140 120 Z" fill="#C9675C"/><path d="M124 -150 C110 -40 130 40 112 120" stroke="#9A4A40" stroke-width="5" fill="none"/>
<rect x="-150" y="-160" width="300" height="16" rx="6" fill="#7A4424"/></g>
<polygon points="60,300 250,300 640,1080 120,1080" fill="#FFF3D0" opacity=".16" filter="url(#dof)"/>
<g transform="translate(470 300)"><rect x="-80" y="-60" width="160" height="120" fill="#7A4424" filter="url(#woodgrain)"/><rect x="-66" y="-46" width="132" height="92" fill="#8FA88A"/><path d="M-66 30 L-20 -10 L20 20 L66 -20 V46 H-66 Z" fill="#5A7A4A"/></g>
<g transform="translate(760 300)">{clock}</g>
<g transform="translate(770 730)">{radio_svg}</g>
<g transform="translate(420 780)">{couch}</g>
<g id="hole2" opacity="0"><path d="M450 120 L490 92 L540 130 L590 100 L580 160 L520 176 L462 168 Z" fill="#14181F"/><path d="M440 140 L400 190 M600 120 L650 160 M520 176 L530 230 M470 168 L430 210" stroke="#B9AE95" stroke-width="5" stroke-linecap="round"/><polygon points="470,170 590,170 680,830 380,830" fill="#FFF3D0" opacity=".22" filter="url(#dof)"/></g>
<g id="traj2" opacity="0"><path d="M520 170 L740 600 L560 650 L470 690" fill="none" stroke="#FF8A1F" stroke-width="6" stroke-dasharray="16 12"/></g>
<g id="dust2" opacity="0" filter="url(#dof)"><ellipse cx="520" cy="200" rx="160" ry="80" fill="#E9E2D0"/><ellipse cx="460" cy="260" rx="110" ry="60" fill="#D9CFBC"/></g>
<g id="burst2" opacity="0"><circle cx="520" cy="160" r="120" fill="url(#fire2)" filter="url(#glow)"/></g>
<g id="burst3" opacity="0"><circle cx="470" cy="690" r="90" fill="#FFF6D8" filter="url(#glow)"/></g>
</g>
<g filter="url(#dof)" transform="translate(40 640)"><rect x="-8" y="0" width="16" height="440" fill="#2A1A10"/><path d="M-70 0 L70 0 L44 -110 L-44 -110 Z" fill="#E9D3A0"/><path d="M-70 0 L70 0 L44 -110 L-44 -110 Z" fill="#FFE9B0" opacity=".5" filter="url(#glow)"/></g>''') + \
    mover("rock2", rock2(.9), 160, 160, "opacity:0") + """
<div id="kg2" style="position:absolute; right:36px; top:36px; padding:14px 22px; border-radius:16px; background:#0B1220; border:4px solid #FF8A1F; color:#FF8A1F; font-weight:800; font-size:44px; opacity:0">≈ 4 KG</div>
<div class="chip">SAAT 12:45</div>"""

panic = svg(f'''<rect width="960" height="1080" fill="url(#sky2)"/>
<path d="M980 -40 L420 420 L440 440 L1000 0 Z" fill="url(#smoke)" opacity=".7" filter="url(#dof)"/>
<g filter="url(#dof)">{house2(140, 560, .45, "pa")}{house2(820, 560, .45, "pb")}{tree_autumn(480, 600, .8, 6)}</g>
<rect y="600" width="960" height="60" fill="url(#hazeG)"/>
<rect y="640" width="960" height="440" fill="url(#grass2)" filter="url(#grainy)"/><path d="M0 760 H960 V860 H0 Z" fill="#8A8478" filter="url(#grainy)"/><path d="M0 808 H960" stroke="#E9E2D0" stroke-width="6" stroke-dasharray="40 30"/>
<g transform="translate(720 800)">{car50s(.75, "#2F6E8A")}</g>
<g id="crowd2">{''.join('<g>' + person2(70 + i * 102, 1000 + (i % 3) * 24, .95 + (i % 3) * .1, ["#2E3B4E", "#5A3A2A", "#3A4A3A", "#6A5A4A", "#22303F"][i % 5], i % 2 == 0, ["#C98B63", "#E8B48E", "#8A5A3E"][i % 3]) + '</g>' for i in range(9))}</g>''') + """
<div class="qb" id="q1" style="left:50px; top:110px">UÇAK MI DÜŞTÜ?</div>
<div class="qb" id="q2" style="right:50px; top:250px; background:#E8524A; color:#fff">SOVYET SALDIRISI MI?</div>"""

door = svg(f'''<rect width="960" height="1080" fill="url(#wallLit)"/><rect width="960" height="1080" fill="url(#clapboard)"/>
<rect y="930" width="960" height="150" fill="#9C8F78" filter="url(#grainy)"/>
<g transform="translate(150 260)"><rect x="-30" y="-10" width="60" height="16" fill="#3A2A1E"/><path d="M-26 6 H26 L18 70 H-18 Z" fill="#FFE9B0"/><circle cx="0" cy="40" r="80" fill="#FFE9B0" opacity=".35" filter="url(#glow)"/></g>
<g id="doorg2" transform="translate(500 560)"><rect x="-230" y="-460" width="460" height="830" fill="#E9E2D0" stroke="#B9AE95" stroke-width="6"/>
<rect x="-200" y="-430" width="400" height="800" fill="url(#door2G)" filter="url(#woodgrain)"/>
<rect x="-150" y="-380" width="300" height="230" rx="8" fill="#C9D6DE"/><rect x="-150" y="-380" width="300" height="230" rx="8" fill="url(#glass2)" opacity=".6"/>
<g id="lady" opacity="0" filter="url(#dof)"><ellipse cx="20" cy="-290" rx="46" ry="54" fill="#3A2A2A"/><path d="M-70 -150 C-60 -220 100 -220 110 -150 Z" fill="#3A2A2A"/></g>
<path d="M-150 -380 H150 V-150 H-150 Z" fill="none" stroke="#3A1810" stroke-width="10"/>
<rect x="-150" y="-100" width="130" height="420" rx="8" fill="none" stroke="#3A1810" stroke-width="7"/><rect x="20" y="-100" width="130" height="420" rx="8" fill="none" stroke="#3A1810" stroke-width="7"/>
<circle cx="150" cy="40" r="20" fill="url(#brass)" filter="url(#shadow)"/></g>
<g id="knock2" opacity="0"><path d="M720 420 q34 34 0 68 M752 396 q56 58 0 116 M784 372 q78 82 0 164" stroke="#0B1220" stroke-width="9" fill="none" stroke-linecap="round"/></g>''') + """
<div id="quote" style="position:absolute; left:40px; right:40px; top:50px; padding:28px 32px; border-radius:26px; background:#0B1220; border:4px solid #F5B82E">
  <div style="font-weight:800; font-size:48px; line-height:1.15; color:#F4F1EA">“Taş benim evime düştü, benimdir.”</div>
  <div style="font-weight:600; font-size:30px; color:#F5B82E; margin-top:12px">Ev sahibi Birdie Guy</div>
</div>"""

scale_svg = f'''<g filter="url(#shadow)"><rect x="-14" y="-380" width="28" height="560" fill="url(#brassBar)"/><path d="M-160 180 H160 L130 230 H-130 Z" fill="url(#brassBar)"/><circle cy="-390" r="28" fill="url(#brass)"/>
<g id="beam2"><rect x="-350" y="-392" width="700" height="20" rx="10" fill="url(#brassBar)"/>
<g id="panL2" transform="translate(-330 -380)"><path d="M0 0 L-90 210 M0 0 L90 210" stroke="#B8862E" stroke-width="5"/><path d="M-130 210 H130 Q110 262 0 262 Q-110 262 -130 210 Z" fill="url(#brassBar)"/><g transform="translate(0 168)">{rock2(.85)}</g></g>
<g id="panR2" transform="translate(330 -380)"><path d="M0 0 L-90 210 M0 0 L90 210" stroke="#B8862E" stroke-width="5"/><path d="M-130 210 H130 Q110 262 0 262 Q-110 262 -130 210 Z" fill="url(#brassBar)"/>{''.join(f'<rect x="-74" y="{190-i*14}" width="148" height="22" rx="4" fill="#8DB37A" stroke="#3E5E30" stroke-width="3"/><circle cx="0" cy="{201-i*14}" r="6" fill="#5E8A4C"/>' for i in range(6))}<text x="0" y="100" text-anchor="middle" font-family="Mont" font-weight="800" font-size="50" fill="#9CC48A">$500</text></g></g></g>'''
court = svg(f'''<rect width="960" height="1080" fill="#3A2416"/>
<g filter="url(#dof)">{''.join(f'<rect x="{x}" y="0" width="150" height="760" fill="#5A3420" stroke="#2A160C" stroke-width="10"/><rect x="{x+20}" y="40" width="110" height="300" fill="#6A4028"/><rect x="{x+20}" y="380" width="110" height="300" fill="#6A4028"/>' for x in range(0, 960, 160))}
<rect x="180" y="420" width="600" height="300" fill="#4A2A18"/><circle cx="480" cy="160" r="80" fill="#C9A24A" opacity=".6"/></g>
<rect width="960" height="1080" fill="#000" opacity=".25"/>
<rect y="860" width="960" height="220" fill="#2A160C" filter="url(#woodgrain)"/>
<g transform="translate(480 620)">{scale_svg}</g>''') + mover("gavel2", gavel(.9), 260, 280) + """
<div id="cal" style="position:absolute; right:36px; top:36px; width:200px; border-radius:18px; overflow:hidden; text-align:center; background:#F4F1EA; color:#0B1220">
  <div style="background:#E8524A; color:#fff; font-weight:800; font-size:30px; padding:8px">DAVA</div><div style="font-weight:800; font-size:64px; padding:10px 0">1 YIL</div></div>"""

nobody = svg(f'''<rect width="960" height="1080" fill="url(#wallpaper)"/><rect width="960" height="1080" fill="#3A2A1E" opacity=".35"/>
<rect y="880" width="960" height="200" fill="#7A4A2A" filter="url(#woodgrain)"/><rect y="874" width="960" height="12" fill="#E9E2D0"/>
<g id="ndoor2" transform="translate(560 500)"><rect x="-250" y="-440" width="60" height="820" fill="#E9E2D0"/>
<polygon points="-190,-440 -60,-440 -60,380 -190,380" fill="#FFF3D0"/><polygon points="-190,-440 -60,-440 260,1000 -190,1000" fill="#FFF3D0" opacity=".22" filter="url(#dof)"/>
<path d="M-60 -440 L170 -400 L170 340 L-60 380 Z" fill="url(#door2G)" filter="url(#woodgrain)"/><path d="M-60 -440 L170 -400 L170 340 L-60 380 Z" fill="#000" opacity=".2"/><circle cx="140" cy="-20" r="18" fill="url(#brass)"/></g>
<g id="tag2" transform="translate(300 300) rotate(-10)" filter="url(#shadow)"><path d="M-170 -74 H134 L188 0 L134 74 H-170 Z" fill="#F5B82E" stroke="#7A5A10" stroke-width="5"/><circle cx="134" cy="0" r="12" fill="#7A5A10"/><text x="-20" y="18" text-anchor="middle" font-family="Mont" font-weight="800" font-size="54" fill="#0B1220">SATILIK</text><path id="nocross2" d="M-160 -62 L124 62" stroke="#E8524A" stroke-width="14" stroke-linecap="round" stroke-dasharray="320" stroke-dashoffset="320"/></g>
<g transform="translate(740 870)">{rock2(1.7)}</g>''') + """
<div class="chip red" id="stopchip" style="opacity:0">KAPI TUTUCU</div>"""

meg = svg(f'''<rect width="960" height="1080" fill="#04070C"/>
<circle cx="480" cy="600" r="380" fill="url(#fire2)" opacity=".16" filter="url(#glow)"/>
{''.join(f'<circle class="spark" cx="{(i*137)%960}" cy="{(i*89)%1080}" r="{1.5+(i%3)}" fill="#FFB347" opacity=".5"/>' for i in range(40))}
<g id="frag1b" transform="translate(470 640)">{rock2(2.6)}<path d="M40 -150 L10 -60 L50 10 L20 90" stroke="#FF9A3A" stroke-width="6" fill="none" filter="url(#glow)" id="crackglow" opacity="0"/></g>''') + \
    mover("frag2b", rock2(1.3) + '<circle r="90" fill="url(#fire2)" opacity=".4" filter="url(#glow)"/>', 220, 220, "opacity:0") + """
<div id="megtxt" class="big" style="top:130px; font-size:140px; color:#F5B82E; text-shadow:0 10px 0 #000">MEĞERSE</div>
<div id="megsub" class="big" style="top:310px; font-size:44px; color:#C9D6E4">2. PARÇA</div>"""

farm_bg = svg(f'''<rect width="960" height="1080" fill="url(#sky2)"/>{cloud(220, 160, 1)}{cloud(760, 220, .8, .8)}
<g filter="url(#dof)">{''.join(tree_autumn(x, 560, .7, x % 7) for x in range(-40, 1000, 150))}</g>
<rect y="540" width="960" height="60" fill="url(#hazeG)"/>
<path d="M0 580 H960 V1080 H0 Z" fill="#A89A6A" filter="url(#grainy)"/>
{''.join(f'<path d="M{480+(x-480)*0.08} 580 L{x} 1080" stroke="#6E7A3A" stroke-width="{8+abs(x-480)/40}" opacity=".55"/>' for x in range(-400, 1400, 110) if abs(x-480) > 160)}
{''.join(f'<circle cx="{(i*73)%960}" cy="{620+(i*41)%440}" r="{3+(i%4)}" fill="#F4F0E6" opacity=".85"/>' for i in range(90) if abs(((i*73)%960)-480) > 150 + ((620+(i*41)%440)-580)*.6)}
<path d="M450 580 L510 580 L760 1080 L200 1080 Z" fill="#B49A70" filter="url(#grainy)"/><path d="M480 580 V1080" stroke="#8A7550" stroke-width="5" stroke-dasharray="30 30" opacity=".6"/>
{''.join(f'<rect x="{480+(i*28+70)}" y="{600+i*44}" width="{6+i*1.5}" height="{40+i*12}" fill="#5A4030"/>' for i in range(0, 11))}
<path d="M550 610 L860 1060" stroke="#7A6050" stroke-width="3"/>
<g id="farmrock2" transform="translate(540 870)">{rock2(1.1)}</g>
<g id="newhouse2" transform="translate(760 520) scale(0)">{house2(0, 0, .35, "nh2")}</g>
<g id="bills2" opacity="0">{''.join(f'<g class="bill2" transform="translate({360+(i*61)%260} {220+(i*37)%160}) rotate({(i*29)%60-30})"><rect x="-44" y="-20" width="88" height="40" rx="5" fill="#8DB37A" stroke="#3E5E30" stroke-width="3"/><circle r="10" fill="#5E8A4C"/></g>' for i in range(10))}</g>''')
farmer = farm_bg + mover("farmerman2", farmer2(1.25), 220, 340) + mover("car2", car50s(.85), 460, 200) + f"""
<div class="chip" style="bottom:36px">ÇİFTÇİ JULIUS McKINNEY</div>
<div class="fill" id="mckwrap" style="background:#0B1220"><div class="fill" id="mckkb"><img src="{REAL['mckinney']}" alt="" style="object-position:62% 78%; filter:contrast(1.1)"></div><div class="vign"></div><div class="chip top">McKINNEY AİLESİ VE 2. PARÇA · 1954</div></div>"""

end_right = svg(f'''<rect width="480" height="1080" fill="url(#sky2)"/>{cloud(240, 200, .7)}
<rect y="700" width="480" height="380" fill="url(#grass2)" filter="url(#grainy)"/>
<g transform="translate(250 620)">{house2(0, 0, .5, "eh2")}</g><g transform="translate(240 900)">{car50s(.7)}</g>''', 480, 1080, "", "position:absolute; left:480px; top:0; width:480px; height:1080px")
end = f"""<div style="position:absolute; left:0; top:0; width:480px; height:1080px; overflow:hidden"><img src="{REAL['museum']}" style="width:100%; height:100%; object-fit:cover; object-position:44% 30%"></div>
{end_right}
<div style="position:absolute; left:476px; top:0; width:8px; height:1080px; background:#F4F1EA"></div>
<div class="endlab" style="left:24px">ANN<br><span>taş müzede, para yok</span></div>
<div class="endlab" style="left:504px">McKINNEY<br><span>ev + araba</span></div>"""

HTML = {"hook": hook, "town": town, "room": room, "bruise": bruise, "panic": panic, "police": police, "door": door,
        "court": court, "nobody": nobody, "meg": meg, "farmer": farmer, "end": end, "sources": sources}
scenes_html = "".join(scene(k, HTML[k]) for k in keys)

s = lambda k: S[k][0]
d = lambda k: win(k)[1]
P = lambda cx, cy, w, h: f"x:{cx - w/2},y:{cy - h/2}"   # merkez -> sol-üst
js = "".join(f'tl.fromTo("#{k}-in",{{opacity:0}},{{opacity:1,duration:{FADE},ease:"power1.out"}},{s(k)});' for k in keys if k != "hook")
js += f"""
tl.fromTo("#hookkb",{{scale:1.9,transformOrigin:"42% 62%"}},{{scale:1.02,duration:{d('hook')},ease:"power2.inOut"}},0);
tl.fromTo("#thouse",{{scale:1,transformOrigin:"28% 52%"}},{{scale:1.55,duration:{d('town')},ease:"power1.inOut"}},{s('town')});
tl.fromTo("#tfence",{{y:0}},{{y:120,duration:{d('town')},ease:"power1.inOut"}},{s('town')});
tl.fromTo("#tclouds",{{x:0}},{{x:-60,duration:{d('town')},ease:"none"}},{s('town')});
tl.fromTo("#datecard",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.7)"}},{s('town')+.3});
tl.fromTo("#roomcam2",{{scale:1.12,transformOrigin:"45% 60%"}},{{scale:1,duration:2.2,ease:"power2.out"}},{s('room')});
tl.fromTo("#minhand2",{{rotation:180,transformOrigin:"50% 92%"}},{{rotation:270,duration:2,ease:"power1.out"}},{s('room')});
tl.fromTo("#winball2",{{attr:{{transform:"translate(80 -120) scale(.18)"}}}},{{attr:{{transform:"translate(-70 70) scale(.22)"}},duration:{hit-s('room')},ease:"power1.in"}},{s('room')});
tl.set("#rock2",{{opacity:1}},{hit+.15});
tl.fromTo("#rock2",{{{P(520,-120,160,160)},rotation:0}},{{{P(520,150,160,160)},rotation:40,duration:.4,ease:"power2.in"}},{hit+.15});
tl.to("#hole2",{{opacity:1,duration:.05}},{hit+.55});
tl.set("#burst2",{{opacity:1}},{hit+.55});tl.to("#burst2",{{opacity:0,duration:.7}},{hit+.6});
tl.set("#dust2",{{opacity:.95,scale:.6,transformOrigin:"50% 20%"}},{hit+.55});tl.to("#dust2",{{opacity:0,scale:1.6,duration:2.4,ease:"power2.out"}},{hit+.6});
tl.fromTo("#roomcam2",{{x:-12}},{{x:12,duration:.05,repeat:9,yoyo:true}},{hit+.55});
tl.to("#rock2",{{{P(740,600,160,160)},rotation:200,duration:{radio-hit-.55},ease:"power1.in"}},{hit+.55});
tl.to("#radiocrack2",{{opacity:1,duration:.05}},{radio});
tl.to("#rock2",{{{P(470,690,160,160)},rotation:320,duration:{hip-radio},ease:"power2.out"}},{radio});
tl.set("#burst3",{{opacity:1}},{hip});tl.to("#burst3",{{opacity:0,duration:.6}},{hip+.05});
tl.to("#hipmark2",{{attr:{{r:60}},duration:.6}},{hip});
tl.to("#traj2",{{opacity:.85,duration:.3}},{hip+.3});
tl.fromTo("#kg2",{{opacity:0,y:-20}},{{opacity:1,y:0,duration:.4}},{hit+.7});
tl.fromTo("#stamp",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"power3.in"}},{A('kayıtlara')});
tl.fromTo("#bruisekb",{{scale:1.05,transformOrigin:"64% 66%"}},{{scale:1.5,duration:{alive-s('bruise')},ease:"power1.inOut"}},{s('bruise')});
tl.to("#bedwrap",{{opacity:1,duration:.5}},{alive-.2});
tl.fromTo("#bedkb",{{scale:1.15}},{{scale:1.0,duration:{S['bruise'][1]-alive+.5},ease:"power1.out"}},{alive-.2});
tl.fromTo("#crowd2 > g",{{y:220,opacity:0}},{{y:0,opacity:1,duration:.55,stagger:.07,ease:"back.out(1.5)"}},{s('panic')+.2});
tl.fromTo("#q1",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('uçak')});
tl.fromTo("#q2",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{A('Sovyet')});
tl.fromTo("#policekb",{{scale:1.0,transformOrigin:"60% 25%"}},{{scale:1.25,duration:{d('police')},ease:"power1.inOut"}},{s('police')});
tl.fromTo("#afstamp",{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:.3,ease:"power3.in"}},{A('Hava')});
tl.fromTo("#doorg2",{{scale:1.12,transformOrigin:"50% 40%"}},{{scale:1,duration:{d('door')},ease:"power1.out"}},{s('door')});
tl.to("#lady",{{opacity:.85,duration:.6}},{s('door')+.2});
tl.to("#knock2",{{opacity:1,duration:.06,repeat:5,yoyo:true}},{s('door')+.4});
tl.fromTo("#quote",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"back.out(1.6)"}},{A('Taş benim')});
tl.fromTo("#gavel2",{{{P(760,180,260,280)},rotation:-70,transformOrigin:"50% 85%"}},{{{P(760,330,260,280)},rotation:10,duration:.32,ease:"power4.in"}},{A('beş')-.35});
tl.to("#gavel2",{{rotation:0,duration:.25,ease:"back.out(3)"}},{A('beş')-.03});
tl.fromTo("#beam2",{{rotation:0,transformOrigin:"50% 50%"}},{{rotation:-9,duration:1.2,ease:"elastic.out(1,.5)"}},{A('beş')});
tl.fromTo("#panL2",{{rotation:0}},{{rotation:9,duration:1.2,ease:"elastic.out(1,.5)"}},{A('beş')});
tl.fromTo("#panR2",{{rotation:0}},{{rotation:9,duration:1.2,ease:"elastic.out(1,.5)"}},{A('beş')});
tl.fromTo("#cal",{{rotationX:90,opacity:0}},{{rotationX:0,opacity:1,duration:.5}},{s('court')+.2});
tl.to("#nocross2",{{attr:{{"stroke-dashoffset":0}},duration:.4}},{A('Alıcı')});
tl.to("#tag2",{{y:-420,opacity:0,duration:.6,ease:"power2.in"}},{stopper-.6});
tl.to("#stopchip",{{opacity:1,duration:.3}},{stopper});
tl.fromTo("#ndoor2",{{scale:1,transformOrigin:"80% 90%"}},{{scale:1.22,duration:{d('nobody')},ease:"power1.inOut"}},{s('nobody')});
tl.fromTo("#megtxt",{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{s('meg')+.05});
tl.fromTo(".spark",{{y:0}},{{y:-160,duration:{d('meg')},ease:"none"}},{s('meg')});
tl.to("#crackglow",{{opacity:1,duration:.3}},{s('meg')+.7});
tl.set("#frag2b",{{opacity:1}},{s('meg')+.95});
tl.fromTo("#frag2b",{{{P(500,600,220,220)},rotation:0}},{{{P(760,700,220,220)},rotation:160,duration:.55,ease:"power3.out"}},{s('meg')+.95});
tl.to("#frag1b",{{attr:{{transform:"translate(380 640)"}},duration:.55,ease:"power3.out"}},{s('meg')+.95});
tl.fromTo("#megsub",{{opacity:0}},{{opacity:1,duration:.4}},{s('meg')+1.4});
tl.fromTo("#mckkb",{{scale:1.12,transformOrigin:"62% 85%"}},{{scale:1.0,duration:{road-s('farmer')+.6},ease:"power1.out"}},{s('farmer')});
tl.to("#mckwrap",{{opacity:0,duration:.5}},{road+.5});
tl.fromTo("#farmerman2",{{{P(150,880,220,340)}}},{{{P(290,860,220,340)},duration:1.6,ease:"power1.out"}},{road+.5});
tl.to("#farmrock2",{{attr:{{transform:"translate(540 780) scale(1.1)"}},duration:.5,ease:"back.out(2)"}},{road+2.2});
tl.to("#bills2",{{opacity:1,duration:.3}},{house_car-.6});
tl.fromTo(".bill2",{{y:-300,opacity:0}},{{y:0,opacity:1,duration:.8,stagger:.05,ease:"bounce.out"}},{house_car-.6});
tl.to("#newhouse2",{{attr:{{transform:"translate(760 520) scale(1)"}},duration:.5,ease:"back.out(1.8)"}},{house_car});
tl.fromTo("#car2",{{{P(-300,960,460,200)}}},{{{P(640,960,460,200)},duration:.7,ease:"power3.out"}},{A('araba')});
tl.fromTo(".endlab",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.4,stagger:.5}},{s('end')+.2});
"""

css = """
.qb { position:absolute; padding:22px 30px; border-radius:26px; background:#F4F1EA; color:#0B1220; font-weight:800; font-size:44px; box-shadow:0 8px 0 rgba(0,0,0,.35); }
.endlab { position:absolute; top:40px; width:430px; padding:18px 22px; border-radius:20px; background:rgba(11,18,32,.88); border:3px solid #F4F1EA; font-weight:800; font-size:46px; line-height:1.1; }
.endlab span { font-weight:600; font-size:32px; color:#F5B82E; }
"""
html = page(words, mouth, scenes_html, js, total=TOTAL, voice_end=VOICE_END, kicker="MEĞERSE DOSYASI <b>|</b> VAKA 04 · GÖKTAŞI",
            title="UZAYDAN GELEN TAŞ", voice_src="assets/hodges/voice.mp3", extra_css=css, glow="#3A2414", fx=True, defs=DEFS2)
(HF / "index.html").write_text(html, encoding="utf-8")
print("hf/index.html yazıldı; süre", TOTAL, "sn; sahneler:", {k: round(v[0], 2) for k, v in S.items()})
