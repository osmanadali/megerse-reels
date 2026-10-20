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

VOICE_END = 69.6
TOTAL = 73.6
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
    "hand": (45.2, 51.22),
    "face": (51.22, 54.32),
    "portrait": (54.32, 62.22),
    "diver": (62.22, 65.5),
    "team": (65.5, VOICE_END),
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
        <svg class="fill" viewBox="0 0 960 1080">
          <defs>
            <linearGradient id="deep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C86B0"/><stop offset=".3" stop-color="#145578"/><stop offset=".7" stop-color="#082C46"/><stop offset="1" stop-color="#03111E"/></linearGradient>
            <linearGradient id="sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A5040"/><stop offset="1" stop-color="#1E1A14"/></linearGradient>
            <radialGradient id="silt" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#8A8270" stop-opacity=".85"/><stop offset="1" stop-color="#8A8270" stop-opacity="0"/></radialGradient>
            <linearGradient id="surf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE9FF"/><stop offset="1" stop-color="#2C86B0" stop-opacity="0"/></linearGradient>
          </defs>
          <rect width="960" height="1080" fill="url(#deep)"/>
          <g id="world"><g transform="translate(0 330)">
            <rect x="0" y="-420" width="960" height="486" fill="#1A2633"/><path d="M0 -420 H960 V20 Q700 -20 480 10 T0 0 Z" fill="#22364A" opacity=".85"/>
            <path d="M0 0 H960 V62 Q900 80 840 64 T720 62 T600 70 T480 60 T360 70 T240 62 T120 72 T0 64 Z" fill="url(#surf)" opacity=".9"/>
            <path d="M0 64 Q120 80 240 62 T480 60 T720 62 T960 62" stroke="#E6F7FF" stroke-width="3" fill="none" opacity=".7"/>
            {''.join(f'<path d="M{(i*137)%960} {90+(i*29)%60} q30 -10 60 0 t60 0" stroke="#CFF0FF" stroke-width="2" fill="none" opacity=".25"/>' for i in range(14))}
            {''.join(f'<polygon points="{x},0 {x+70},0 {x+260},1080 {x+150},1080" fill="#BFE6FF" opacity=".07"/>' for x in (60,300,560,760))}
            <g id="seabed">
              <path d="M0 960 Q120 930 260 950 T540 944 T820 956 T960 948 V1080 H0 Z" fill="url(#sand)"/>
              <g fill="#2B261F"><ellipse cx="120" cy="980" rx="40" ry="16"/><ellipse cx="790" cy="990" rx="56" ry="20"/><ellipse cx="610" cy="1010" rx="24" ry="10"/></g>
              <path d="M70 960 q6 -40 -4 -70 M84 958 q10 -30 4 -54 M860 956 q-8 -36 2 -66" stroke="#2F4A2C" stroke-width="5" fill="none" stroke-linecap="round"/>
            </g>
            <g id="ship" transform="translate(480 22) scale(.72)"><defs>
  <linearGradient id="hullG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D23A30"/><stop offset=".55" stop-color="#A72720"/><stop offset="1" stop-color="#5E1410"/></linearGradient>
  <linearGradient id="belowG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6B1F1A"/><stop offset="1" stop-color="#2E0D0B"/></linearGradient>
  <linearGradient id="whiteG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9D0D6"/></linearGradient>
  <linearGradient id="whiteSide" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#E9EDF0"/><stop offset=".7" stop-color="#FAFBFB"/><stop offset="1" stop-color="#B8C0C7"/></linearGradient>
  <linearGradient id="glassG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5D86A6"/><stop offset=".45" stop-color="#1D3A52"/><stop offset="1" stop-color="#0D1B27"/></linearGradient>
  <linearGradient id="steelG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8E979F"/><stop offset=".5" stop-color="#D3D8DC"/><stop offset="1" stop-color="#6F7880"/></linearGradient>
  <linearGradient id="tyreG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3A3A"/><stop offset="1" stop-color="#0E0E0E"/></linearGradient>
  <linearGradient id="shadeG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient>
