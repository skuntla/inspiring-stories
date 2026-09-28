"""Indic Parler-TTS worker: synthesizes lines in Indian languages for `story reel`.

Runs in its own environment (Parler needs different torch/transformers pins than Kokoro), so the
`story` CLI calls it as a subprocess with a JSON job file:

    {"lang": "hi", "out_dir": ".../build/lang-hi/audio", "sample_rate": 24000,
     "items": [{"id": "s01-l01", "text": "...", "description": "...", "pitch": 0}]}

Each line is split into sentences (long Telugu sentences are unreliable in one go). Every sentence
is transcribed with Whisper and regenerated with a new seed when the take rambles, drops words or
comes out in the wrong script; the sentences are then joined with short breaths, trimmed, shifted
in pitch if asked, resampled, and written as <id>.wav. Prints a JSON result per line.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

MODEL = "ai4bharat/indic-parler-tts"
TRIES = 6
GAP = 0.22  # seconds between sentences of one line
SCRIPTS = {"hi": [(0x0900, 0x097F)], "te": [(0x0C00, 0x0C7F), (0x0900, 0x097F)], "en": [(0x41, 0x7A)]}


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?।…])\s+", text.strip())
    out = []
    for p in parts:  # keep very short fragments with the previous sentence
        if out and len(p) < 8:
            out[-1] += " " + p
        else:
            out.append(p)
    return [p for p in out if p]


def in_script(heard: str, lang: str) -> float:
    letters = [c for c in heard if c.isalpha()]
    if not letters:
        return 0.0
    ok = sum(any(a <= ord(c) <= b for a, b in SCRIPTS[lang]) for c in letters)
    return ok / len(letters)


def score(text: str, heard: str, seconds: float, lang: str) -> float:
    """0 is perfect; larger is worse. A take over 1.0 is rejected."""
    ratio = len(heard.replace(" ", "")) / max(1, len(text.replace(" ", "")))
    per_char = seconds / max(1, len(text))
    bad = abs(1 - ratio) / 0.45
    if in_script(heard, lang) < 0.7:
        bad += 2
    if per_char > 0.17:
        bad += 2
    return bad


def trim(a: np.ndarray, sr: int, floor: float = 0.02) -> np.ndarray:
    loud = np.where(np.abs(a) > floor * np.abs(a).max())[0]
    if not len(loud):
        return a
    pad = int(0.06 * sr)
    return a[max(0, loud[0] - pad): loud[-1] + pad]


def ffmpeg_filter(a: np.ndarray, sr_in: int, sr_out: int, pitch: float) -> np.ndarray:
    ratio = 2 ** (pitch / 12)
    af = f"asetrate={sr_in * ratio:.3f},aresample={sr_out},atempo={1 / ratio:.6f}" if pitch else f"aresample={sr_out}"
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr_in), "-ac", "1", "-i", "pipe:0", "-af", af,
                          "-f", "f32le", "-ar", str(sr_out), "-ac", "1", "pipe:1"],
                         input=a.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32)


def main(job_path: str) -> None:
    from faster_whisper import WhisperModel
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer

    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    lang, out_dir, sr_out = job["lang"], Path(job["out_dir"]), int(job.get("sample_rate", 24000))
    out_dir.mkdir(parents=True, exist_ok=True)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL).to(device)
    tok = AutoTokenizer.from_pretrained(MODEL)
    desc_tok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    sr = model.config.sampling_rate
    asr = WhisperModel("medium" if lang == "te" else "small", device="cpu", compute_type="int8")
    for item in job["items"]:
        d = desc_tok(item["description"], return_tensors="pt").to(device)
        pieces, notes = [], []
        for sent in sentences(item["text"]):
            p = tok(sent, return_tensors="pt").to(device)
            best, best_score, best_heard = None, 1e9, ""
            for seed in range(TRIES):
                torch.manual_seed(seed)
                with torch.no_grad():
                    gen = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                         prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
                a = trim(gen.cpu().numpy().squeeze().astype(np.float32), sr)
                tmp = out_dir / f"_{item['id']}.wav"
                sf.write(tmp, a, sr)
                heard = " ".join(s.text.strip() for s in asr.transcribe(str(tmp), language=lang)[0])
                tmp.unlink()
                s = score(sent, heard, len(a) / sr, lang)
                if s < best_score:
                    best, best_score, best_heard = a, s, heard
                if s <= 1.0:
                    break
            pieces += [best, np.zeros(int(GAP * sr), np.float32)]
            notes.append({"sentence": sent, "heard": best_heard, "ok": best_score <= 1.0, "tries": seed + 1})
        audio = np.concatenate(pieces[:-1])
        audio = ffmpeg_filter(audio / max(1e-6, np.abs(audio).max()) * 0.9, sr, sr_out, float(item.get("pitch", 0)))
        path = out_dir / f"{item['id']}.wav"
        sf.write(path, audio, sr_out, subtype="PCM_16")
        print(json.dumps({"id": item["id"], "file": str(path), "duration": round(len(audio) / sr_out, 3),
                          "ok": all(n["ok"] for n in notes), "sentences": notes}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
