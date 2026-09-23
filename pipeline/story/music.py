"""Music: a light background score composed in code for an episode, mixed under the voices.

The `hopeful` style is a soft pad, a low bass and a gentle piano arpeggio over I–V–vi–IV in D major.
It follows the story: each shot's energy comes from its characters' moods (sparse and quiet when
they are sad or worried, fuller when they are happy), the final shot resolves on the home chord,
and the whole bed ducks while anyone speaks. When an episode opens with a hook (a few seconds before
a `title-card` shot), the music waits and starts on the title card. Deterministic: the same episode
gives the same audio.
"""
from __future__ import annotations

import random
import zlib

STYLES = ("none", "hopeful")
BPM = 72
BEAT = 60.0 / BPM
BAR = 4 * BEAT
CHORD_BARS = 2
TONIC = 50  # MIDI D3
PROGRESSION = [(0, (0, 4, 7)), (7, (0, 4, 7)), (9, (0, 3, 7)), (5, (0, 4, 7))]  # I V vi IV
ENERGY = {"sad": 0.0, "tired": 0.0, "worried": 0.0, "scared": 0.0, "angry": 0.0, "thoughtful": 1.0,
          "calm": 1.0, "neutral": 1.0, "surprised": 1.0, "happy": 2.0, "proud": 2.0}
LEVEL_DB = -15.0      # the bed, between lines, relative to the voices' loudness
DUCK_DB = -7.0        # extra dip while someone speaks
FADE_IN, FADE_OUT = 1.5, 3.0
TITLE_CARD = "title-card"  # the shared location a hook cuts to; the music starts there
HOOK_SHOTS = 3             # a title card among the first shots marks the end of a hook


def _hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def shot_energy(timeline: dict) -> list[float]:
    """0 (low) .. 2 (bright) per shot: the lowest mood on screen; inserts keep the previous shot's."""
    out, last = [], 1.0
    for shot in timeline["shots"]:
        moods = [ENERGY.get(c.get("mood", "neutral"), 1.0) for c in shot.get("cast", [])]
        last = min(moods) if moods else last
        out.append(last)
    if out:
        out[-1] = 2.0  # the last shot lifts
    return out


def music_start(timeline: dict) -> float:
    """Seconds into the episode where the music begins: the title card after a hook, else 0."""
    for shot in timeline["shots"][:HOOK_SHOTS]:
        if shot.get("location") == TITLE_CARD:
            return shot["from"] / timeline["fps"]
    return 0.0


def chord_at(t: float, final_from: float) -> tuple[int, tuple[int, ...]]:
    if t >= final_from:
        return PROGRESSION[0]
    return PROGRESSION[int(t // (CHORD_BARS * BAR)) % len(PROGRESSION)]


def _energy_curve(timeline: dict, n: int, sr: int, np):
    """Per-sample energy, eased over ~2.5 s so layers cross-fade instead of switching."""
    fps = timeline["fps"]
    rate = 100
    control = np.zeros(int(np.ceil(n / sr * rate)) + 1, dtype=np.float32)
    for shot, e in zip(timeline["shots"], shot_energy(timeline)):
        a = int(shot["from"] / fps * rate)
        control[a:] = e
    k = int(2.5 * rate)
    padded = np.concatenate([np.full(k, control[0]), control, np.full(k, control[-1])])
    smooth = np.convolve(padded, np.ones(k) / k, mode="same")[k:-k]
    return np.interp(np.arange(n) / sr * rate, np.arange(len(smooth)), smooth).astype(np.float32)


def _piano(freq: float, sr: int, np, seconds: float = 3.2):
    t = np.arange(int(seconds * sr)) / sr
    tone = np.zeros_like(t)
    for h in range(1, 7):
        tone += np.sin(2 * np.pi * freq * h * (1 + 0.0004 * h * h) * t) * np.exp(-t * (1.1 + 0.9 * h)) / h ** 1.6
    return (tone * np.minimum(1.0, t / 0.006)).astype(np.float32)


def _reverb(x, sr: int, np, seed: int, seconds: float = 2.4, wet: float = 0.28):
    rng = np.random.default_rng(seed)
    t = np.arange(int(seconds * sr)) / sr
    ir = rng.standard_normal(len(t)) * np.exp(-t / 0.55)
    ir = np.convolve(ir, np.ones(12) / 12, mode="same")  # darker tail
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    tail = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x)]
    return ((1 - wet) * x + wet * tail).astype(np.float32)


