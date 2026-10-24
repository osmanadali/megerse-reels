"""Ücretsiz, yerel ses efekti + müzik altlığı üreticisi ve miks (kredi harcamaz).

Kullanım (Python):
    from sfx import mix
    mix("hf/assets/x/voice.mp3", [(1.2, "whoosh"), (3.4, "pop", .8)], "hf/assets/x/mix.mp3", pad=True)
Efektler: whoosh, pop, tick, pluck, heartbeat, riser, boom, ding, swish
Sonuç -16 LUFS'a normalize edilir (Instagram).
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _lp(x, a):
    """tek kutuplu alçak geçiren; a: 0..1 (büyük = daha parlak), dizi olabilir."""
    y = np.zeros_like(x)
    a = np.broadcast_to(a, x.shape)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(d=.5):
    t = _t(d)
    env = np.sin(np.pi * t / d) ** 2
    cut = .02 + .25 * np.sin(np.pi * t / d)
    n = _lp(rng.standard_normal(len(t)), cut)
    return .9 * env * n / (np.abs(n).max() + 1e-9)


def swish(d=.28):
    t = _t(d)
    env = np.exp(-((t - d * .35) / (d * .18)) ** 2)
    n = _lp(rng.standard_normal(len(t)), .35)
    return .7 * env * n / (np.abs(n).max() + 1e-9)


def pop(d=.14):
    t = _t(d)
    f = 900 * np.exp(-t * 18) + 260
    return .8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)


def tick(d=.06):
    t = _t(d)
    return .6 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) + .3 * rng.standard_normal(len(t)) * np.exp(-t * 400)


def pluck(d=.12):
    """saç koparma 'çıt': keskin gürültü patlaması + yüksek rezonans."""
    t = _t(d)
    n = rng.standard_normal(len(t))
    hp = n - _lp(n, .2)
    return .9 * hp * np.exp(-t * 120) + .5 * np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 60)


def heartbeat(d=.9):
    t = _t(d)
    out = np.zeros_like(t)
    for s in (0, .22):
        tt = np.clip(t - s, 0, None)
        out += (t >= s) * np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 14)
    return .95 * out


def riser(d=1.4):
    t = _t(d)
    f = 180 + 1100 * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    n = _lp(rng.standard_normal(len(t)), .05 + .3 * t / d)
    env = (t / d) ** 2
    return .55 * env * (tone * .5 + n / (np.abs(n).max() + 1e-9))


def boom(d=1.0):
    t = _t(d)
    f = 70 * np.exp(-t * 2) + 38
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    n = _lp(rng.standard_normal(len(t)), .03) * np.exp(-t * 9)
    return .95 * (s + .8 * n / (np.abs(n).max() + 1e-9))


def ding(d=.9):
    t = _t(d)
    return .45 * (np.sin(2 * np.pi * 1320 * t) + .5 * np.sin(2 * np.pi * 1980 * t) + .25 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 5)


FX = dict(whoosh=whoosh, swish=swish, pop=pop, tick=tick, pluck=pluck, heartbeat=heartbeat, riser=riser, boom=boom, ding=ding)


def pad(d, gain=.06):
    """yumuşak, gergin müzik altlığı: düşük akor + yavaş tremolo + alçak geçiren."""
    t = _t(d)
    chord = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((55, 82.4, 110, 130.8, 164.8)))
    trem = .7 + .3 * np.sin(2 * np.pi * .25 * t)
    pulse = .5 + .5 * (np.sin(2 * np.pi * 1.6 * t) > .92)          # hafif nabız
    sig = _lp(chord * trem, .05) * (1 + .15 * pulse)
    fade = np.minimum(1, np.minimum(t / 1.5, (d - t) / 2.5))
    return gain * sig / (np.abs(sig).max() + 1e-9) * fade


def _read(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).astype(np.float64)


def mix(voice, events, out, pad_on=True, tail=4.0, fx_gain=.45, duck=.35):
    """events: [(saniye, efekt_adı[, kazanç])]. Ses konuşurken altlık kısılır (ducking)."""
    v = _read(voice)
    n = len(v) + int(SR * tail)
    bus = np.zeros(n)
    bus[:len(v)] += v
    fx = np.zeros(n)
    for ev in events:
        at, name = ev[0], ev[1]
        g = ev[2] if len(ev) > 2 else 1.0
        s = FX[name]()
        i = int(at * SR)
        j = min(n, i + len(s))
        fx[i:j] += g * s[: j - i]
    bus += fx_gain * fx
    if pad_on:
        p = pad(n / SR)
        env = np.abs(np.concatenate([v, np.zeros(n - len(v))]))
        k = int(SR * .25)
        sm = np.convolve(env, np.ones(k) / k, mode="same")
        dk = 1 - duck * np.clip(sm / (sm.max() * .25 + 1e-9), 0, 1)
        bus += p * dk
    bus /= max(1.0, np.abs(bus).max() / .95)
    tmp = Path(out).with_suffix(".wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((bus * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", str(out)], check=True)
    tmp.unlink()
    return out


if __name__ == "__main__":
    # örnek kütüphane: her efekti ayrı wav olarak yazar (dinleme/kontrol için)
    od = Path(sys.argv[1] if len(sys.argv) > 1 else "sfx_out")
    od.mkdir(parents=True, exist_ok=True)
    for k, f in FX.items():
        s = f()
        with wave.open(str(od / f"{k}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(s, -1, 1) * 32767).astype(np.int16).tobytes())
    print("yazıldı:", od)
