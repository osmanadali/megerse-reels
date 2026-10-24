#!/usr/bin/env bash
# Seslendirmeyi işle → render. Kullanım: reels/beyaz-sac/ses_isle.sh <ses.(mp3|m4a|wav)>
# v2 sesi: ElevenLabs "Fatih Yıldırım" (eleven_v4, tek deneme) → hf/assets/beyazsac/voice-v2-raw.mp3
set -euo pipefail
cd "$(dirname "$0")/../.."
SRC="$1"
D=hf/assets/beyazsac
.venv/bin/python scripts/tighten.py "$SRC" $D/voice-v2-tight.mp3
.venv/bin/python scripts/align.py $D/voice-v2-tight.mp3 --text reels/beyaz-sac/metin-v2.txt
# kancadan ("...daha tuhaf.") sonra intro için boşluk (INTRO_DUR 1,8 + 0,15 sn)
.venv/bin/python scripts/insert_gap.py $D/voice-v2-tight.mp3 $D/words.json --after tuhaf --gap 1.95 --out-audio $D/voice-v2.mp3 --out-words reels/beyaz-sac/words-v2.json
rm $D/words.json
python3 reels/beyaz-sac/build.py
.venv/bin/python -c "
import sys,json; sys.path.insert(0,'scripts')
from sfx import mix
mix('$D/voice-v2.mp3',[tuple(e) for e in json.load(open('reels/beyaz-sac/sfx-v2.json'))],'$D/mix-v2.mp3',tail=3.6)"
(cd hf && npx -y hyperframes@0.8.181 render -o renders/beyazsac-v2.mp4 --quiet)
echo "→ hf/renders/beyazsac-v2.mp4"