def _duck(voice, sr: int, np):
    """1 between lines, DUCK_DB while speaking: eased in ~0.15 s ahead of speech, out over ~0.6 s."""
    hop = sr // 100
    frames_ = int(np.ceil(len(voice) / hop))
    padded = np.zeros(frames_ * hop, dtype=np.float32)
    padded[:len(voice)] = np.abs(voice)
    level = padded.reshape(frames_, hop).max(axis=1)
    speaking = (level > max(1e-4, level.max() * 0.02)).astype(np.float32)
    # hold through the gaps between words, open slightly early, close late
    held = np.convolve(speaking, np.ones(60), mode="full")[:frames_] > 0
    early = np.convolve(held.astype(np.float32)[::-1], np.ones(15), mode="full")[:frames_][::-1] > 0
    mask = np.convolve(early.astype(np.float32), np.ones(20) / 20, mode="same")
    gain = 1 - (1 - 10 ** (DUCK_DB / 20)) * np.clip(mask, 0, 1)
    return np.interp(np.arange(len(voice)) / hop, np.arange(frames_), gain).astype(np.float32)


def compose(timeline: dict, voice, sr: int, style: str = "hopeful"):
    """The music bed for `timeline`, as many samples as `voice`, already leveled and ducked under it."""
    import numpy as np
    n = len(voice)
    if style == "none" or n == 0:
        return np.zeros(n, dtype=np.float32)
    seed = zlib.crc32(timeline["episode"].encode())
    rnd = random.Random(seed)
    seconds = n / sr
    start = music_start(timeline)  # bars count from here, so the first chord lands on the title card
    final_from = timeline["shots"][-1]["from"] / timeline["fps"] - start
    energy = _energy_curve(timeline, n, sr, np)
    t = np.arange(n) / sr

    # pad: chord tones, two slightly detuned voices each, cross-faded between chord changes
    pad = np.zeros(n, dtype=np.float32)
    starts = sorted({*np.arange(start, seconds, CHORD_BARS * BAR).tolist(), final_from + start})
    starts = [s for s in starts if s < seconds]
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else seconds
        a, b = max(0, int((s - 1.2) * sr)), min(n, int((e + 1.2) * sr))
        seg = t[a:b]
        env = np.clip(np.minimum(seg - (s - 1.2), (e + 1.2) - seg) / 2.4, 0, 1)
        root, shape = chord_at(s - start + 0.01, final_from)
        for iv in (*shape, 12):
            f = _hz(TONIC + root % 12 + iv)
            for d in (-0.0012, 0.0012):
                pad[a:b] += np.sin(2 * np.pi * f * (1 + d) * seg) * env * 0.16
    pad *= 0.85 + 0.15 * np.sin(2 * np.pi * t / (2 * BAR))  # slow breathing swell

    # bass and piano notes, placed beat by beat
    bass = np.zeros(n, dtype=np.float32)
    piano = np.zeros(n, dtype=np.float32)
    # arpeggio shapes: (chord degree, octave above the pad) for each beat of a bar
    patterns = [((0, 1), (1, 1), (2, 1), (1, 1)), ((0, 1), (2, 1), (1, 1), (0, 2)), ((2, 0), (0, 1), (1, 1), (2, 1))]
    beat, pattern = 0, patterns[0]
    while start + beat * BEAT < seconds - 0.5:
        at = start + beat * BEAT
        i = int(at * sr)
        e = float(energy[min(i, n - 1)])
        root, shape = chord_at(at - start + 0.01, final_from)
        pos = beat % 4
        if pos == 0:
            pattern = rnd.choice(patterns)
            note = _piano(_hz(TONIC - 12 + root % 12), sr, np, 3.0) * 0.55
            bass[i:i + len(note)] += note[:n - i] * min(1.0, e / 1.2)
        # beat 1 always, beat 3 from medium energy, the off-beats only when bright
        threshold = {0: 0.0, 2: 0.7, 1: 1.45, 3: 1.45}[pos]
        if e >= threshold:
            degree, octave = pattern[pos]
            midi = TONIC + root % 12 + shape[degree] + 12 * octave
            jitter = int(rnd.uniform(-0.008, 0.008) * sr)
            j = max(0, i + jitter)
            vel = (0.5 + 0.2 * e) * rnd.uniform(0.85, 1.0) * (1.0 if pos == 0 else 0.8)
            note = _piano(_hz(midi), sr, np) * vel
            piano[j:j + len(note)] += note[:n - j]
        beat += 1

    music = pad * (0.9 - 0.15 * energy / 2) + bass * 0.5 + piano * 0.6
    music = _reverb(music, sr, np, seed)
    fade = np.minimum(1.0, np.minimum((t - start) / (0.6 if start else FADE_IN), (seconds - t) / FADE_OUT)).clip(0, 1)
    music *= fade

    # level against the voices, then duck under them
    voiced = np.abs(voice) > 1e-4
    voice_rms = float(np.sqrt(np.mean(voice[voiced] ** 2))) if voiced.any() else 0.1
    music_rms = float(np.sqrt(np.mean(music ** 2))) or 1.0
    music *= voice_rms * 10 ** (LEVEL_DB / 20) / music_rms
    return (music * _duck(voice, sr, np)).astype(np.float32)
