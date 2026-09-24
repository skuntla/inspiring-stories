"""Narration: synthesize every line with Kokoro and measure word timings and visemes.

Kokoro returns, per token, the IPA phonemes and start/end times. Each word's phonemes are
spread across its duration and mapped to one of eight mouth shapes, so lip sync needs no
separate aligner. Kokoro itself is an optional install (`.[voice]`) and imported lazily.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

SAMPLE_RATE = 24000
LEAD_TRIM = 0.06   # keep this much silence before the first word
TAIL_KEEP = 0.12   # keep this much after the last word
JOIN_GAP = 0.06    # a word starting within this gap of the previous one is not separated by "rest"
SPEECH_FILE = Path("build") / "speech.json"
AUDIO_DIR = Path("build") / "audio"
VOICE_INSTALL = "uv pip install --python .venv/bin/python -e '.[voice]'"

# Misaki (Kokoro's G2P) phoneme -> mouth shape. Capital letters are Misaki's diphthongs.
VISEME: dict[str, str] = {}
for _chars, _shape in [
    ("mbp", "closed"),
    ("fv", "fv"),
    ("iɪjE", "ee"),
    ("eɛəɜᵊæ", "mid"),
    ("aɑʌAI", "open"),
    ("oɔOuʊwWYQ", "round"),
    ("tdnszkgŋhɹlʃʒθðʧʤɾ", "consonant"),
]:
    for _ch in _chars:
        VISEME[_ch] = _shape
VOWEL_SHAPES = {"ee", "mid", "open", "round"}
SHAPES = ("rest", "closed", "fv", "consonant", "ee", "mid", "open", "round")


def line_id(shot_id: str, index: int) -> str:
    """Derived line id: `<shot id>-l<NN>`, NN counted from 1 within the shot."""
    return f"{shot_id}-l{index + 1:02d}"


def word_visemes(phonemes: str, start: float, end: float) -> list[tuple[float, str]]:
    """Spread a word's phonemes over its duration; vowels get 1.6x the time of consonants."""
    shapes = [VISEME[ch] for ch in phonemes if ch in VISEME]
    if not shapes or end <= start:
        return []
    weights = [1.6 if s in VOWEL_SHAPES else 1.0 for s in shapes]
    total = sum(weights)
    out, t = [], start
    for shape, w in zip(shapes, weights):
        out.append((round(t, 3), shape))
        t += (end - start) * w / total
    return out


def line_visemes(words: list[dict]) -> list[tuple[float, str]]:
    """Viseme keys for a line from its words ({start, end, phonemes}), in time order.

    Each word ends in "rest", unless the next word starts within JOIN_GAP. Repeated
    shapes collapse into one key.
    """
    keys: list[tuple[float, str]] = []
    for w in words:
        if keys and keys[-1][1] == "rest" and w["start"] - keys[-1][0] < JOIN_GAP:
            keys.pop()
        keys += word_visemes(w.get("phonemes", ""), w["start"], w["end"])
        keys.append((round(w["end"], 3), "rest"))
    merged: list[tuple[float, str]] = []
    for t, shape in keys:
        if not merged or merged[-1][1] != shape:
            merged.append((t, shape))
    return merged


def spoken_pieces(text: str, pronunciations: dict[str, str]) -> list[tuple[str, str]]:
    """(display word, spoken form) per whitespace-separated word; overrides keep punctuation."""
    out = []
    for word in text.split():
        m = re.match(r"^(\W*)(.*?)(\W*)$", word)
        lead, core, trail = m.groups() if m else ("", word, "")
        spoken = pronunciations.get(core)
        out.append((word, f"{lead}{spoken}{trail}" if spoken else word))
    return out


def _alnum(s: str) -> str:
    return "".join(ch.lower() for ch in s if ch.isalnum())


def align_words(pieces: list[tuple[str, str]], tokens: list[dict]) -> list[dict]:
    """Assign Kokoro tokens ({text, phonemes, start, end}) to display words in order."""
    spoken_tokens = [t for t in tokens if _alnum(t["text"]) and t["start"] is not None and t["end"] is not None]
    words, i = [], 0
    for display, spoken in pieces:
        target = _alnum(spoken)
        if not target:
            continue
        acc, group = "", []
        while i < len(spoken_tokens) and len(acc) < len(target):
            acc += _alnum(spoken_tokens[i]["text"])
            group.append(spoken_tokens[i])
            i += 1
        if not group:  # Kokoro produced fewer tokens than words: stretch the last word
            if words:
                words[-1]["text"] += " " + display
            continue
        words.append({"text": display, "start": group[0]["start"], "end": group[-1]["end"],
                      "phonemes": " ".join(t["phonemes"] or "" for t in group)})
    if i < len(spoken_tokens) and words:  # leftover tokens belong to the last word
        words[-1]["end"] = spoken_tokens[-1]["end"]
    return words


# --- Kokoro -----------------------------------------------------------------------------

class VoiceUnavailable(Exception):
    pass


_PIPELINES: dict = {}


def kokoro_version() -> str:
    try:
        from importlib.metadata import version
        return version("kokoro")
    except Exception:  # noqa: BLE001
        return "unknown"


