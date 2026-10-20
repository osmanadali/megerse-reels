"""Hazır bir ses dosyasından (ör. ElevenLabs ya da kendi kaydın) kelime zamanları çıkarır. Yerel, kredisiz.

Kullanım:
  .venv/bin/python scripts/align.py public/reels/<id>/voice.mp3 [--model small] [--text metin.txt]

--text verilirse kelimeler senaryo metniyle eşlenir: zamanlar Whisper'dan, yazım metinden gelir.

İlk çalıştırmada model HuggingFace'ten indirilir (small ≈ 480 MB). CPU'da çalışır.
"""
import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel

p = argparse.ArgumentParser()
p.add_argument("audio")
p.add_argument("--model", default="small")
p.add_argument("--text", help="seslendirilen metin; altyazı yazımı buradan alınır")
a = p.parse_args()

model = WhisperModel(a.model, device="cpu", compute_type="int8")
# PyAV sürüm uyumsuzluğuna karşı sesi ffmpeg ile 16 kHz mono float32 olarak oku
import subprocess

import numpy as np

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
segments, _ = model.transcribe(np.frombuffer(pcm, np.float32), language="tr", word_timestamps=True, vad_filter=True)
words = [
    {"text": w.word.strip(), "startMs": round(w.start * 1000), "endMs": round(w.end * 1000)}
    for s in segments
    for w in s.words
]
if a.text:
    import difflib
    import re

    def norm(t):
        return re.sub(r"[^\wçğıöşü]", "", t.lower().replace("İ", "i").replace("I", "ı"))

    script = Path(a.text).read_text(encoding="utf-8").split()
    sm = difflib.SequenceMatcher(None, [norm(w["text"]) for w in words], [norm(t) for t in script], autojunk=False)
    fixed = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            fixed += [{**words[i1 + k], "text": script[j1 + k]} for k in range(i2 - i1)]
        elif j2 > j1:
            # eşleşmeyen bölüm: Whisper'ın aralığını senaryo kelimelerine eşit böl
            if i2 > i1:
                s0, e0 = words[i1]["startMs"], words[i2 - 1]["endMs"]
            else:
                s0 = fixed[-1]["endMs"] if fixed else 0
                e0 = words[i1]["startMs"] if i1 < len(words) else s0 + 300 * (j2 - j1)
            step = (e0 - s0) / (j2 - j1)
            fixed += [{"text": script[j1 + k], "startMs": round(s0 + k * step), "endMs": round(s0 + (k + 1) * step)} for k in range(j2 - j1)]
    words = fixed

out = Path(a.audio).with_name("words.json")
out.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(words)} kelime -> {out}  (yazımı metin.txt ile karşılaştır: Whisper Türkçe'de hata yapabilir)")
