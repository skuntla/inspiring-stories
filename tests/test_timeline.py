"""Timeline: frame arithmetic, mixing and loudness, camera and staging, captions, determinism."""
import json

import numpy as np
import pytest
import soundfile as sf

from story import timeline, voice
from story.timeline import (FPS, HEIGHT, WIDTH, camera_path, caption_pages, frames, measure, schedule)
from test_voice import FakeKokoro


@pytest.fixture
def voiced(project, capsys, monkeypatch):
    """The example episode voiced with the fake Kokoro."""
    monkeypatch.setattr(voice, "synthesize", FakeKokoro())
    monkeypatch.setattr(voice, "kokoro_version", lambda: "test")
    code, _, _ = project.run("voice", str(project.episode_dir), capsys=capsys)
    assert code == 0
    return project


def _timeline(project):
    return json.loads((project.episode_dir / "build" / "timeline.json").read_text())


def _speech(lines: dict) -> dict:
    return {"lines": {k: {"duration": d, "words": [], "visemes": []} for k, d in lines.items()}}


# --- durations -------------------------------------------------------------------------------

def test_frames_round_up():
    assert frames(1.0) == 30 and frames(1.001) == 31 and frames(0.5) == 15


def test_schedule_hand_computed():
    doc = {"shots": [
        {"id": "s01", "lines": [{"speaker": "n", "text": "a"}, {"speaker": "n", "text": "b", "pause_after": 1.0}]},
        {"id": "s02", "lines": [{"speaker": "n", "text": "c"}]},
    ]}
    shots = schedule(doc, _speech({"s01-l01": 2.0, "s01-l02": 1.0, "s02-l01": 0.4}))
    # s01: lead 0.5 -> l01 at frame 15; 15/30 + 2.0 + 0.35 = 2.85 -> l02 at frame 86 (ceil 85.5);
    # 86/30 + 1.0 + 1.0 = 4.8667; + tail 1.0 = 5.8667 s -> exactly 176 frames
    assert [l["from"] for l in shots[0]["lines"]] == [15, 86]
    assert shots[0]["frames"] == 176
    # s02: 0.5 + 0.4 + 0.35 + 1.0 = 2.25 s, below the 2.5 s minimum -> 75 frames, starting at 176
    assert shots[1]["from"] == 176 and shots[1]["frames"] == 75 and shots[1]["lines"][0]["from"] == 176 + 15


# --- mixing ------------------------------------------------------------------------------------

def test_lines_start_at_exact_sample_offsets_and_loudness_is_on_target(voiced, capsys):
    code, out, _ = voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    assert code == 0 and "LUFS" in out
    tl = _timeline(voiced)
    wav, sr = sf.read(voiced.episode_dir / "build" / "narration.wav", dtype="float32")
    assert sr == voice.SAMPLE_RATE and len(wav) == tl["durationInFrames"] * sr // FPS
    speech = json.loads((voiced.episode_dir / "build" / "speech.json").read_text())
    for shot in tl["shots"]:
        for line in shot["lines"]:
            offset = line["from"] * sr // FPS
            assert np.all(wav[offset - 40:offset] == 0), line
            assert abs(wav[offset]) > 0, line
            assert line["frames"] == frames(speech["lines"][line["line"]]["duration"])
    lufs, tp = measure(voiced.episode_dir / "build" / "narration.wav")
    assert -15.0 <= lufs <= -13.0 and tp <= -1.0


# --- camera and staging --------------------------------------------------------------------

@pytest.mark.parametrize("move", ["static", "push_in", "pull_out", "pan_left", "pan_right", "tilt_up", "tilt_down"])
@pytest.mark.parametrize("intensity", ["low", "medium", "high"])
def test_camera_stays_inside_the_scene(move, intensity):
    path = camera_path(move, intensity, focus_x=1700)
    for cx, cy, z in (path["from"], path["to"]):
        assert z >= 1.0
        assert WIDTH / 2 / z <= cx <= WIDTH - WIDTH / 2 / z + 0.1
        assert HEIGHT / 2 / z <= cy <= HEIGHT - HEIGHT / 2 / z + 0.1


@pytest.mark.parametrize("move, check", [
    ("push_in", lambda a, b: b[2] > a[2]),
    ("pull_out", lambda a, b: b[2] < a[2]),
    ("pan_left", lambda a, b: b[0] < a[0] and a[2] == b[2]),
    ("pan_right", lambda a, b: b[0] > a[0] and a[2] == b[2]),
    ("tilt_up", lambda a, b: b[1] < a[1]),
    ("tilt_down", lambda a, b: b[1] > a[1]),
    ("static", lambda a, b: abs(b[2] - a[2]) <= 0.011 and a[:2] == b[:2]),
])
def test_camera_moves_in_the_right_direction(move, check):
    path = camera_path(move, "medium", focus_x=960)
    assert check(path["from"], path["to"])


def test_intensity_scales_the_move():
    low, high = camera_path("push_in", "low", 960), camera_path("push_in", "high", 960)
    assert high["to"][2] - high["from"][2] > low["to"][2] - low["from"][2]


def test_staging_and_mouths(voiced, capsys):
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    shots = {s["id"]: s for s in _timeline(voiced)["shots"]}
    s05 = {c["id"]: c for c in shots["s05"]["cast"]}
    assert s05["pip"]["x"] == pytest.approx(0.18 * WIDTH, abs=0.1) and s05["bramble"]["x"] == pytest.approx(0.82 * WIDTH, abs=0.1)
    assert s05["pip"]["mouth"] and s05["bramble"]["mouth"]          # both speak on screen
    assert {c["id"]: c["depth"] for c in shots["s06"]["cast"]}["wren"] == 0.6   # background
    assert all(c["blinks"] == sorted(c["blinks"]) for c in shots["s06"]["cast"])


def test_off_screen_speaker_gets_no_mouth_but_a_label(voiced, capsys):
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    s03 = next(s for s in _timeline(voiced)["shots"] if s["id"] == "s03")   # Wren calls from off screen
    assert all(c["mouth"] == [] for c in s03["cast"])
    assert s03["captions"][0]["speaker"] == "Wren"


def test_narration_captions_have_no_label(voiced, capsys):
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    s01 = _timeline(voiced)["shots"][0]
    assert s01["captions"] and all(p["speaker"] is None for p in s01["captions"])


def test_caption_pages_hold_at_most_seven_words():
    item = {"from": 100, "rec": {"words": [{"text": f"w{i}", "start": i * 0.3, "end": i * 0.3 + 0.25}
                                           for i in range(16)]}}
    pages = caption_pages(item, "Pip", shot_from=100, next_from=None)
    assert [len(p["words"]) for p in pages] == [7, 7, 2]
    assert pages[0]["to"] == pages[1]["from"]              # pages hand over without a gap
    assert all(p["speaker"] == "Pip" for p in pages)


# --- determinism and stale speech -----------------------------------------------------------

def test_timeline_is_byte_identical(voiced, capsys):
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    first = (voiced.episode_dir / "build" / "timeline.json").read_bytes()
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    assert (voiced.episode_dir / "build" / "timeline.json").read_bytes() == first


def test_stale_speech_is_refused(voiced, capsys):
    doc = voiced.episode()
    doc["shots"][0]["lines"][0]["text"] = "A different first line."
    voiced.write_episode(doc)
    code, _, err = voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    assert code == 1 and "s01-l01" in err and "story voice" in err


def test_missing_speech_is_refused(project, capsys):
    code, _, err = project.run("timeline", str(project.episode_dir), capsys=capsys)
    assert code == 1 and "run `story voice` first" in err
