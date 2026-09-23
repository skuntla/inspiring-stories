"""Generate the POC audio with Kokoro and derive word timings and a viseme track from it.

Kokoro returns, per word, its IPA phonemes and start/end times. Each word's phonemes are
spread across its duration (vowels weighted longer) and mapped to one of eight mouth shapes.
No separate aligner or lip-sync tool is needed.

Run with the voicemodels venv (it has kokoro installed):  npm run audio
Writes public/poc.wav and src/timeline.json.
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000
FPS = 30
LEAD_IN = 0.6       # seconds of silence before the first line
GAP = 0.45          # silence between lines
TAIL = 1.2          # hold after the last line

LINES = [
    {"speaker": "narrator", "voice": "af_heart", "speed": 0.95,
     "text": "Pip had walked the path many times. But this morning, a thick silver fog rolled across Willow Meadow."},
    {"speaker": "pip", "voice": "af_bella", "speed": 1.05,
     "text": "The fog is thick. But the ground beneath me is firm. I know this place."},
]

# Misaki (Kokoro's G2P) phoneme -> mouth shape. Capitals are Misaki's diphthongs.
VISEME = {}
for chars, shape in [
    ("mbp", "closed"),
    ("fv", "fv"),
    ("iɪjE", "ee"),                       # spread lips
    ("eɛəɜᵊæ", "mid"),
    ("aɑʌAI", "open"),
    ("oɔOuʊwWYQ", "round"),
    ("tdnszkgŋhɹlʃʒθðʧʤɾ", "consonant"),
]:
    for ch in chars:
        VISEME[ch] = shape
VOWEL_SHAPES = {"ee", "mid", "open", "round"}
IGNORE = set("ˈˌːʲ ")


def word_visemes(phonemes: str, start: float, end: float) -> list[tuple[float, str]]:
    shapes = [VISEME[ch] for ch in phonemes if ch not in IGNORE and ch in VISEME]
    if not shapes:
        return []
    weights = [1.6 if s in VOWEL_SHAPES else 1.0 for s in shapes]
    total = sum(weights)
    out, t = [], start
    for shape, w in zip(shapes, weights):
        out.append((round(t, 3), shape))
        t += (end - start) * w / total
    return out


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    track: list[np.ndarray] = [np.zeros(int(LEAD_IN * SR), dtype=np.float32)]
    cursor = LEAD_IN
    lines_out = []
    for n, line in enumerate(LINES):
        audio, words, visemes = [], [], []
        offset = 0.0
        for result in pipeline(line["text"], voice=line["voice"], speed=line["speed"]):
            chunk = np.asarray(result.audio, dtype=np.float32)
            for tok in result.tokens or []:
                if tok.start_ts is None or tok.end_ts is None:
                    continue
                s, e = cursor + offset + tok.start_ts, cursor + offset + tok.end_ts
                if not any(c.isalnum() for c in tok.text):
                    if words:
                        words[-1]["text"] += tok.text.strip()
                    continue
                if True:
                    words.append({"text": tok.text, "start": round(s, 3), "end": round(e, 3)})
                    # a previous word's closing "rest" is dropped when this word starts right after it
                    if visemes and visemes[-1][1] == "rest" and s - visemes[-1][0] < 0.06:
                        visemes.pop()
                    visemes += word_visemes(tok.phonemes or "", s, e)
                    visemes.append((round(e, 3), "rest"))
            offset += len(chunk) / SR
            audio.append(chunk)
        clip = np.concatenate(audio)
        # collapse repeats; keys are already in time order
        merged: list[tuple[float, str]] = []
        for t, shape in visemes:
            if not merged or merged[-1][1] != shape:
                merged.append((t, shape))
        duration = len(clip) / SR
        lines_out.append({"speaker": line["speaker"], "text": line["text"], "start": round(cursor, 3),
                          "end": round(cursor + duration, 3), "words": words,
                          "visemes": [{"t": t, "shape": s} for t, s in merged]})
        track.append(clip)
        cursor += duration
        gap = GAP if n < len(LINES) - 1 else TAIL
        track.append(np.zeros(int(gap * SR), dtype=np.float32))
        cursor += gap
    full = np.concatenate(track)
    peak = float(np.max(np.abs(full))) or 1.0
    full = full / peak * 0.89  # about -1 dBFS peak; loudness is not the point of this POC
    sf.write(root / "public" / "poc.wav", full, SR)
    timeline = {"fps": FPS, "durationInFrames": int(np.ceil(len(full) / SR * FPS)), "lines": lines_out}
    (root / "src" / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n")
    print(f"wrote public/poc.wav ({len(full) / SR:.2f} s) and src/timeline.json "
          f"({sum(len(l['visemes']) for l in lines_out)} viseme keys)")


if __name__ == "__main__":
    main()
