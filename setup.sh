#!/usr/bin/env bash
# @megerse.tr reels sistemi: tek komutla kurulum (Linux/macOS). Gerekenler: Node 18+, Python 3.10+, ffmpeg, git.
set -euo pipefail
cd "$(dirname "$0")"

npm install --no-fund --no-audit

python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
# İsteğe bağlı (matematik/infografik animasyonu): sistemde pango gerekir
#   Ubuntu: sudo apt install libpango1.0-dev pkg-config   macOS: brew install pango pkg-config
.venv/bin/pip install -q manim==0.22.0 || echo "manim kurulamadı (isteğe bağlı) — pango kurup tekrar dene"

# Vektör çizim kütüphanesi: Microsoft Fluent Emoji (MIT), yalnızca Flat SVG'ler (~56 MB)
if [ ! -d assets/fluentui-emoji ]; then
  mkdir -p assets
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/microsoft/fluentui-emoji.git assets/fluentui-emoji
  git -C assets/fluentui-emoji sparse-checkout set --no-cone '/assets/**/Flat/*.svg'
fi

cp node_modules/@fontsource/montserrat/files/montserrat-latin-ext-800-normal.woff2 \
   node_modules/@fontsource/montserrat/files/montserrat-latin-800-normal.woff2 public/
echo "Kurulum tamam. Deneme: npx remotion render src/index.ts Reel out/demo.mp4 --props='{\"reelId\":\"demo\"}'"
