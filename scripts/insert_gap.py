"""Sese belirli bir kelimeden sonra sessizlik ekler ve kelime zamanlarını kaydırır (intro boşluğu için).

Kullanım:
    .venv/bin/python scripts/insert_gap.py voice.mp3 words.json --after tuhaf --gap 1.95 --out-audio out.mp3 --out-words out.json
'--after' kelimesinin ilk geçtiği yerin bitişinden .08 sn sonra keser (sonraki kelimeye taşmadan).
"""
import argparse
import json
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("words")
ap.add_argument("--after", required=True)
ap.add_argument("--gap", type=float, required=True)
ap.add_argument("--out-audio", required=True)
ap.add_argument("--out-words", required=True)
a = ap.parse_args()

words = json.load(open(a.words, encoding="utf-8"))
i = next(k for k, w in enumerate(words) if w["text"].lower().startswith(a.after.lower()))
cut = words[i]["endMs"] / 1000 + .08
if i + 1 < len(words):
    cut = min(cut, words[i + 1]["startMs"] / 1000 - .02)
fmt = "aformat=sample_rates=44100:channel_layouts=mono"
fc = (f"[0]{fmt},atrim=0:{cut:.3f},asetpts=PTS-STARTPTS[a];[0]{fmt},atrim={cut:.3f},asetpts=PTS-STARTPTS[b];"
      f"anullsrc=r=44100:cl=mono,atrim=0:{a.gap:.3f}[s];[a][s][b]concat=n=3:v=0:a=1[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-filter_complex", fc, "-map", "[o]", "-b:a", "192k", a.out_audio], check=True)
sh = int(round(a.gap * 1000))
for w in words[i + 1:]:
    w["startMs"] += sh
    w["endMs"] += sh
json.dump(words, open(a.out_words, "w", encoding="utf-8"), ensure_ascii=False)
print(f"kesim {cut:.2f} sn, {a.gap} sn boşluk; {len(words) - i - 1} kelime kaydırıldı")
