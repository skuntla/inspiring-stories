"""Timeline: turn a locked episode plus its measured speech into one frame-exact description of
the video (build/timeline.json) and the mixed narration track (build/narration.wav).

All timing, staging and camera decisions happen here; the renderer only draws.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import tempfile
from pathlib import Path

from . import voice
from .voice import SAMPLE_RATE, SPEECH_FILE, line_specs

FPS = 30
WIDTH, HEIGHT = 1920, 1080
LEAD_IN = 0.5
DEFAULT_PAUSE = 0.35
TAIL = 1.0
MIN_SHOT = 2.5
CAPTION_PAGE = 7
CAPTION_HOLD = 0.3          # seconds a caption page stays after its last word
TARGET_LUFS = -14.0
TRUE_PEAK = -1.0
TIMELINE_FILE = Path("build") / "timeline.json"
NARRATION_FILE = Path("build") / "narration.wav"

POSITION_X = {"left": 0.18, "center_left": 0.35, "center": 0.5, "center_right": 0.65, "right": 0.82,
              "background": 0.5}
INTENSITY = {"low": (0.06, 0.06), "medium": (0.12, 0.12), "high": (0.20, 0.20)}  # (zoom delta, pan fraction)
SAMPLES_PER_FRAME = SAMPLE_RATE // FPS  # 800


class StaleSpeech(Exception):
    pass


def frames(seconds: float) -> int:
    """Seconds to whole frames, always rounding up (so nothing is cut short)."""
    return int(math.ceil(round(seconds * FPS, 6)))


# --- timing --------------------------------------------------------------------------------

def schedule(doc: dict, speech: dict) -> list[dict]:
    """Shots with absolute frame ranges and frame-aligned line starts."""
    shots, cursor_frame = [], 0
    for shot in doc["shots"]:
        t = LEAD_IN
        lines = []
        for n, line in enumerate(shot["lines"]):
            lid = f"{shot['id']}-l{n + 1:02d}"
            rec = speech["lines"][lid]
            start_frame = frames(t)
            lines.append({"id": lid, "line": line, "rec": rec, "from": cursor_frame + start_frame})
            pause = line.get("pause_after", DEFAULT_PAUSE)
            t = start_frame / FPS + rec["duration"] + pause
        length = max(frames(t + TAIL), frames(MIN_SHOT))
        shots.append({"shot": shot, "from": cursor_frame, "frames": length, "lines": lines})
        cursor_frame += length
    return shots


# --- staging and camera ----------------------------------------------------------------------

def _clamp_view(cx: float, cy: float, z: float) -> list[float]:
    hw, hh = WIDTH / 2 / z, HEIGHT / 2 / z
    return [round(min(max(cx, hw), WIDTH - hw), 1), round(min(max(cy, hh), HEIGHT - hh), 1), round(z, 4)]


def camera_path(move: str, intensity: str, focus_x: float) -> dict:
    """Start and end view [center x, center y, zoom]; the renderer eases between them."""
    dz, pan = INTENSITY[intensity]
    fy = HEIGHT * 0.56
    if move == "push_in":
        a, b = [WIDTH / 2, HEIGHT / 2, 1.0], [focus_x, fy, 1.0 + dz]
    elif move == "pull_out":
        a, b = [focus_x, fy, 1.0 + dz], [WIDTH / 2, HEIGHT / 2, 1.0]
    elif move in ("pan_left", "pan_right"):
        z = 1.0 / (1.0 - pan) + 0.01
        d = pan * WIDTH / 2
        a, b = [WIDTH / 2 + d, HEIGHT / 2, z], [WIDTH / 2 - d, HEIGHT / 2, z]
        if move == "pan_right":
            a, b = b, a
    elif move in ("tilt_up", "tilt_down"):
        z = 1.0 / (1.0 - pan) + 0.01
        d = pan * HEIGHT / 2
        a, b = [WIDTH / 2, HEIGHT / 2 + d, z], [WIDTH / 2, HEIGHT / 2 - d, z]
        if move == "tilt_down":
            a, b = b, a
    else:  # static: a barely perceptible drift keeps the frame alive
        a, b = [WIDTH / 2, HEIGHT / 2, 1.0], [WIDTH / 2, HEIGHT / 2, 1.01]
    return {"from": _clamp_view(*a), "to": _clamp_view(*b), "ease": "inOutQuad"}


def blink_frames(character: str, shot_id: str, length: int) -> list[int]:
    rng = random.Random(f"{character}:{shot_id}")
    out, f = [], rng.randint(20, 60)
    while f < length - 6:
        out.append(f)
        f += rng.randint(85, 150)
    return out


def mouth_track(start_frame: int, visemes: list, shot_from: int) -> list[list]:
    """Viseme keys as [frame within shot, shape]; later keys win when two land on one frame."""
    keys: dict[int, str] = {}
    for t, shape in visemes:
        keys[start_frame - shot_from + int(round(t * FPS))] = shape
    return [[f, keys[f]] for f in sorted(keys)]


def caption_pages(item: dict, speaker_label: str | None, shot_from: int, next_from: int | None) -> list[dict]:
    words = [[w["text"], item["from"] - shot_from + int(round(w["start"] * FPS)),
              item["from"] - shot_from + max(1, int(round(w["end"] * FPS)))] for w in item["rec"]["words"]]
    pages = []
    for i in range(0, len(words), CAPTION_PAGE):
        chunk = words[i:i + CAPTION_PAGE]
        end = chunk[-1][2] + frames(CAPTION_HOLD)
        if i + CAPTION_PAGE < len(words):
            end = words[i + CAPTION_PAGE][1]
        elif next_from is not None:
            end = min(end, next_from - shot_from)
        pages.append({"from": chunk[0][1], "to": end, "speaker": speaker_label, "words": chunk})
    return pages


def build(doc: dict, bible: dict, speech: dict) -> dict:
    names = {c["id"]: c["name"] for c in bible["characters"]}
    narrators = {c["id"] for c in bible["characters"] if c["kind"] == "narrator"}
    shots_out = []
    for sched in schedule(doc, speech):
        shot, sfrom, length = sched["shot"], sched["from"], sched["frames"]
        visible = shot["characters"]
        speakers = [it for it in sched["lines"] if it["line"].get("on_screen") is True]
        focus = [POSITION_X[v["position"]] * WIDTH for v in visible if v["position"] != "background"
                 and any(s["line"]["speaker"] == v["id"] for s in speakers)] or \
                [POSITION_X[v["position"]] * WIDTH for v in visible if v["position"] != "background"] or [WIDTH / 2]
        cast = []
        for v in visible:
            mouth = []
            for it in speakers:
                if it["line"]["speaker"] == v["id"]:
                    mouth += mouth_track(it["from"], it["rec"]["visemes"], sfrom)
            cast.append({"id": v["id"], "x": round(POSITION_X[v["position"]] * WIDTH, 1),
                         "depth": 0.6 if v["position"] == "background" else 1.0, "facing": v["facing"],
                         "stance": v["stance"], "mood": v["mood"], "mouth": mouth,
                         "blinks": blink_frames(v["id"], shot["id"], length)})
        captions, audio = [], []
        for k, it in enumerate(sched["lines"]):
            speaker = it["line"]["speaker"]
            nxt = sched["lines"][k + 1]["from"] if k + 1 < len(sched["lines"]) else None
            captions += caption_pages(it, None if speaker in narrators else names[speaker], sfrom, nxt)
            audio.append({"line": it["id"], "from": it["from"], "frames": frames(it["rec"]["duration"])})
        shots_out.append({
            "id": shot["id"], "from": sfrom, "frames": length, "location": shot["location"],
            "timeOfDay": shot["time_of_day"], "atmosphere": shot["atmosphere"], "ambience": shot["ambience"],
            "props": shot.get("props", []), "camera": camera_path(shot["camera"]["move"],
                                                                  shot["camera"]["intensity"], sum(focus) / len(focus)),
            "cast": cast, "captions": captions, "lines": audio,
        })
    total = shots_out[-1]["from"] + shots_out[-1]["frames"] if shots_out else 0
    return {"schema": "story-timeline/v1", "fps": FPS, "width": WIDTH, "height": HEIGHT, "durationInFrames": total,
            "series": doc["series"], "episode": doc["id"], "title": doc["title"],
            "audio": {"src": NARRATION_FILE.name}, "shots": shots_out}


# --- audio ------------------------------------------------------------------------------------

def measure(path: Path) -> tuple[float, float]:
    """Integrated loudness (LUFS) and true peak (dBTP) via ffmpeg's loudnorm analysis."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                          "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    data = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def _limit(x, ceiling_db: float):
    """Look-ahead peak limiter: 2 ms blocks, 4 ms look-ahead, ~60 ms release."""
    import numpy as np
    ceiling = 10 ** (ceiling_db / 20)
    block = 48
    n = int(math.ceil(len(x) / block))
    padded = np.zeros(n * block, dtype=np.float32)
    padded[:len(x)] = x
    peaks = np.abs(padded).reshape(n, block).max(axis=1)
    target = np.minimum(1.0, ceiling / np.maximum(peaks, 1e-9))
    ahead = np.minimum.reduce([np.roll(target, s) for s in (-2, -1, 0, 1, 2)])
    gain = np.empty(n, dtype=np.float32)
    g, release = 1.0, 1.0 / 30  # recover fully within ~30 blocks
    for i in range(n):
        g = min(ahead[i], g + release)
        gain[i] = g
    return (padded * np.repeat(gain, block))[:len(x)]