def synthesize(text: str, voice: str, speed: float):
    """Run Kokoro; returns (float32 samples, tokens [{text, phonemes, start, end}])."""
    try:
        import numpy as np
        from kokoro import KPipeline
    except ImportError as exc:
        raise VoiceUnavailable(f"Kokoro is not installed ({exc.name}); install it with: {VOICE_INSTALL}")
    lang = voice[0]  # 'a' American, 'b' British
    if lang not in _PIPELINES:
        _PIPELINES[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    chunks, tokens, offset = [], [], 0.0
    for result in _PIPELINES[lang](text, voice=voice, speed=speed):
        audio = np.asarray(result.audio, dtype=np.float32)
        for tok in result.tokens or []:
            tokens.append({"text": tok.text, "phonemes": tok.phonemes,
                           "start": None if tok.start_ts is None else offset + tok.start_ts,
                           "end": None if tok.end_ts is None else offset + tok.end_ts})
        chunks.append(audio)
        offset += len(audio) / SAMPLE_RATE
    return (np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float32)), tokens


@dataclass
class LineSpec:
    id: str
    speaker: str
    text: str
    spoken: str
    pieces: list[tuple[str, str]]
    voice: str
    speed: float
    pitch: float = 0.0  # semitones; a child's voice is a Kokoro voice raised a few semitones

    def digest(self, version: str) -> str:
        fields = {"spoken": self.spoken, "voice": self.voice, "speed": self.speed, "kokoro": version,
                  "lead_trim": LEAD_TRIM, "tail_keep": TAIL_KEEP}
        if self.pitch:
            fields["pitch"] = self.pitch  # only when set, so unpitched lines keep their cache
        payload = json.dumps(fields, sort_keys=True)
        return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


def line_specs(doc: dict, bible: dict) -> list[LineSpec]:
    voices = {c["id"]: c["voice"] for c in bible["characters"]}
    pron = doc.get("pronunciations") or {}
    specs = []
    for shot in doc["shots"]:
        for n, line in enumerate(shot["lines"]):
            pieces = spoken_pieces(line["text"], pron)
            v = voices[line["speaker"]]
            specs.append(LineSpec(line_id(shot["id"], n), line["speaker"], line["text"],
                                  " ".join(s for _, s in pieces), pieces, v["kokoro"], float(v["speed"]),
                                  float(v.get("pitch", 0))))
    return specs


def generate(episode_dir: Path, doc: dict, bible: dict, force: bool = False, log=print) -> dict:
    """Synthesize changed lines; write build/audio/*.wav and build/speech.json. Returns the speech doc."""
    speech_path = episode_dir / SPEECH_FILE
    previous = json.loads(speech_path.read_text()).get("lines", {}) if speech_path.is_file() else {}
    version = kokoro_version()
    (episode_dir / AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    lines: dict[str, dict] = {}
    made = 0
    for spec in line_specs(doc, bible):
        digest = spec.digest(version)
        wav = episode_dir / AUDIO_DIR / f"{spec.id}.wav"
        old = previous.get(spec.id)
        if not force and old and old.get("digest") == digest and wav.is_file():
            lines[spec.id] = old
            continue
        audio, tokens = synthesize(spec.spoken, spec.voice, spec.speed)
        words = align_words(spec.pieces, tokens)
        if not words:
            raise RuntimeError(f"{spec.id}: Kokoro returned no word timings for: {spec.spoken!r}")
        start = max(0.0, words[0]["start"] - LEAD_TRIM)
        end = min(len(audio) / SAMPLE_RATE, words[-1]["end"] + TAIL_KEEP)
        clip = audio[int(start * SAMPLE_RATE):int(round(end * SAMPLE_RATE))]
        for w in words:
            w["start"], w["end"] = round(w["start"] - start, 3), round(w["end"] - start, 3)
        if spec.pitch:
            clip = shift_pitch(clip, spec.pitch)
        _write_wav(wav, clip)
        lines[spec.id] = {
            "speaker": spec.speaker, "text": spec.text, "spoken": spec.spoken, "voice": spec.voice,
            "speed": spec.speed, **({"pitch": spec.pitch} if spec.pitch else {}), "digest": digest, "file": f"audio/{spec.id}.wav",
            "duration": round(len(clip) / SAMPLE_RATE, 3),
            "words": [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in words],
            "visemes": [[t, s] for t, s in line_visemes(words)],
        }
        made += 1
        log(f"  voiced {spec.id} ({spec.speaker}, {lines[spec.id]['duration']:.2f} s)")
    doc_out = {"schema": "story-speech/v1", "sample_rate": SAMPLE_RATE, "kokoro": version, "lines": lines}
    speech_path.write_text(json.dumps(doc_out, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    for stale in (episode_dir / AUDIO_DIR).glob("*.wav"):
        if stale.stem not in lines:
            stale.unlink()
    log(f"{made} line(s) synthesized, {len(lines) - made} reused; wrote {SPEECH_FILE}")
    return doc_out


def shift_pitch(samples, semitones: float):
    """Raise (or lower) pitch and formants together by `semitones`, keeping the exact length, so word
    timings and mouth shapes stay put. A few semitones up makes an adult voice sound like a child's."""
    import subprocess

    import numpy as np
    ratio = 2 ** (semitones / 12)
    cmd = ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SAMPLE_RATE), "-ac", "1", "-i", "pipe:0",
           "-af", f"asetrate={SAMPLE_RATE * ratio:.3f},aresample={SAMPLE_RATE},atempo={1 / ratio:.6f}",
           "-f", "f32le", "-ar", str(SAMPLE_RATE), "-ac", "1", "pipe:1"]
    out = subprocess.run(cmd, input=np.asarray(samples, dtype=np.float32).tobytes(), capture_output=True, check=True).stdout
    shifted = np.frombuffer(out, dtype=np.float32)
    fitted = np.zeros(len(samples), dtype=np.float32)
    fitted[:min(len(samples), len(shifted))] = shifted[:len(samples)]
    return fitted


def _write_wav(path: Path, samples) -> None:
    import soundfile as sf
    sf.write(path, samples, SAMPLE_RATE, subtype="PCM_16")
