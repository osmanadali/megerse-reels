#!/usr/bin/env bash
# Puanlama skill'i için girdi hazırlar: süre, çözünürlük, LUFS, 0.3/1/2 sn kareleri, kontak sayfası.
set -euo pipefail
IN="$1"; OUT="${2:-${IN%.*}_check}"; mkdir -p "$OUT"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of default=nw=1 "$IN"
for t in 0.3 1.0 2.0; do ffmpeg -v error -y -ss $t -i "$IN" -frames:v 1 -vf scale=540:-1 "$OUT/kare_${t}s.jpg"; done
ffmpeg -v error -y -i "$IN" -vf "fps=1/3,scale=270:-1,tile=6x2" -frames:v 1 "$OUT/kontak.jpg"
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | grep -q .; then
  ffmpeg -nostats -i "$IN" -filter_complex ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | sed 's/^/Ses (hedef -15\/-16 LUFS):/'
else echo "Ses: yok"; fi
echo "Kareler: $OUT"