def mix(episode_dir: Path, timeline: dict, speech: dict) -> tuple[float, float]:
    """Place each line at its frame, normalize to TARGET_LUFS / TRUE_PEAK; returns measured (LUFS, dBTP)."""
    import numpy as np
    import soundfile as sf
    total = timeline["durationInFrames"] * SAMPLES_PER_FRAME
    track = np.zeros(total, dtype=np.float32)
    for shot in timeline["shots"]:
        for line in shot["lines"]:
            clip, _ = sf.read(episode_dir / "build" / speech["lines"][line["line"]]["file"], dtype="float32")
            start = line["from"] * SAMPLES_PER_FRAME
            track[start:start + len(clip)] += clip[:total - start]
    out = episode_dir / NARRATION_FILE
    # Gain toward the target, limit peaks, re-measure; tighten the limiter ceiling while true peak
    # (which includes inter-sample overs) is still too hot.
    ceiling = TRUE_PEAK - 1.5
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "probe.wav"
        sf.write(probe, track, SAMPLE_RATE, subtype="FLOAT")
        lufs, tp = measure(probe)
        for _ in range(8):
            if abs(lufs - TARGET_LUFS) <= 0.5 and tp <= TRUE_PEAK:
                break
            if tp > TRUE_PEAK and abs(lufs - TARGET_LUFS) <= 0.5:
                ceiling -= 0.5
            track = _limit(track * 10 ** ((TARGET_LUFS - lufs) / 20), ceiling)
            sf.write(probe, track, SAMPLE_RATE, subtype="FLOAT")
            lufs, tp = measure(probe)
    sf.write(out, track, SAMPLE_RATE, subtype="PCM_16")
    return measure(out)


# --- entry point --------------------------------------------------------------------------------

def load_speech(episode_dir: Path, doc: dict, bible: dict) -> dict:
    path = episode_dir / SPEECH_FILE
    if not path.is_file():
        raise StaleSpeech("no build/speech.json yet; run `story voice` first")
    speech = json.loads(path.read_text())
    version = voice.kokoro_version()
    stale = [s.id for s in line_specs(doc, bible)
             if speech["lines"].get(s.id, {}).get("digest") != s.digest(version)]
    if stale:
        raise StaleSpeech(f"speech is out of date for {', '.join(stale)}; run `story voice` first")
    return speech


def generate(episode_dir: Path, doc: dict, bible: dict, log=print) -> dict:
    speech = load_speech(episode_dir, doc, bible)
    timeline = build(doc, bible, speech)
    path = episode_dir / TIMELINE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timeline, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    lufs, tp = mix(episode_dir, timeline, speech)
    seconds = timeline["durationInFrames"] / FPS
    log(f"wrote {TIMELINE_FILE} ({len(timeline['shots'])} shots, {timeline['durationInFrames']} frames, "
        f"{seconds:.1f} s) and {NARRATION_FILE} ({lufs:.1f} LUFS, {tp:.1f} dBTP)")
    return timeline
