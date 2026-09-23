"""Timeline: turn a locked episode plus its measured speech into one frame-exact description of
the video (build/timeline.json) and the mixed soundtrack (build/narration.wav: the voices, plus
the episode's background music when it has any).

All timing, staging and camera decisions happen here; the renderer only draws.
"""
from __future__ import annotations

import json
import math
import random
import subprocess
import tempfile
from pathlib import Path

from . import music, voice
from .voice import SAMPLE_RATE, SPEECH_FILE, line_specs

FPS = 30
WIDTH, HEIGHT = 1920, 1080
LEAD_IN = 0.5
DEFAULT_PAUSE = 0.35
TAIL = 1.0
MIN_SHOT = 2.5
CAPTION_CHARS = 42         # a caption page fits two short lines on a phone
CAPTION_HOLD = 0.3          # seconds a caption page stays after its last word
TARGET_LUFS = -14.0
TRUE_PEAK = -1.0
TIMELINE_FILE = Path("build") / "timeline.json"
NARRATION_FILE = Path("build") / "narration.wav"

POSITION_X = {"left": 0.18, "center_left": 0.35, "center": 0.5, "center_right": 0.65, "right": 0.82,
              "background": 0.5}
INTENSITY = {"low": (0.06, 0.06), "medium": (0.12, 0.12), "high": (0.20, 0.20)}  # (zoom delta, pan fraction)
SAMPLES_PER_FRAME = SAMPLE_RATE // FPS  # 800
WALK_SPEED = 100.0      # px/s at depth 1 for a neutral walk of a ~470 px tall character
# Walk energy follows mood: brisk when happy, slow and relaxed when calm or low.
WALK_ENERGY = {"happy": 1.25, "angry": 1.2, "scared": 1.25, "worried": 1.1, "proud": 1.0, "neutral": 1.0,
               "surprised": 1.0, "thoughtful": 0.8, "calm": 0.72, "tired": 0.7, "sad": 0.7}
MAX_TRAVEL = 900.0      # px a walker may cross in one shot
SCENE_MARGIN = 160.0    # keep walkers this far inside the scene edges


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


def camera_path(move: str, intensity: str, focus_x: float, framing: str = "wide") -> dict:
    """Start and end view as offsets [dx, dy, zoom factor] from the shot's base view.

    The base view is the whole scene for wide shots (center 960,540, zoom 1) and the subject's
    face for medium and close shots, which the renderer frames from the rig and location. Wide
    moves are the same as before, just stored relative to the scene center; framed moves stay
    small so the subject stays in frame.
    """
    if framing != "wide":
        dz, pan = INTENSITY[intensity]
        moves = {"push_in": ([0, 0, 1.0], [0, 0, 1.0 + dz]), "pull_out": ([0, 0, 1.0 + dz], [0, 0, 1.0]),
                 "pan_left": ([pan * 200, 0, 1.0], [-pan * 200, 0, 1.0]), "pan_right": ([-pan * 200, 0, 1.0], [pan * 200, 0, 1.0]),
                 "tilt_up": ([0, pan * 120, 1.0], [0, -pan * 120, 1.0]), "tilt_down": ([0, -pan * 120, 1.0], [0, pan * 120, 1.0])}
        a, b = moves.get(move, ([0, 0, 1.0], [0, 0, 1.02]))
        return {"framing": framing, "from": [round(v, 4) for v in a], "to": [round(v, 4) for v in b], "ease": "inOutQuad"}
    absolute = _wide_path(move, intensity, focus_x)
    rel = lambda v: [round(v[0] - WIDTH / 2, 1), round(v[1] - HEIGHT / 2, 1), v[2]]  # noqa: E731
    return {"framing": "wide", "from": rel(absolute["from"]), "to": rel(absolute["to"]), "ease": "inOutQuad"}


def _wide_path(move: str, intensity: str, focus_x: float) -> dict:
    """Absolute start and end views for a wide shot, clamped to the scene."""
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
    return {"from": _clamp_view(*a), "to": _clamp_view(*b)}


def walk_travel(x: float, facing: str, stance: str, frames_: int, depth: float, mood: str = "neutral") -> dict | None:
    """Start/end x and speed for a character walking left or right, centered on its position."""
    if stance != "walk" or facing not in ("left", "right"):
        return None
    seconds = frames_ / FPS
    distance = min(WALK_SPEED * WALK_ENERGY.get(mood, 1.0) * depth * seconds, MAX_TRAVEL * depth)
    direction = 1 if facing == "right" else -1
    x0, x1 = x - direction * distance / 2, x + direction * distance / 2
    lo, hi = SCENE_MARGIN, WIDTH - SCENE_MARGIN
    shift = max(0.0, lo - min(x0, x1)) - max(0.0, max(x0, x1) - hi)
    x0, x1 = x0 + shift, x1 + shift
    return {"from": round(x0, 1), "to": round(x1, 1), "speed": round(abs(x1 - x0) / seconds, 2)}


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
    chunks, current = [], []
    for w in words:
        if current and len(" ".join(x[0] for x in current + [w])) > CAPTION_CHARS:
            chunks.append(current)
            current = []
        current.append(w)
    if current:
        chunks.append(current)
    pages = []
    for i, chunk in enumerate(chunks):
        end = chunk[-1][2] + frames(CAPTION_HOLD)
        if i + 1 < len(chunks):
            end = chunks[i + 1][0][1]
        elif next_from is not None:
            end = min(end, next_from - shot_from)
        pages.append({"from": chunk[0][1], "to": end, "speaker": speaker_label, "words": chunk})
    return pages


