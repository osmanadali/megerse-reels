"""Ücretsiz Türkçe seslendirme + kelime zamanları (edge-tts).

Kullanım:
  .venv/bin/python scripts/tts.py public/reels/<id>/metin.txt public/reels/<id> [--voice tr-TR-AhmetNeural] [--rate +8%]

Çıktı: voice.mp3 ve words.json (reel.json'daki "words" alanına konur).
Altyazı için Whisper'a gerek kalmaz: kelime zamanları doğrudan TTS'ten gelir.
"""
import argparse
import asyncio
import json
from pathlib import Path

import edge_tts


async def main(text_file: str, out_dir: str, voice: str, rate: str) -> None:
    text = Path(text_file).read_text(encoding="utf-8").strip()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    words = []
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    with open(out / "voice.mp3", "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000  # 100 ns -> ms
                words.append({
                    "text": chunk["text"],
                    "startMs": round(start),
                    "endMs": round(start + chunk["duration"] / 10_000),
                })
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(words)} kelime, {words[-1]['endMs'] / 1000:.1f} sn -> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("text_file")
    p.add_argument("out_dir")
    p.add_argument("--voice", default="tr-TR-AhmetNeural")  # kadın ses: tr-TR-EmelNeural
    p.add_argument("--rate", default="+8%")
    a = p.parse_args()
    asyncio.run(main(a.text_file, a.out_dir, a.voice, a.rate))
