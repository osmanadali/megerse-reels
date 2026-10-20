#!/usr/bin/env bash
# Sesi Instagram için -16 LUFS'a getirir (puanlama hedefi -15/-16).
# Kullanım: scripts/loudnorm.sh giris.mp3 cikis.mp3
set -euo pipefail
ffmpeg -v error -y -i "$1" -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 "$2"
echo "-> $2"
