"""Okene reel'inin HyperFrames kompozisyonunu üretir: hf/index.html.

Kullanım: python3 reels/okene/build.py && (cd hf && npm run check && npm run render)
Girdiler: reels/okene/words.json (kelime zamanları), hf/avatar/osman.svg, hf/avatar/mouth-okene.json (30 fps ağız seviyesi 0-3).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HF = ROOT / "hf"
words = json.loads((ROOT / "reels/okene/words.json").read_text(encoding="utf-8"))
mouth = json.loads((HF / "avatar/mouth-okene.json").read_text())
svg = (HF / "avatar/osman.svg").read_text(encoding="utf-8").replace("<svg ", '<svg id="av" data-m="0" data-b="0" ', 1)

VOICE_END = 70.0
TOTAL = 74.0
FADE = 0.45

# Sahneler: (id, başlangıç, bitiş). Ardışık sahneler FADE kadar örtüşür.
S = {
    "hook": (0.0, 5.6),
    "tug": (5.6, 14.6),
    "sink": (14.6, 20.2),
    "pocket": (20.2, 24.6),
    "photo": (24.6, 34.9),
    "clock": (34.9, 39.5),
    "light": (39.5, 45.2),
    "hand": (45.2, 51.5),
    "face": (51.5, 54.6),
    "portrait": (54.6, 62.5),
    "diver": (62.5, VOICE_END),
    "sources": (VOICE_END, TOTAL),
}


def win(k):
    a, b = S[k]
    return a, (b + FADE if b < TOTAL else b) - a


# --- altyazı parçaları: noktalamada ya da 4 kelimede böl
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= 4 or w["text"][-1] in ".,…?!":
        chunks.append(cur)
        cur = []
if cur:
    chunks.append(cur)

cap_html, cap_js = [], []
for ci, ch in enumerate(chunks):
    a = ch[0]["startMs"] / 1000
    b = chunks[ci + 1][0]["startMs"] / 1000 if ci + 1 < len(chunks) else ch[-1]["endMs"] / 1000 + 0.4
    spans = "".join(f'<span id="w{ci}_{wi}">{w["text"]}</span> ' for wi, w in enumerate(ch))
    cap_html.append(f'<div class="cap" id="c{ci}"><div>{spans.strip()}</div></div>')
    cap_js.append(f'tl.set("#c{ci}",{{opacity:1}},{a:.2f});tl.set("#c{ci}",{{opacity:0}},{b:.2f});')
    for wi, w in enumerate(ch):
        cap_js.append(f'tl.set("#w{ci}_{wi}",{{color:"#F5B82E"}},{w["startMs"]/1000:.2f});')

# --- ağız: yalnızca değiştiği karelerde
mouth_js, prev = [], None
for i, ch in enumerate(mouth):
    if ch != prev:
        mouth_js.append(f"[{i/30:.3f},{ch}]")
        prev = ch
blinks = [t + 0.05 for t in range(2, int(VOICE_END), 4)]

html = f"""<!doctype html>
<html lang="tr" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-800-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }}
@font-face {{ font-family: "Mont"; font-weight: 800; src: url(assets/fonts/montserrat-latin-ext-800-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }}
@font-face {{ font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-600-normal.woff2) format("woff2"); unicode-range: U+0000-00FF; }}
@font-face {{ font-family: "Mont"; font-weight: 600; src: url(assets/fonts/montserrat-latin-ext-600-normal.woff2) format("woff2"); unicode-range: U+0100-024F; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0B1220; }}
#root {{ position: relative; width: 100%; height: 100%; font-family: "Mont", sans-serif; color: #F4F1EA;
  background: radial-gradient(120% 70% at 50% 0%, #17304A 0%, #0B1220 60%); }}
.grid {{ position: absolute; inset: 0; opacity: .07;
  background-image: linear-gradient(#9FC3E6 1px, transparent 1px), linear-gradient(90deg, #9FC3E6 1px, transparent 1px); background-size: 54px 54px; }}
#kicker {{ position: absolute; left: 60px; top: 92px; font-weight: 600; font-size: 30px; letter-spacing: .14em; color: #9FB4CC; }}
#kicker b {{ color: #E8524A; font-weight: 800; }}
#title {{ position: absolute; left: 60px; top: 150px; padding: 16px 28px; background: #F4F1EA; color: #0B1220; border-radius: 18px;
  font-weight: 800; font-size: 46px; box-shadow: 0 8px 0 #E8524A; }}
#panel {{ position: absolute; left: 60px; top: 270px; width: 960px; height: 1080px; border-radius: 36px; overflow: hidden;
  border: 8px solid #F4F1EA; background: #06101C; }}
.scene {{ position: absolute; inset: 0; }}
.fill {{ position: absolute; inset: 0; }}
.fill img, .fill video {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.vign {{ position: absolute; inset: 0; background: radial-gradient(70% 60% at 50% 45%, transparent 40%, rgba(0,0,0,.75) 100%); }}
.chip {{ position: absolute; left: 36px; bottom: 36px; padding: 12px 22px; border-radius: 14px; background: rgba(6,16,28,.82);
  border: 3px solid #F4F1EA; font-weight: 800; font-size: 34px; letter-spacing: .02em; }}
.chip.red {{ background: #E8524A; border-color: #E8524A; color: #fff; }}
#avatarbox {{ position: absolute; left: 44px; top: 1420px; width: 330px; height: 330px; }}
#avatarbox svg {{ width: 100%; height: 100%; display: block; }}
#av #mouth-0, #av #mouth-1, #av #mouth-2, #av #mouth-3, #av #eyes-closed {{ display: none; }}
#av[data-m="0"] #mouth-0, #av[data-m="1"] #mouth-1, #av[data-m="2"] #mouth-2, #av[data-m="3"] #mouth-3 {{ display: inline; }}
#av[data-b="1"] #eyes-open {{ display: none; }}
#av[data-b="1"] #eyes-closed {{ display: inline; }}
#bubble {{ position: absolute; left: 400px; top: 1452px; width: 636px; height: 266px; border-radius: 30px; background: #111A28;
  border: 6px solid #F4F1EA; }}
#bubble::before {{ content: ""; position: absolute; left: -30px; top: 104px; border: 22px solid transparent; border-right: 30px solid #F4F1EA; border-left: 0; }}
.cap {{ position: absolute; inset: 0; padding: 30px 36px; display: flex; align-items: center; font-weight: 800; font-size: 54px;
  line-height: 1.15; opacity: 0; color: #F4F1EA; }}
#handle {{ position: absolute; right: 60px; top: 1790px; font-weight: 600; font-size: 30px; color: #6F86A0; letter-spacing: .06em; }}
/* vektör sahneleri */
.sea {{ background: linear-gradient(#1E5D84 0%, #0E3552 35%, #071B2C 75%, #030B14 100%); }}
.ray {{ position: absolute; top: -10%; width: 120px; height: 120%; background: linear-gradient(rgba(170,220,255,.18), transparent 70%);
  transform-origin: top center; }}
.gauge {{ position: absolute; right: 40px; top: 60px; width: 210px; padding: 18px; border-radius: 22px; background: rgba(4,12,22,.8);
  border: 3px solid #9FC3E6; text-align: center; }}
.gauge .n {{ font-weight: 800; font-size: 92px; line-height: 1; color: #fff; }}
.gauge .u {{ font-weight: 600; font-size: 26px; color: #9FC3E6; letter-spacing: .12em; }}
.big {{ position: absolute; left: 0; right: 0; text-align: center; font-weight: 800; }}
#meg {{ position: absolute; left: 0; right: 0; top: 420px; text-align: center; font-weight: 800; font-size: 150px; color: #F5B82E;
  letter-spacing: .02em; text-shadow: 0 10px 0 #000; }}
.src {{ font-weight: 600; font-size: 34px; line-height: 1.5; color: #C9D6E4; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
  <div class="grid"></div>
  <div id="kicker">MEĞERSE DOSYASI <b>|</b> VAKA 03 · OKYANUS</div>
  <div id="title">OKYANUSUN DİBİNDE 60 SAAT</div>

  <audio id="vo" src="assets/okene/voice.mp3" data-start="0" data-duration="{VOICE_END}" data-track-index="9" data-volume="1"></audio>

  <div id="panel">
    <!-- 1 kanca: gerçek dalgıç kamerası, yüz beliriyor -->
    <div class="scene" id="s-hook">
      <div class="fill" id="hook-in"><div class="fill" id="hook-kb"><video id="v-hook" class="clip" style="object-position: 18% 50%" src="assets/okene/dalgic-kamera.m4v" muted playsinline
        data-start="{win('hook')[0]}" data-duration="{win('hook')[1]}" data-media-start="31.8" data-track-index="2"></video></div></div>
      <div class="fill clip" data-start="{win('hook')[0]}" data-duration="{win('hook')[1]}" data-track-index="3"><div class="vign"></div><div class="chip red">30 METRE · ZİFİRİ KARANLIK</div></div>
    </div>

    <!-- 2 römorkör + fırtına -->
    <div class="scene clip" id="s-tug" data-start="{win('tug')[0]}" data-duration="{win('tug')[1]}" data-track-index="1">
      <div class="fill" id="tug-in">
        <div class="fill" id="tug-kb"><img src="assets/okene/jascon-romorkor.webp" alt="" style="object-position: 38% 50%"></div>
        <div class="fill" id="storm" style="background: linear-gradient(rgba(8,18,34,.55), rgba(8,18,34,.25))"></div>
        <svg class="fill" id="rain" viewBox="0 0 960 1080" preserveAspectRatio="none">{''.join(f'<line x1="{(i*73)%960}" y1="{(i*131)%1080}" x2="{(i*73)%960-18}" y2="{(i*131)%1080+70}" stroke="#CFE3F5" stroke-width="2.5" opacity=".45"/>' for i in range(70))}</svg>
        <div class="fill" id="flash" style="background:#EAF4FF; opacity:0"></div>
        <div class="vign"></div>
        <div class="chip">26 MAYIS 2013 · NİJERYA AÇIKLARI</div>
      </div>
    </div>

    <!-- 3 vektör: gemi ters dönüp batıyor -->
    <div class="scene clip sea" id="s-sink" data-start="{win('sink')[0]}" data-duration="{win('sink')[1]}" data-track-index="1">
      <div class="fill" id="sink-in">
        <div class="ray" style="left:120px; transform: rotate(14deg)"></div><div class="ray" style="left:420px; transform: rotate(-6deg)"></div><div class="ray" style="left:700px; transform: rotate(10deg)"></div>
        <svg class="fill" viewBox="0 0 960 1080">
          <defs>
            <linearGradient id="hull" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E2453C"/><stop offset="1" stop-color="#8E1F1A"/></linearGradient>
            <linearGradient id="cab" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F4F4F0"/><stop offset="1" stop-color="#B9C2CB"/></linearGradient>
          </defs>
          <path d="M0 70 Q60 52 120 70 T240 70 T360 70 T480 70 T600 70 T720 70 T840 70 T960 70 V0 H0 Z" fill="#2E7DA8" opacity=".9"/>
          <path d="M0 1020 Q160 990 320 1012 T640 1004 T960 1016 V1080 H0 Z" fill="#1A1410"/>
          <g id="ship" transform="translate(480 230)">
            <g>
              <path d="M-230 20 L230 20 L200 95 Q190 110 170 110 L-185 110 Q-215 110 -225 85 Z" fill="url(#hull)" stroke="#1B0F0E" stroke-width="5"/>
              <path d="M-230 20 L230 20 L226 34 L-226 34 Z" fill="#F2F2EE"/>
              {''.join(f'<circle cx="{x}" cy="62" r="13" fill="#1E1E1E" stroke="#555" stroke-width="3"/>' for x in range(-190, 200, 48))}
              <path d="M-90 20 L-90 -70 L60 -70 L80 -40 L80 20 Z" fill="url(#cab)" stroke="#1B2530" stroke-width="5"/>
              <path d="M-60 -110 L40 -110 L52 -70 L-72 -70 Z" fill="url(#cab)" stroke="#1B2530" stroke-width="5"/>
              {''.join(f'<rect x="{x}" y="-100" width="22" height="18" rx="3" fill="#2B4B66"/>' for x in range(-52, 40, 30))}
              {''.join(f'<rect x="{x}" y="-52" width="26" height="20" rx="3" fill="#2B4B66"/>' for x in range(-74, 70, 34))}
              <path d="M-10 -110 L-10 -175 M-30 -150 L10 -150" stroke="#1B2530" stroke-width="6" stroke-linecap="round"/>
              <rect x="100" y="0" width="110" height="20" fill="#C9CED3" stroke="#1B2530" stroke-width="4"/>
            </g>
          </g>
          {''.join(f'<circle cx="{120+ (i*97)%760}" cy="{900-(i*53)%600}" r="{4+i%5}" fill="none" stroke="#BFE3FF" stroke-width="2" opacity=".5" class="bub"/>' for i in range(16))}
        </svg>
        <div class="gauge"><div class="n" id="depth">0</div><div class="u">METRE</div></div>
        <div class="chip">İÇERİDE 12 KİŞİ</div>
      </div>
    </div>

    <!-- 4 vektör: ters geminin kesiti, hava cebi -->
    <div class="scene clip sea" id="s-pocket" data-start="{win('pocket')[0]}" data-duration="{win('pocket')[1]}" data-track-index="1">
      <div class="fill" id="pocket-in">
        <svg class="fill" viewBox="0 0 960 1080">
          <defs>
            <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFE6A6" stop-opacity=".9"/><stop offset="1" stop-color="#FFE6A6" stop-opacity="0"/></radialGradient>
            <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D6A93"/><stop offset="1" stop-color="#0A2840"/></linearGradient>
          </defs>
          <path d="M150 300 L810 300 L840 900 Q842 950 790 950 L170 950 Q118 950 120 900 Z" fill="url(#water)" stroke="#E2453C" stroke-width="14" stroke-linejoin="round"/>
          <path d="M150 300 L810 300" stroke="#8E1F1A" stroke-width="26"/>
          <path d="M136 520 L824 520 M130 730 L830 730 M480 300 L480 950 M300 520 L300 950 M660 520 L660 950" stroke="#33495F" stroke-width="12"/>
          <rect x="314" y="530" width="152" height="46" fill="#0A0F16"/>
          <path d="M314 576 Q352 570 390 576 T466 576" stroke="#9FD8FF" stroke-width="4" fill="none"/>
          <circle id="pocketGlow" cx="390" cy="556" r="110" fill="url(#glow)" opacity="0"/>
          <circle cx="390" cy="566" r="16" fill="#3B2A22"/>
          {''.join(f'<circle cx="{180+(i*83)%600}" cy="{620+(i*47)%300}" r="{3+i%4}" fill="none" stroke="#BFE3FF" stroke-width="2" opacity=".35"/>' for i in range(14))}
          <text x="480" y="210" text-anchor="middle" font-family="Mont" font-weight="800" font-size="40" fill="#9FC3E6" letter-spacing="4">GEMİ TERS · 30 METRE DİPTE</text>
          <text x="480" y="262" text-anchor="middle" font-family="Mont" font-weight="600" font-size="30" fill="#6F86A0" letter-spacing="3">KESİT</text>
          <path d="M466 548 L600 420" stroke="#F5B82E" stroke-width="5"/><circle cx="466" cy="548" r="9" fill="#F5B82E"/>
          <rect x="560" y="370" width="300" height="60" rx="12" fill="#0B1220" stroke="#F5B82E" stroke-width="3"/>
          <text x="710" y="412" text-anchor="middle" font-family="Mont" font-weight="800" font-size="34" fill="#F5B82E">~1,2 m HAVA</text>
        </svg>
        <div class="chip">MÜHENDİS KAMARASI</div>
      </div>
    </div>

    <!-- 5 gerçek fotoğraf: hava cebinde -->
    <div class="scene clip" id="s-photo" data-start="{win('photo')[0]}" data-duration="{win('photo')[1]}" data-track-index="1">
      <div class="fill" id="photo-in">
        <div class="fill" id="photo-kb"><img src="assets/okene/hava-cebi-kamera.jpg" alt="" style="object-position: 22% 50%"></div>
        <div class="fill" id="photo-dark" style="background:#000; opacity:.55"></div>
        <div class="vign"></div>
        <div class="chip">SU GÖĞSÜNE KADAR</div>
      </div>
    </div>

    <!-- 6 vektör: 60 saat sayacı, hava azalıyor -->
    <div class="scene clip" id="s-clock" data-start="{win('clock')[0]}" data-duration="{win('clock')[1]}" data-track-index="1" style="background:#05090F">
      <div class="fill" id="clock-in">
        <div class="big" style="top:250px; font-size:52px; color:#9FB4CC; letter-spacing:.2em">GEÇEN SÜRE</div>
        <div class="big" id="hours" style="top:330px; font-size:300px; line-height:1; color:#fff">0</div>
        <div class="big" style="top:640px; font-size:64px; color:#F5B82E">SAAT</div>
        <div style="position:absolute; left:120px; top:800px; width:720px; height:46px; border-radius:23px; border:4px solid #9FC3E6; overflow:hidden">
          <div id="air" style="width:100%; height:100%; background:linear-gradient(90deg,#E8524A,#F5B82E 40%,#5BC0EB); transform-origin:left center"></div>
        </div>
        <div class="big" style="top:870px; font-size:34px; color:#9FB4CC; letter-spacing:.14em">HAVA</div>
        <div class="fill" id="clock-dark" style="background:radial-gradient(60% 50% at 50% 45%, transparent 30%, #000 100%); opacity:0"></div>
      </div>
    </div>

    <!-- 7 gerçek video: fener ışığı -->
    <div class="scene" id="s-light">
      <div class="fill" id="light-in"><div class="fill" id="light-kb"><video id="v-light" class="clip" src="assets/okene/dalgic-kamera.m4v" muted playsinline
        data-start="{win('light')[0]}" data-duration="{win('light')[1]}" data-media-start="5.6" data-track-index="2"></video></div>
        <div class="fill clip" data-start="{win('light')[0]}" data-duration="{win('light')[1]}" data-track-index="3"><div class="vign"></div><div class="chip">DALGIÇ KAMERASI · GERÇEK GÖRÜNTÜ</div></div></div>
    </div>

    <!-- 8 gerçek video: el, yavaşlatılmış -->
    <div class="scene" id="s-hand">
      <div class="fill" id="hand-in"><div class="fill" id="hand-kb"><video id="v-hand" class="clip" src="assets/okene/dalgic-kamera.m4v" muted playsinline
        data-start="{win('hand')[0]}" data-duration="{win('hand')[1]}" data-media-start="11.6" data-playback-rate="0.8" data-track-index="2"></video></div>
        <div class="fill clip" data-start="{win('hand')[0]}" data-duration="{win('hand')[1]}" data-track-index="3"><div class="vign"></div></div></div>
    </div>

    <!-- 9 meğerse: yüz beliriyor -->
    <div class="scene" id="s-face">
      <div class="fill" id="face-in"><div class="fill" id="face-kb"><video id="v-face" class="clip" style="object-position: 18% 50%" src="assets/okene/dalgic-kamera.m4v" muted playsinline
        data-start="{win('face')[0]}" data-duration="{win('face')[1]}" data-media-start="31.6" data-track-index="2"></video></div>
        <div class="fill clip" data-start="{win('face')[0]}" data-duration="{win('face')[1]}" data-track-index="3"><div class="fill" id="face-flash" style="background:#fff; opacity:0"></div>
        <div id="meg">MEĞERSE</div></div></div>
    </div>

    <!-- 10 portre -->
    <div class="scene clip" id="s-portrait" data-start="{win('portrait')[0]}" data-duration="{win('portrait')[1]}" data-track-index="1">
      <div class="fill" id="portrait-in"><div class="fill" id="portrait-kb"><img src="assets/okene/okene-portre.jpg" alt=""></div>
        <div class="vign"></div>
        <div class="chip red" id="survivor">12 KİŞİDEN TEK SAĞ KALAN</div></div>
    </div>

    <!-- 11 dalgıç Okene -->
    <div class="scene clip" id="s-diver" data-start="{win('diver')[0]}" data-duration="{win('diver')[1]}" data-track-index="1">
      <div class="fill" id="diver-in"><div class="fill" id="diver-kb"><img src="assets/okene/gorsel-4.avif" alt="" style="object-position: 50% 30%"></div>
        <div class="vign"></div>
        <div class="chip">BUGÜN: TİCARİ DALGIÇ</div></div>
    </div>

    <!-- 12 kaynakça -->
    <div class="scene clip" id="s-sources" data-start="{win('sources')[0]}" data-duration="{win('sources')[1]}" data-track-index="1" style="background:#0B1220">
      <div class="fill" id="sources-in" style="padding:90px 70px">
        <div style="font-weight:800; font-size:56px; color:#F5B82E; margin-bottom:40px">KAYNAKLAR</div>
        <div class="src">ABC News (Haziran ve Aralık 2013)<br>ITV News (2 Aralık 2013)<br>Netwerk24 (8 Temmuz 2015)<br>Soundings Online<br><br>Görüntü: DCN Diving / The Telegraph</div>
      </div>
    </div>
  </div>

  <div id="avatarbox">{svg}</div>
  <div id="bubble">{''.join(cap_html)}</div>
  <div id="handle">@megerse.tr</div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const F = {FADE};
// sahne girişleri: iç katmanı yumuşak aç
{''.join(f'tl.fromTo("#{k}-in",{{opacity:0}},{{opacity:1,duration:F,ease:"power1.out"}},{S[k][0]});' for k in S if k != "hook")}
tl.fromTo("#hook-in",{{opacity:0}},{{opacity:1,duration:.3}},0);

// kanca: yavaş itiş
tl.fromTo("#hook-kb",{{scale:1.25}},{{scale:1.05,duration:{win('hook')[1]},ease:"none"}},0);
// römorkör: Ken Burns + yağmur + şimşek
tl.fromTo("#tug-kb",{{scale:1.08,x:30}},{{scale:1.28,x:-40,duration:{win('tug')[1]},ease:"none"}},{S['tug'][0]});
tl.fromTo("#rain",{{y:-120}},{{y:120,duration:.5,ease:"none",repeat:{int(win('tug')[1]/.5)}}},{S['tug'][0]});
tl.to("#flash",{{opacity:.85,duration:.06}},{S['tug'][0]+3.2}).to("#flash",{{opacity:0,duration:.35}});
tl.to("#flash",{{opacity:.6,duration:.05}},{S['tug'][0]+6.4}).to("#flash",{{opacity:0,duration:.3}});
// batış: dönüp dibe iner, derinlik sayacı
tl.fromTo("#ship",{{attr:{{transform:"translate(480 230) rotate(0)"}}}},{{attr:{{transform:"translate(480 300) rotate(178)"}},duration:1.6,ease:"power2.inOut"}},{S['sink'][0]+.2});
tl.to("#ship",{{attr:{{transform:"translate(480 900) rotate(180)"}},duration:3.4,ease:"power1.in"}},{S['sink'][0]+1.8});
const depth = {{v:0}};
tl.to(depth,{{v:30,duration:3.6,ease:"power1.in",onUpdate:()=>{{document.getElementById("depth").textContent=Math.round(depth.v)}}}},{S['sink'][0]+1.8});
tl.fromTo(".bub",{{y:0,opacity:.6}},{{y:-260,opacity:0,duration:2.4,stagger:.12,ease:"power1.out"}},{S['sink'][0]+.6});
// kesit: hava cebi parlıyor
tl.fromTo("#pocket-in svg",{{scale:1}},{{scale:1.35,transformOrigin:"40% 52%",duration:{win('pocket')[1]},ease:"power1.inOut"}},{S['pocket'][0]});
tl.to("#pocketGlow",{{opacity:1,duration:.8,yoyo:true,repeat:3}},{S['pocket'][0]+.6});
// hava cebi fotoğrafı: yavaş yakınlaşma, karanlıktan aydınlığa, su titremesi
tl.fromTo("#photo-kb",{{scale:1.05}},{{scale:1.35,duration:{win('photo')[1]},ease:"none"}},{S['photo'][0]});
tl.fromTo("#photo-dark",{{opacity:.75}},{{opacity:.25,duration:3}},{S['photo'][0]});
tl.to("#photo-kb",{{y:6,duration:.9,yoyo:true,repeat:{int(win('photo')[1]/.9)},ease:"sine.inOut"}},{S['photo'][0]});
// saat sayacı
const hrs = {{v:0}};
tl.to(hrs,{{v:60,duration:3.6,ease:"power2.in",onUpdate:()=>{{document.getElementById("hours").textContent=Math.round(hrs.v)}}}},{S['clock'][0]+.3});
tl.fromTo("#air",{{scaleX:1}},{{scaleX:.04,duration:3.8,ease:"power1.in"}},{S['clock'][0]+.3});
tl.to("#clock-dark",{{opacity:1,duration:2.2}},{S['clock'][0]+2.4});
// gerçek video sahneleri
tl.fromTo("#light-kb",{{scale:1.15}},{{scale:1.3,duration:{win('light')[1]},ease:"none"}},{S['light'][0]});
tl.fromTo("#hand-kb",{{scale:1.1}},{{scale:1.45,duration:{win('hand')[1]},ease:"power1.in"}},{S['hand'][0]});
tl.fromTo("#face-kb",{{scale:1.4}},{{scale:1.1,duration:{win('face')[1]},ease:"power2.out"}},{S['face'][0]});
tl.fromTo("#face-flash",{{opacity:.9}},{{opacity:0,duration:.5}},{S['face'][0]});
tl.fromTo("#meg",{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:.35,ease:"back.out(2)"}},{S['face'][0]+.05});
tl.to("#meg",{{opacity:0,duration:.4}},{S['face'][0]+1.9});
tl.fromTo("#portrait-kb",{{scale:1.02}},{{scale:1.18,duration:{win('portrait')[1]},ease:"none"}},{S['portrait'][0]});
tl.fromTo("#survivor",{{y:40,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.6)"}},{S['portrait'][0]+1.6});
tl.fromTo("#diver-kb",{{scale:1.2,y:40}},{{scale:1.02,y:0,duration:{win('diver')[1]},ease:"power1.out"}},{S['diver'][0]});

// başlık ve avatar girişi
tl.fromTo("#title",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"back.out(1.6)"}},.1);
tl.fromTo("#avatarbox",{{scale:.6,opacity:0}},{{scale:1,opacity:1,duration:.45,ease:"back.out(1.8)"}},0);
tl.fromTo("#bubble",{{x:-30,opacity:0}},{{x:0,opacity:1,duration:.4}},.15);
// avatar: hafif baş sallanması, göz kırpma, ağız
tl.to("#av #head",{{rotation:1.6,y:-3,transformOrigin:"50% 80%",duration:1.3,yoyo:true,repeat:{int(VOICE_END/1.3)},ease:"sine.inOut"}},0);
{''.join(f'tl.set("#av",{{attr:{{"data-b":"1"}}}},{t:.2f});tl.set("#av",{{attr:{{"data-b":"0"}}}},{t+0.13:.2f});' for t in blinks)}
[{','.join(mouth_js)}].forEach(([t,m])=>tl.set("#av",{{attr:{{"data-m":String(m)}}}},t));
tl.set("#av",{{attr:{{"data-m":"0"}}}},{VOICE_END});
// altyazılar
{''.join(cap_js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
(HF / "index.html").write_text(html, encoding="utf-8")
print("hf/index.html yazıldı:", len(chunks), "altyazı parçası,", len(mouth_js), "ağız değişimi")
