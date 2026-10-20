"""Avatar ağız zarfı: sesin 30 fps RMS'inden 0-3 ağız seviyesi dizisi (JSON string) üretir.

Kullanım: python3 scripts/mouth.py <ses.mp3> <çıktı.json>
"""
import json
import subprocess
import sys

import numpy as np

audio, out = sys.argv[1], sys.argv[2]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(pcm, np.float32)
hop = 16000 // 30
r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
r = r / np.percentile(r, 95)
levels = "".join(map(str, np.digitize(r, [0.12, 0.35, 0.65])))
json.dump(levels, open(out, "w"))
print(len(levels), "kare ->", out)
