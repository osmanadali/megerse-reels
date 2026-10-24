"""Kendi kaydını akıcılaştır: uzun sessizlikleri kısalt + temizle + seviyele (kredisiz).

Kullanım: .venv/bin/python scripts/tighten.py giris.(m4a|mp3|wav) cikis.mp3 [--gap 0.22] [--max 0.32]
- --max'tan uzun sessizlikler --gap uzunluğuna indirilir (cümle içi akış korunur).
- 80 Hz altı kesilir, hafif kompresör, -16 LUFS.
"""
import argparse
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
p = argparse.ArgumentParser()
p.add_argument("src")
p.add_argument("out")
p.add_argument("--gap", type=float, default=.22)
p.add_argument("--max", type=float, default=.32)
p.add_argument("--thresh", type=float, default=-38, help="sessizlik eşiği dBFS")
a = p.parse_args()

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-af", "highpass=f=80", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32).astype(np.float64)
hop = int(SR * .01)
rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x) - hop, hop)])
db = 20 * np.log10(rms + 1e-12)
quiet = db < a.thresh
keep = np.ones(len(x), bool)
i, removed = 0, 0.0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]:
            j += 1
        dur = (j - i) * .01
        lim = .12 if (i == 0 or j == len(quiet)) else a.max   # baş/son sessizlik kısa
        tgt = .1 if (i == 0 or j == len(quiet)) else a.gap
        if dur > lim:
            cut = dur - tgt
            s0 = int((i * .01 + tgt / 2) * SR)
            keep[s0:s0 + int(cut * SR)] = False
            removed += cut
        i = j
    else:
        i += 1
y = x[keep]
# yumuşak geçiş: kesim noktalarında tıkırtı olmasın diye 5 ms çapraz sönüm yerine kısa fade (basit)
tmp = Path(a.out).with_suffix(".tmp.wav")
with wave.open(str(tmp), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af",
                "acompressor=threshold=-20dB:ratio=3:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "44100", "-b:a", "192k", a.out], check=True)
tmp.unlink()
print(f"{len(x)/SR:.1f} sn → {len(y)/SR:.1f} sn ({removed:.1f} sn sessizlik kısaldı) → {a.out}")