def _camera(shot: dict, cast: list[dict], speakers: list[dict], focus_x: float) -> dict:
    """Camera path plus, for medium and close shots, the subject it frames."""
    cam = shot["camera"]
    framing = cam.get("framing", "wide")
    path = camera_path(cam["move"], cam["intensity"], focus_x, framing)
    if framing != "wide":
        on_screen = [it["line"]["speaker"] for it in speakers]
        subject = cam.get("subject") or next((c for c in on_screen if any(m["id"] == c for m in cast)), None) \
            or cast[0]["id"]
        member = next(m for m in cast if m["id"] == subject)
        path["subject"] = {"id": subject, "x": member["x"], "depth": member["depth"], "facing": member["facing"]}
    return path


def build(doc: dict, bible: dict, speech: dict) -> dict:
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
            x = round(POSITION_X[v["position"]] * WIDTH, 1)
            depth = 0.6 if v["position"] == "background" else 1.0
            member = {"id": v["id"], "x": x, "depth": depth, "facing": v["facing"],
                      "stance": v["stance"], "mood": v["mood"], "mouth": mouth,
                      "blinks": blink_frames(v["id"], shot["id"], length)}
            travel = walk_travel(x, v["facing"], v["stance"], length, depth, v["mood"])
            if travel:
                member["travel"] = travel
            cast.append(member)
        captions, audio = [], []
        for k, it in enumerate(sched["lines"]):
            speaker = it["line"]["speaker"]
            nxt = sched["lines"][k + 1]["from"] if k + 1 < len(sched["lines"]) else None
            captions += caption_pages(it, None if speaker in narrators else speaker, sfrom, nxt)
            audio.append({"line": it["id"], "from": it["from"], "frames": frames(it["rec"]["duration"])})
        shots_out.append({
            "id": shot["id"], "from": sfrom, "frames": length, "location": shot["location"],
            "timeOfDay": shot["time_of_day"], "atmosphere": shot["atmosphere"], "ambience": shot["ambience"],
            "props": shot.get("props", []), "camera": _camera(shot, cast, speakers, sum(focus) / len(focus)),
            "cast": cast, "captions": captions, "lines": audio,
        })
    total = shots_out[-1]["from"] + shots_out[-1]["frames"] if shots_out else 0
    return {"schema": "story-timeline/v1", "fps": FPS, "width": WIDTH, "height": HEIGHT, "durationInFrames": total,
            "series": doc["series"], "episode": doc["id"], "title": doc["title"],
            "audio": {"src": NARRATION_FILE.name, "music": doc.get("music", "none")}, "shots": shots_out}


# --- audio ------------------------------------------------------------------------------------

def measure(path: Path) -> tuple[float, float]:
    """Integrated loudness (LUFS) and true peak (dBTP) via ffmpeg's loudnorm analysis."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                          "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    data = json.loads(out[out.rindex("{"):out.rindex("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def _true_peaks(x, factor: int = 4):
    """Per-sample peak including the overshoot between samples: the signal upsampled `factor` times."""
    import numpy as np
    n = len(x)
    spectrum = np.fft.rfft(x)
    up = np.fft.irfft(spectrum, n * factor) * factor
    return np.abs(up).reshape(n, factor).max(axis=1)


def _limit(x, ceiling_db: float):
    """Look-ahead true-peak limiter: 2 ms blocks, 4 ms look-ahead, ~60 ms release, gain interpolated
    per sample (a stepped gain would itself create peaks between samples)."""
    import numpy as np
    ceiling = 10 ** (ceiling_db / 20)
    block = 48
    n = int(math.ceil(len(x) / block))
    padded = np.zeros(n * block, dtype=np.float32)
    padded[:len(x)] = x
    peaks = _true_peaks(padded).reshape(n, block).max(axis=1)
    target = np.minimum(1.0, ceiling / np.maximum(peaks, 1e-9))
    ahead = np.minimum.reduce([np.roll(target, s) for s in (-2, -1, 0, 1, 2)])
    gain = np.empty(n, dtype=np.float32)
    g, release = 1.0, 1.0 / 30  # recover fully within ~30 blocks
    for i in range(n):
        g = min(ahead[i], g + release)
        gain[i] = g
    centers = np.arange(n) * block + block / 2
    smooth = np.interp(np.arange(n * block), centers, gain)
    return (padded * smooth)[:len(x)].astype(np.float32)


def mix(episode_dir: Path, timeline: dict, speech: dict) -> tuple[float, float]:
    """Place each line at its frame, lay the music bed under it, normalize to TARGET_LUFS / TRUE_PEAK;
    returns measured (LUFS, dBTP)."""
    import numpy as np
    import soundfile as sf
    total = timeline["durationInFrames"] * SAMPLES_PER_FRAME
    track = np.zeros(total, dtype=np.float32)
    for shot in timeline["shots"]:
        for line in shot["lines"]:
            clip, _ = sf.read(episode_dir / "build" / speech["lines"][line["line"]]["file"], dtype="float32")
            start = line["from"] * SAMPLES_PER_FRAME
            track[start:start + len(clip)] += clip[:total - start]
    track = track + music.compose(timeline, track, SAMPLE_RATE, timeline["audio"].get("music", "none"))
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
