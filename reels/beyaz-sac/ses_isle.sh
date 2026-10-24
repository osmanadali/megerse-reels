#!/usr/bin/env bash
# Osman'ın kaydını işle → render. Kullanım: reels/beyaz-sac/ses_isle.sh <kayit.(m4a|mp3|wav)>
set -euo pipefail
cd "$(dirname "$0")/../.."
SRC="$1"
.venv/bin/python scripts/tighten.py "$SRC" hf/assets/beyazsac/voice-osman.mp3
.venv/bin/python scripts/align.py hf/assets/beyazsac/voice-osman.mp3 --text reels/beyaz-sac/metin-v2.txt
mv hf/assets/beyazsac/words.json reels/beyaz-sac/words-v2.json
.venv/bin/python scripts/mouth.py hf/assets/beyazsac/voice-osman.mp3 hf/avatar/mouth-beyazsac-v2.json
python3 reels/beyaz-sac/build.py
.venv/bin/python -c "
import sys,json; sys.path.insert(0,'scripts')
from sfx import mix
mix('hf/assets/beyazsac/voice-osman.mp3',[tuple(e) for e in json.load(open('reels/beyaz-sac/sfx-v2.json'))],'hf/assets/beyazsac/mix-v2.mp3',tail=3.6)"
(cd hf && npx -y hyperframes@0.8.181 render -o renders/beyazsac-v2.mp4 --quiet)
echo "→ hf/renders/beyazsac-v2.mp4"
