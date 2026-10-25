#!/usr/bin/env bash
# Seslendirmeyi işle → render. Kullanım: reels/dis-hekimi/ses_isle.sh <elevenlabs.mp3>
# Ses: ElevenLabs "Fatih Yıldırım" (eleven_v4, tek deneme) → reels/dis-hekimi/voice-raw.mp3 (yedek)
# Süre kuralı (Osman): toplam ≤ 80 sn → boşluklar sıkı (--max .26 --gap .17) + atempo 1.10 (ton korunur)
set -euo pipefail
cd "$(dirname "$0")/../.."
D=hf/assets/dis
TEMPO=${TEMPO:-1.10}
mkdir -p $D
.venv/bin/python scripts/tighten.py --max .26 --gap .17 "$1" $D/voice-tight.mp3
ffmpeg -v error -y -i $D/voice-tight.mp3 -filter:a atempo=$TEMPO -ar 44100 -b:a 192k $D/voice-fast.mp3
.venv/bin/python scripts/align.py $D/voice-fast.mp3 --text reels/dis-hekimi/metin.txt
.venv/bin/python scripts/insert_gap.py $D/voice-fast.mp3 $D/words.json --after "${HOOK_WORD:-öneriyor}" --gap 1.95 --out-audio $D/voice.mp3 --out-words reels/dis-hekimi/words.json
rm $D/words.json
python3 reels/dis-hekimi/build.py
.venv/bin/python -c "
import sys,json; sys.path.insert(0,'scripts')
from sfx import mix
mix('$D/voice.mp3',[tuple(e) for e in json.load(open('reels/dis-hekimi/sfx.json'))],'$D/mix.mp3',tail=4.6,fx_gain=.4)"
(cd hf && npx -y hyperframes@0.8.181 render -o renders/dis-hekimi.mp4 --quiet)
mkdir -p out && cp hf/renders/dis-hekimi.mp4 out/dis-hekimi.mp4
echo "→ hf/renders/dis-hekimi.mp4"
