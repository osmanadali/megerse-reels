"""Hazır bir ses dosyasından (ör. ElevenLabs ya da kendi kaydın) kelime zamanları çıkarır. Yerel, kredisiz.

Kullanım:
  .venv/bin/python scripts/align.py public/reels/<id>/voice.mp3 [--model small]

İlk çalıştırmada model HuggingFace'ten indirilir (small ≈ 480 MB). CPU'da çalışır.
"""
import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel

p = argparse.ArgumentParser()
p.add_argument("audio")
p.add_argument("--model", default="small")
a = p.parse_args()

model = WhisperModel(a.model, device="cpu", compute_type="int8")
segments, _ = model.transcribe(a.audio, language="tr", word_timestamps=True, vad_filter=True)
words = [
    {"text": w.word.strip(), "startMs": round(w.start * 1000), "endMs": round(w.end * 1000)}
    for s in segments
    for w in s.words
]
out = Path(a.audio).with_name("words.json")
out.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(words)} kelime -> {out}  (yazımı metin.txt ile karşılaştır: Whisper Türkçe'de hata yapabilir)")