</defs>
<g id="tug">
  <!-- direk, radar, ışıklar -->
  <rect x="18" y="-318" width="8" height="96" fill="url(#steelG)"/>
  <rect x="-22" y="-290" width="88" height="6" rx="3" fill="#C9CFD4"/>
  <ellipse cx="22" cy="-322" rx="26" ry="9" fill="url(#whiteG)" stroke="#5B656E" stroke-width="2"/>
  <rect x="-40" y="-262" width="60" height="5" rx="2.5" fill="#3B444C"/>
  <circle cx="-18" cy="-293" r="4" fill="#F5D36B"/><circle cx="62" cy="-293" r="4" fill="#E2453C"/>
  <!-- köprü üstü (wheelhouse) -->
  <path d="M-64 -232 L104 -232 L116 -222 L-70 -222 Z" fill="#E7EBEE" stroke="#4A545D" stroke-width="2"/>
  <path d="M-58 -222 L100 -222 L112 -172 L-58 -172 Z" fill="url(#whiteSide)" stroke="#4A545D" stroke-width="2.5"/>
  <path d="M-46 -214 L-8 -214 L-8 -184 L-46 -184 Z M2 -214 L40 -214 L40 -184 L2 -184 Z M50 -214 L92 -214 L100 -184 L50 -184 Z" fill="url(#glassG)" stroke="#27323B" stroke-width="2"/>
  <path d="M-42 -212 L-26 -212 L-40 -190 Z M6 -212 L22 -212 L8 -190 Z M54 -212 L70 -212 L56 -190 Z" fill="#BFD6E8" opacity=".55"/>
  <!-- 2. kat -->
  <path d="M-92 -172 L118 -172 L122 -112 L-96 -112 Z" fill="url(#whiteSide)" stroke="#4A545D" stroke-width="2.5"/>
  <path d="M-96 -172 L122 -172" stroke="#8C959D" stroke-width="5"/>
  <g fill="url(#glassG)" stroke="#27323B" stroke-width="2"><rect x="-74" y="-156" width="30" height="22" rx="4"/><rect x="-30" y="-156" width="30" height="22" rx="4"/><rect x="14" y="-156" width="30" height="22" rx="4"/><rect x="58" y="-156" width="30" height="22" rx="4"/></g>
  <path d="M-110 -178 L-96 -178 M122 -178 L136 -178 M136 -178 L136 -112" stroke="#7D8790" stroke-width="3"/>
  <path d="M122 -150 L150 -150 M122 -132 L150 -132" stroke="#A3ACB4" stroke-width="2"/>
  <!-- egzoz bacaları -->
  <g><path d="M-128 -190 L-108 -190 L-104 -40 L-130 -40 Z" fill="url(#steelG)" stroke="#40484F" stroke-width="2"/><rect x="-130" y="-198" width="24" height="10" fill="#1C1C1C"/>
     <path d="M-100 -180 L-82 -180 L-80 -40 L-102 -40 Z" fill="url(#steelG)" stroke="#40484F" stroke-width="2"/><rect x="-102" y="-188" width="22" height="10" fill="#1C1C1C"/></g>
  <!-- ana güverte evi -->
  <path d="M-150 -112 L170 -112 L176 -24 L-156 -24 Z" fill="url(#whiteSide)" stroke="#4A545D" stroke-width="2.5"/>
  <path d="M-156 -112 L176 -112" stroke="#8C959D" stroke-width="6"/>
  <g fill="#22323F" stroke="#5B6872" stroke-width="3">
    <circle cx="-120" cy="-70" r="10"/><circle cx="-84" cy="-70" r="10"/><circle cx="-48" cy="-70" r="10"/><circle cx="-12" cy="-70" r="10"/><circle cx="24" cy="-70" r="10"/><circle cx="60" cy="-70" r="10"/><circle cx="96" cy="-70" r="10"/><circle cx="132" cy="-70" r="10"/>
  </g>
  <rect x="146" y="-100" width="20" height="64" rx="3" fill="#D5DBE0" stroke="#5B656E" stroke-width="2"/>
  <path d="M-156 -40 L176 -40" stroke="#AEB6BD" stroke-width="2"/>
  <!-- kıç güverte: römork vinci, babalar -->
  <rect x="-262" y="-58" width="70" height="34" rx="6" fill="#2F5F7E" stroke="#1B2E3B" stroke-width="2.5"/>
  <ellipse cx="-227" cy="-41" rx="22" ry="14" fill="#173246"/><path d="M-249 -41 L-205 -41" stroke="#C8CED3" stroke-width="3"/>
  <path d="M-290 -24 L-290 -48 M-280 -24 L-280 -48" stroke="#2A2A2A" stroke-width="7" stroke-linecap="round"/>
  <path d="M-182 -24 L-182 -64 L-164 -64 L-164 -24" fill="none" stroke="#F0B429" stroke-width="7"/>
  <!-- ön güverte ırgat -->
  <rect x="200" y="-48" width="40" height="24" rx="5" fill="#2F5F7E" stroke="#1B2E3B" stroke-width="2"/>
  <!-- küpeşte (bulwark) -->
  <path d="M-306 -24 L300 -40 L312 -40 L314 -12 L-306 2 Z" fill="url(#hullG)" stroke="#3A0C09" stroke-width="3"/>
  <path d="M-306 -26 L312 -42" stroke="#F2F2EE" stroke-width="6" stroke-linecap="round"/>
  <!-- gövde -->
  <path d="M-306 2 L314 -12 C318 30 300 80 250 104 C200 122 120 128 0 128 L-210 126 C-270 124 -300 100 -306 60 Z" fill="url(#hullG)" stroke="#3A0C09" stroke-width="4" stroke-linejoin="round"/>
  <!-- su hattı altı (zehirli boya) -->
  <path d="M-305 70 L300 66 C290 88 270 98 250 104 C200 122 120 128 0 128 L-210 126 C-270 124 -298 102 -305 70 Z" fill="url(#belowG)"/>
  <path d="M-305 66 L302 62" stroke="#111" stroke-width="7"/>
  <!-- gövde levha çizgileri ve pas izleri -->
  <path d="M-200 4 L-200 120 M-90 2 L-90 126 M20 0 L20 128 M130 -4 L130 124 M230 -8 L230 108" stroke="#7A1C16" stroke-width="2" opacity=".6"/>
  <path d="M-250 8 l2 30 M-160 6 l1 22 M-40 4 l2 34 M80 2 l1 26 M190 -2 l2 30" stroke="#6B3A1E" stroke-width="3" opacity=".45" stroke-linecap="round"/>
  <!-- lastik usturmaçalar -->
  <g fill="url(#tyreG)" stroke="#000" stroke-width="2">
    <ellipse cx="-270" cy="22" rx="17" ry="19"/><ellipse cx="-222" cy="21" rx="17" ry="19"/><ellipse cx="-174" cy="20" rx="17" ry="19"/><ellipse cx="-126" cy="19" rx="17" ry="19"/><ellipse cx="-78" cy="18" rx="17" ry="19"/><ellipse cx="-30" cy="17" rx="17" ry="19"/><ellipse cx="18" cy="16" rx="17" ry="19"/><ellipse cx="66" cy="15" rx="17" ry="19"/><ellipse cx="114" cy="14" rx="17" ry="19"/><ellipse cx="162" cy="13" rx="17" ry="19"/><ellipse cx="210" cy="11" rx="17" ry="19"/>
  </g>
  <g fill="none" stroke="#555" stroke-width="2" opacity=".7">
    <ellipse cx="-270" cy="22" rx="7" ry="8"/><ellipse cx="-222" cy="21" rx="7" ry="8"/><ellipse cx="-174" cy="20" rx="7" ry="8"/><ellipse cx="-126" cy="19" rx="7" ry="8"/><ellipse cx="-78" cy="18" rx="7" ry="8"/><ellipse cx="-30" cy="17" rx="7" ry="8"/><ellipse cx="18" cy="16" rx="7" ry="8"/><ellipse cx="66" cy="15" rx="7" ry="8"/><ellipse cx="114" cy="14" rx="7" ry="8"/><ellipse cx="162" cy="13" rx="7" ry="8"/><ellipse cx="210" cy="11" rx="7" ry="8"/>
  </g>
  <path d="M290 -36 C312 -30 318 0 316 30 C314 60 300 84 276 98" fill="none" stroke="#151515" stroke-width="12" stroke-linecap="round"/><path d="M296 -30 C310 -20 312 4 310 28" fill="none" stroke="#3C3C3C" stroke-width="3" stroke-linecap="round"/>
  <!-- dümen ve pervane nozulu -->
  <path d="M-250 112 L-250 146 L-214 146 L-214 118" fill="#3A1512" stroke="#1A0705" stroke-width="3"/>
  <ellipse cx="-180" cy="130" rx="26" ry="20" fill="#5A4A2A" stroke="#2A1F10" stroke-width="3"/>
  <!-- genel gölgelendirme -->
  <path d="M-306 2 L314 -12 C318 30 300 80 250 104 C200 122 120 128 0 128 L-210 126 C-270 124 -300 100 -306 60 Z" fill="url(#shadeG)"/>
