"""Reels: a vertical (9:16) video from a series of story cards, narrated with Kokoro.

A reel folder holds `reel.yaml` and its card images. Each slide is one image and the lines spoken over
it; the slide lasts as long as its lines (plus a breath before and after). The same machinery as the
episodes does the work: Kokoro voices with caching (build/audio, build/speech.json), frame-aligned
scheduling, the composed music bed and loudness mix (build/narration.wav), and Remotion renders
build/reel.mp4 with a slow camera move over each card.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import yaml

from . import timeline, voice

REEL_FILE = "reel.yaml"
TIMELINE_FILE = Path("build") / "reel.json"
OUTPUT_FILE = Path("build") / "reel.mp4"
SHARE_FILE = Path("build") / "reel-instagram.mp4"  # a lighter copy for uploading from a phone
WIDTH, HEIGHT = 1080, 1920
MOTIONS = ("card", "cover")
CAPTION_STYLES = ("words", "labels", "none")  # words: the spoken words, highlighted as they are said
FORMATS = ("reel", "short")  # short: kept clear of the Shorts/Reels buttons, stays on the art, captions
# Breath before and after each card's lines (seconds): a Short keeps moving.
PACING = {"reel": {"lead_in": 0.5, "tail": 1.0, "min_shot": 2.5}, "short": {"lead_in": 0.15, "tail": 0.35, "min_shot": 1.5}}
# Where the camera settles on a card (fractions of the card) and how far it zooms: the illustration
# sits in the upper-middle of these story cards, above the notes.
CARD_FOCUS = [0.5, 0.38, 1.32]
COVER_FOCUS = [0.5, 0.5, 1.08]


# Dubbed languages are voiced by Indic Parler-TTS, which runs in its own environment (see
# pipeline/parler_worker.py); one storyteller per language acts every character.
DUB_LANGS = ("hi", "te")
PARLER_PYTHON = os.environ.get("STORY_PARLER_PYTHON", str(Path.home() / "Documents/projects/tts-lab/.venv-parler/bin/python"))
PARLER_WORKER = Path(__file__).resolve().parents[1] / "parler_worker.py"
DUB_VERSION = "1"  # bump to regenerate every dubbed line
DESCRIPTION = ("{speaker} speaks in a {style} tone at a {pace} pace with a {pitch} pitch, very expressive, "
               "in a close-sounding recording with very clear audio and no background noise.")


class ReelError(Exception):
    pass


def load(folder: Path) -> dict:
    path = folder / REEL_FILE
    if not path.is_file():
        raise ReelError(f"no {REEL_FILE} in {folder}")
    reel = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = []
    if reel.get("captions", "words") not in CAPTION_STYLES:
        problems.append(f"captions must be one of {', '.join(CAPTION_STYLES)}")
    if reel.get("format", "reel") not in FORMATS:
        problems.append(f"format must be one of {', '.join(FORMATS)}")
    if reel.get("schema") != "story-reel/v1":
        problems.append("schema must be story-reel/v1")
    voices = reel.get("voices") or {}
    allowed = {v["id"] for v in json.loads((Path(__file__).resolve().parents[2] / "schemas" / "kokoro-voices.en.json").read_text())["voices"]}
    for name, v in voices.items():
        if v.get("kokoro") not in allowed:
            problems.append(f"voice '{name}' uses unknown Kokoro voice '{v.get('kokoro')}'")
    for i, slide in enumerate(reel.get("slides") or []):
        if not (folder / slide.get("image", "")).is_file():
            problems.append(f"slides[{i}]: image '{slide.get('image')}' not found")
        if slide.get("motion", "card") not in MOTIONS:
            problems.append(f"slides[{i}]: motion must be one of {', '.join(MOTIONS)}")
        if not slide.get("lines"):
            problems.append(f"slides[{i}]: needs at least one line")
        for j, line in enumerate(slide.get("lines") or []):
            if line.get("speaker") not in voices:
                problems.append(f"slides[{i}].lines[{j}]: speaker '{line.get('speaker')}' has no voice")
    for lang, dub in (reel.get("dubs") or {}).items():
        if lang not in DUB_LANGS:
            problems.append(f"dubs: language '{lang}' is not supported (use {', '.join(DUB_LANGS)})")
        for i, slide in enumerate(reel.get("slides") or []):
            for j, line in enumerate(slide.get("lines") or []):
                if not line.get(lang):
                    problems.append(f"slides[{i}].lines[{j}]: no '{lang}' text for the {lang} dub")
    if not reel.get("slides"):
        problems.append("the reel has no slides")
    if problems:
        raise ReelError("; ".join(problems))
    return reel


def _as_episode(reel: dict) -> tuple[dict, dict]:
    """The reel in the shape the voice and timeline code expect: slides as shots, voices as a cast."""
    doc = {"pronunciations": reel.get("pronunciations") or {},
           "shots": [{"id": f"s{i + 1:02d}", "lines": s["lines"]} for i, s in enumerate(reel["slides"])]}
    bible = {"characters": [{"id": k, "voice": v} for k, v in reel["voices"].items()]}
    return doc, bible


def _captions(slide: dict, scheduled: dict) -> list[dict]:
    """On-screen captions for a slide as [{at: frames from the slide's start, text}]. `caption` is one
    text for the whole slide, or a list of {line: n, text} that changes as line n starts."""
    cap = slide.get("caption")
    if not cap:
        return []
    if isinstance(cap, str):
        return [{"at": 0, "text": cap}]
    lines = scheduled["lines"]
    return [{"at": lines[min(c.get("line", 0), len(lines) - 1)]["from"] - scheduled["from"] if c.get("line", 0) else 0,
             "text": c["text"]} for c in cap]


def _dub(folder: Path, reel: dict, lang: str, log) -> dict:
    """Voice every line in `lang` with Indic Parler (cached by content); returns a speech doc whose
    files are relative to build/, like Kokoro's."""
    dub = reel["dubs"][lang]
    base = folder / "build" / f"lang-{lang}"
    speech_path = base / "speech.json"
    old = json.loads(speech_path.read_text()).get("lines", {}) if speech_path.is_file() else {}
    lines, todo = {}, []
    for i, slide in enumerate(reel["slides"]):
        for n, line in enumerate(slide["lines"]):
            lid = voice.line_id(f"s{i + 1:02d}", n)
            role = {**(dub.get("roles") or {}).get("narrator", {}), **(dub.get("roles") or {}).get(line["speaker"], {})}
            description = DESCRIPTION.format(speaker=dub["speaker"], style=line.get("mood") or role.get("style", "warm, gentle storytelling"),
                                             pace=role.get("pace", "moderate"), pitch=role.get("tone", "moderate"))
            item = {"id": lid, "text": line[lang], "description": description, "pitch": role.get("pitch", 0)}
            digest = hashlib.sha256(json.dumps([item, DUB_VERSION], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            rec = old.get(lid)
            if rec and rec.get("digest") == digest and (folder / "build" / rec["file"]).is_file():
                lines[lid] = rec
            else:
                lines[lid] = {"digest": digest, "text": line[lang], "file": f"lang-{lang}/audio/{lid}.wav"}
                todo.append(item)
    if todo:
        if not Path(PARLER_PYTHON).is_file():
            raise ReelError(f"the {lang} dub needs Indic Parler-TTS: no Python at {PARLER_PYTHON} (set STORY_PARLER_PYTHON)")
        job = base / "job.json"
        base.mkdir(parents=True, exist_ok=True)
        job.write_text(json.dumps({"lang": lang, "out_dir": str((base / "audio").resolve()), "sample_rate": voice.SAMPLE_RATE,
                                   "items": todo}, ensure_ascii=False), encoding="utf-8")
        log(f"voicing {len(todo)} {lang} line(s) with Indic Parler ({dub['speaker']}) …")
        proc = subprocess.Popen([PARLER_PYTHON, str(PARLER_WORKER), str(job)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        for out in proc.stdout:
            if out.startswith("{"):
                r = json.loads(out)
                lines[r["id"]]["duration"] = r["duration"]
                lines[r["id"]]["checked"] = r["ok"]
                log(f"  {lang} {r['id']} {r['duration']:.2f} s{'' if r['ok'] else '  (check by ear: the transcript did not match)'}")
        if proc.wait() != 0:
            raise ReelError(f"the {lang} Parler worker failed")
    speech_path.write_text(json.dumps({"lines": lines}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"lines": lines}


PAGE_CHARS = 40  # about two short lines above the card


def _balanced(words: list, limit: int = PAGE_CHARS) -> list[list]:
    """Split a line's words into the fewest pages of at most `limit` characters, as even as possible
    (so no page is left with a stranded word)."""
    text_len = lambda ws: len(" ".join(w[0] for w in ws))
    n = max(1, -(-text_len(words) // limit))
    while True:
        target = text_len(words) / n
        pages, cur = [], []
        for w in words:
            if cur and (text_len(cur + [w]) > limit or (len(pages) < n - 1 and text_len(cur) >= target)):
                pages.append(cur)
                cur = []
            cur.append(w)
        pages.append(cur)
        if len(pages) <= n or n > len(words):
            return pages
        n += 1


def _word_pages(s: dict) -> list[dict]:
    """Caption pages for a slide: the spoken words, a short page at a time, each word timed (frames
    from the slide's start). Dialogue pages carry the speaker so they can be set off in quotes."""
    fps, pages = timeline.FPS, []
    for k, ln in enumerate(s["lines"]):
        at = ln["from"] - s["from"]
        words = [[w["text"], at + round(w["start"] * fps), at + max(1, round(w["end"] * fps))] for w in ln["rec"]["words"]]
        nxt = s["lines"][k + 1]["from"] - s["from"] if k + 1 < len(s["lines"]) else None
        chunks = _balanced(words)
        speaker = ln["line"]["speaker"]
        for i, chunk in enumerate(chunks):
            end = chunks[i + 1][0][1] if i + 1 < len(chunks) else chunk[-1][2] + round(0.35 * fps)
            if nxt is not None:
                end = min(end, nxt)
            pages.append({"from": chunk[0][1], "to": end, "speaker": None if speaker == "narrator" else speaker, "words": chunk})
    return pages


def _srt(lines: list[tuple[int, float, str]]) -> str:
    """SubRip subtitles from (start frame, duration seconds, text)."""
    def ts(sec):
        ms = int(round(sec * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "\n".join(f"{n}\n{ts(f / timeline.FPS)} --> {ts(f / timeline.FPS + d)}\n{t}\n" for n, (f, d, t) in enumerate(lines, 1))


def build(folder: Path, log=print, only: str | None = None) -> dict:
    """Voice (and dub), schedule and mix the reel; copy its images into build/; write build/reel.json.

    With `only`, the reel is built for that one language at its own natural pace (English keeps its
    captions); without it, every language shares one timeline for YouTube's multi-language audio."""
    reel = load(folder)
    doc, bible = _as_episode(reel)
    pacing = {**PACING[reel.get("format", "reel")], **(reel.get("pacing") or {})}  # a story can take more breath
    langs = [only] if only else ["en", *(reel.get("dubs") or {})]
    if only and only != "en" and only not in (reel.get("dubs") or {}):
        raise ReelError(f"no '{only}' dub in {REEL_FILE}")
    speeches = {lang: voice.generate(folder, doc, bible, log=log) if lang == "en" else _dub(folder, reel, lang, log) for lang in langs}
    plans = {lang: timeline.schedule(doc, sp, **pacing) for lang, sp in speeches.items()}
    multi = len(plans) > 1
    # every language shares one picture track: each card stays up as long as its longest language needs
    lengths = [max(plans[lang][i]["frames"] for lang in plans) for i in range(len(reel["slides"]))]
    starts = [sum(lengths[:i]) for i in range(len(lengths))]
    scheduled = plans[langs[0]]
    # captions come from the English words, so they are shown only when the video's audio is English alone
    style = reel.get("captions", "words") if not multi and langs[0] == "en" else "none"
    shots = []
    for i, (slide, s) in enumerate(zip(reel["slides"], scheduled)):
        shift = starts[i] - s["from"]
        s = {**s, "from": starts[i], "frames": lengths[i], "lines": [{**ln, "from": ln["from"] + shift} for ln in s["lines"]]}
        motion = slide.get("motion", "card")
        image = f"images/{Path(slide['image']).name}"
        dest = folder / "build" / image
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(folder / slide["image"], dest)
        shots.append({"id": s["shot"]["id"], "from": s["from"], "frames": s["frames"], "image": image, "motion": motion,
                      "focus": slide.get("focus") or (COVER_FOCUS if motion == "cover" else CARD_FOCUS),
                      "captions": _captions(slide, s) if style == "labels" else [],
                      "pages": _word_pages(s) if style == "words" else [], "cast": [], "location": "card",
                      "lines": [{"line": ln["id"], "from": ln["from"]} for ln in s["lines"]]})
    total = sum(s["frames"] for s in shots)
    tl = {"schema": "story-reel-timeline/v1", "fps": timeline.FPS, "width": WIDTH, "height": HEIGHT,
          "durationInFrames": total, "episode": reel["id"], "title": reel.get("title", ""), "format": reel.get("format", "reel"),
          "audio": {"src": timeline.NARRATION_FILE.name, "music": reel.get("music", "none")}, "shots": shots}
    tracks = {}
    for lang, plan in plans.items():
        lines = [{"line": ln["id"], "from": starts[i] + ln["from"] - plan[i]["from"]} for i in range(len(plan)) for ln in plan[i]["lines"]]
        per_lang = {**tl, "shots": [{**sh, "lines": [x for x in lines if x["line"].startswith(sh["id"] + "-")]} for sh in shots]}
        lufs, tp = timeline.mix(folder, per_lang, speeches[lang])
        track = folder / "build" / f"narration-{lang}.wav"
        shutil.copyfile(folder / timeline.NARRATION_FILE, track)
        tracks[lang] = track.name
        texts = {voice.line_id(f"s{i + 1:02d}", n): (ln.get(lang) if lang != "en" else ln["text"])
                 for i, sl in enumerate(reel["slides"]) for n, ln in enumerate(sl["lines"])}
        (folder / "build" / f"subtitles-{lang}.srt").write_text(
            _srt([(x["from"], speeches[lang]["lines"][x["line"]]["duration"], texts[x["line"]]) for x in lines]), encoding="utf-8")
        log(f"{lang}: {track.name} ({lufs:.1f} LUFS, {tp:.1f} dBTP) and subtitles-{lang}.srt")
    shutil.copyfile(folder / "build" / tracks[langs[0]], folder / timeline.NARRATION_FILE)  # the video's own audio
    tl["tracks"] = tracks
    tl["only"] = only
    (folder / TIMELINE_FILE).write_text(json.dumps(tl, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    log(f"wrote {TIMELINE_FILE} ({len(shots)} slides, {total / timeline.FPS:.1f} s)")
    return tl


def render(root: Path, folder: Path, tl: dict, log=print) -> Path:
    props = folder / "build" / "reel-props.json"
    props.write_text(json.dumps({"reel": tl}), encoding="utf-8")
    only = tl.get("only")
    out = folder / (OUTPUT_FILE if not only else OUTPUT_FILE.with_name(f"reel-{only}.mp4"))
    share = folder / (SHARE_FILE if not only else SHARE_FILE.with_name(f"reel-{only}-instagram.mp4"))
    log(f"rendering reel{' (' + only + ')' if only else ''} (1080x1920) …")
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "Reel", str(out.resolve()), f"--props={props.resolve()}",
                    f"--public-dir={(folder / 'build').resolve()}", "--codec=h264", "--audio-codec=aac", "--crf=18",
                    "--overwrite", "--log=error"], cwd=root / "render", check=True)
    # Instagram re-encodes every upload (to a few Mbit/s): a ~6 Mbit/s copy looks the same there and moves easily to a phone
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-c:v", "libx264", "-preset", "slow", "-crf", "22",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(share)], check=True)
    if only:
        return out
    # dubbed languages: an Instagram-ready video each, and the audio track alone for YouTube's multi-language audio
    for lang, track in (tl.get("tracks") or {}).items():
        if lang == "en":
            continue
        wav = folder / "build" / track
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(folder / SHARE_FILE), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                        str(folder / "build" / f"reel-instagram-{lang}.mp4")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "256k",
                        str(folder / "build" / f"youtube-audio-{lang}.m4a")], check=True)
        log(f"wrote build/reel-instagram-{lang}.mp4 and build/youtube-audio-{lang}.m4a")
    return out
