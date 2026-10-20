# @megerse.tr reels üretim sistemi (kredisiz araçlar)

| İş | Araç | Lisans |
|---|---|---|
| Montaj, efekt, geçiş, altyazı render | Remotion 4 (`remotion`, `@remotion/transitions`, `@remotion/captions`, `@remotion/lottie`) | Remotion License: bireyler ve ≤3 çalışanlı şirketlere ücretsiz |
| Ses normalizasyonu, kare çıkarma | FFmpeg | LGPL/GPL |
| Python tarafı kesme/birleştirme | MoviePy | MIT |
| Matematik/infografik animasyonu (isteğe bağlı) | Manim Community | MIT |
| Seslendirme + kelime zamanları | edge-tts (`tr-TR-AhmetNeural`, `tr-TR-EmelNeural`) | LGPL-3 (servis: Microsoft) |
| Hazır sesten kelime zamanı | faster-whisper | MIT |
| Kaynak toplama | ddgs + trafilatura + Wikipedia-API | MIT / Apache-2.0 / MIT |
| Vektör çizim kütüphanesi | Microsoft Fluent Emoji (Flat SVG, 1500+), OpenMoji | MIT / CC BY-SA 4.0 (atıf gerekir) |
| Elle çizilmiş görünüm, raster→vektör | rough.js, vtracer | MIT |
| Lottie animasyonları | lottie-web | MIT |
| Türkçe font | Montserrat (@fontsource) | OFL |

## Akış
1. `scripts/research.py "<konu>"` → kaynak topla, iddiaları doğrula
2. `public/reels/<id>/metin.txt` yaz → `scripts/tts.py` → `voice.mp3` + `words.json`
3. `scripts/loudnorm.sh` → -16 LUFS
4. `public/reels/<id>/reel.json` (sahneler, SVG'ler, words, kaynaklar; örnek: `public/reels/demo`)
5. `npx remotion render src/index.ts Reel out/<id>.mp4 --props='{"reelId":"<id>"}'`
6. `scripts/check.sh out/<id>.mp4` → puanlama skill'i (bağımsız hakem, ≥75 kapısı)

Kurulum: `./setup.sh`. Önizleme: `npm run studio`.