</g>
</g>
            <g id="siltcloud" opacity="0"><ellipse cx="340" cy="930" rx="200" ry="70" fill="url(#silt)"/><ellipse cx="620" cy="935" rx="220" ry="80" fill="url(#silt)"/><ellipse cx="480" cy="900" rx="260" ry="90" fill="url(#silt)"/></g>
          </g></g>
          {''.join(f'<circle cx="{(i*53)%960}" cy="{(i*97)%1080}" r="{1.2+(i%3)*.8}" fill="#DDEFFF" opacity=".35" class="snow"/>' for i in range(60))}
          {''.join(f'<circle cx="{380+(i*37)%200}" cy="{360+(i*41)%120}" r="{4+i%6}" fill="none" stroke="#BFE3FF" stroke-width="2" opacity=".6" class="bub"/>' for i in range(18))}
          <rect id="sinkdark" width="960" height="1080" fill="#020810" opacity="0"/>
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


    <!-- 11b kurtarmadan sonra: en soldaki kurtaran dalgıç Nico van Heerden -->
    <div class="scene clip" id="s-team" data-start="{win('team')[0]}" data-duration="{win('team')[1]}" data-track-index="1" style="background:#0B1220">
      <div class="fill" id="team-in">
        <div class="fill" style="background:url(assets/okene/basinc-odasi-dalgiclar.jpg) center/cover; filter: blur(28px) brightness(.45); transform: scale(1.2)"></div>
        <div id="team-kb" style="position:absolute; left:0; top:180px; width:960px; height:720px">
          <img src="assets/okene/basinc-odasi-dalgiclar.jpg" alt="" style="width:100%; height:100%; display:block">
          <svg viewBox="0 0 960 720" style="position:absolute; inset:0; width:100%; height:100%">
            <circle id="ring" cx="150" cy="215" r="135" fill="none" stroke="#F5B82E" stroke-width="10" stroke-dasharray="849" stroke-dashoffset="849"/>
          </svg>
        </div>
        <div id="team-label" style="position:absolute; left:36px; top:44px; right:36px; padding:18px 24px; border-radius:18px; background:#F5B82E; color:#0B1220">
          <div style="font-weight:800; font-size:44px; line-height:1.1">NICO VAN HEERDEN</div>
          <div style="font-weight:600; font-size:30px; margin-top:6px">Okene'yi dipte bulan dalgıç · en solda</div>
        </div>
        <div class="chip" style="bottom:40px">KURTARMADAN SONRA · 2013</div>
      </div>
    </div>
    <!-- 12 kaynakça -->
    <div class="scene clip" id="s-sources" data-start="{win('sources')[0]}" data-duration="{win('sources')[1]}" data-track-index="1" style="background:#0B1220">
      <div class="fill" id="sources-in" style="padding:90px 70px">
        <div style="font-weight:800; font-size:56px; color:#F5B82E; margin-bottom:40px">KAYNAKLAR</div>
        <div class="src">ABC News (Haziran ve Aralık 2013)<br>ITV News (2 Aralık 2013)<br>Netwerk24 (8 Temmuz 2015)<br>Explorersweb (2021)<br>Soundings Online<br><br>Görüntü: DCN Diving / The Telegraph</div>
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
tl.fromTo("#ship",{{attr:{{transform:"translate(480 22) scale(.72) rotate(0)"}}}},{{attr:{{transform:"translate(480 60) scale(.72) rotate(-35)"}},duration:.9,ease:"power2.in"}},{S['sink'][0]+.1});
tl.to("#ship",{{attr:{{transform:"translate(480 150) scale(.72) rotate(-180)"}},duration:1.1,ease:"power2.out"}},{S['sink'][0]+1.0});
tl.to("#ship",{{attr:{{transform:"translate(470 740) scale(.72) rotate(-176)"}},duration:3.2,ease:"power1.in"}},{S['sink'][0]+2.1});
tl.to("#ship",{{attr:{{transform:"translate(470 732) scale(.72) rotate(-178)"}},duration:.3,ease:"power2.out"}},{S['sink'][0]+5.3});
tl.to("#siltcloud",{{opacity:1,duration:.5}},{S['sink'][0]+5.25}).to("#siltcloud",{{opacity:.6,duration:.6}});
tl.fromTo("#siltcloud",{{scale:.6,transformOrigin:"50% 90%"}},{{scale:1.15,duration:1.1,ease:"power2.out"}},{S['sink'][0]+5.25});
tl.fromTo("#world",{{y:0}},{{y:-400,duration:5,ease:"power1.inOut"}},{S['sink'][0]+.5});
tl.to("#sinkdark",{{opacity:.45,duration:4,ease:"power1.in"}},{S['sink'][0]+1.5});
tl.fromTo(".snow",{{y:0}},{{y:-120,duration:{win('sink')[1]},ease:"none"}},{S['sink'][0]});
const depth = {{v:0}};
tl.to(depth,{{v:30,duration:3.4,ease:"power1.in",onUpdate:()=>{{document.getElementById("depth").textContent=Math.round(depth.v)}}}},{S['sink'][0]+2.0});
tl.fromTo(".bub",{{y:0,opacity:.7}},{{y:-320,opacity:0,duration:1.8,stagger:.09,ease:"power1.out"}},{S['sink'][0]+.9});
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
tl.fromTo("#team-kb",{{scale:1,transformOrigin:"16% 30%"}},{{scale:1.35,duration:{win('team')[1]},ease:"power1.inOut"}},{S['team'][0]});
tl.to("#ring",{{attr:{{"stroke-dashoffset":0}},duration:.7,ease:"power2.out"}},{S['team'][0]+.5});
tl.fromTo("#team-label",{{y:-30,opacity:0}},{{y:0,opacity:1,duration:.45,ease:"back.out(1.7)"}},{S['team'][0]+.8});
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
