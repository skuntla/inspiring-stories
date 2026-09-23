"""Narration: viseme rules, word alignment, and `story voice` with Kokoro mocked."""
import json

import numpy as np
import pytest

from story import voice
from story.voice import (align_words, line_id, line_visemes, spoken_pieces, word_visemes)


# --- pure functions ------------------------------------------------------------------

@pytest.mark.parametrize("phoneme, shape", [
    ("m", "closed"), ("b", "closed"), ("p", "closed"), ("f", "fv"), ("v", "fv"),
    ("i", "ee"), ("ɪ", "ee"), ("ɛ", "mid"), ("ə", "mid"), ("ɑ", "open"), ("I", "open"),
    ("o", "round"), ("u", "round"), ("w", "round"), ("t", "consonant"), ("s", "consonant"), ("ð", "consonant"),
])
def test_each_viseme_class(phoneme, shape):
    assert word_visemes(phoneme, 0.0, 0.2) == [(0.0, shape)]


def test_bilabial_opens_word_closed():
    keys = word_visemes("bɹˈɛkfəst", 1.0, 1.8)
    assert keys[0] == (1.0, "closed")
    assert [s for _, s in keys] == ["closed", "consonant", "mid", "consonant", "fv", "mid", "consonant", "consonant"]


def test_vowels_get_more_time():
    keys = word_visemes("ta", 0.0, 1.0)   # consonant weight 1.0, vowel 1.6
    assert keys[1][0] == pytest.approx(1.0 / 2.6, abs=0.001)


def test_line_visemes_are_ordered_and_joined():
    words = [{"start": 0.0, "end": 0.3, "phonemes": "bi"},
             {"start": 0.33, "end": 0.6, "phonemes": "tu"},      # starts within 60 ms: no rest between
             {"start": 1.0, "end": 1.2, "phonemes": "mi"}]       # after a pause: rest stays
    keys = line_visemes(words)
    times = [t for t, _ in keys]
    assert times == sorted(times)
    assert (0.3, "rest") not in keys
    assert (0.6, "rest") in keys and keys[-1] == (1.2, "rest")
    shapes = [s for _, s in keys]
    assert all(a != b for a, b in zip(shapes, shapes[1:]))   # repeats collapsed


def test_line_id():
    assert line_id("s03", 1) == "s03-l02"


def test_spoken_pieces_replace_core_word_only():
    assert spoken_pieces("Zephyrine smiled, “Zephyrine!”", {"Zephyrine": "ZEF-ih-reen"}) == [
        ("Zephyrine", "ZEF-ih-reen"), ("smiled,", "smiled,"), ("“Zephyrine!”", "“ZEF-ih-reen!”")]


def test_align_words_groups_multi_token_spoken_forms():
    pieces = [("Zephyrine", "ZEF-ih-reen"), ("smiled.", "smiled.")]
    tokens = [{"text": "ZEF", "phonemes": "zɛf", "start": 0.1, "end": 0.3},
              {"text": "-", "phonemes": None, "start": 0.3, "end": 0.3},
              {"text": "ih", "phonemes": "ɪ", "start": 0.3, "end": 0.4},
              {"text": "-", "phonemes": None, "start": 0.4, "end": 0.4},
              {"text": "reen", "phonemes": "ɹin", "start": 0.4, "end": 0.7},
              {"text": "smiled", "phonemes": "smIld", "start": 0.7, "end": 1.1},
              {"text": ".", "phonemes": ".", "start": 1.1, "end": 1.2}]
    words = align_words(pieces, tokens)
    assert [(w["text"], w["start"], w["end"]) for w in words] == [("Zephyrine", 0.1, 0.7), ("smiled.", 0.7, 1.1)]


# --- story voice with Kokoro mocked -------------------------------------------------------

class FakeKokoro:
    """Each word lasts 0.3 s after 0.25 s of leading silence; records every call."""

    def __init__(self):
        self.calls = []

    def __call__(self, text, voice_id, speed):
        self.calls.append((text, voice_id, speed))
        tokens, t = [], 0.25
        for word in text.split():
            core = word.strip(".,!?;:\"'“”")
            tokens.append({"text": core, "phonemes": "bi", "start": t, "end": t + 0.3})
            t += 0.3
        n = int((t + 0.4) * voice.SAMPLE_RATE)
        # a 220 Hz tone with a tiny offset: measurable loudness, and the first sample is never zero
        audio = 0.02 + 0.2 * np.sin(2 * np.pi * 220 * np.arange(n) / voice.SAMPLE_RATE)
        return audio.astype(np.float32), tokens


@pytest.fixture
def fake(monkeypatch):
    f = FakeKokoro()
    monkeypatch.setattr(voice, "synthesize", f)
    monkeypatch.setattr(voice, "kokoro_version", lambda: "test")
    return f


def _speech(project):
    return json.loads((project.episode_dir / "build" / "speech.json").read_text())


def test_voice_uses_bible_voice_and_speed(project, capsys, fake):
    code, _, _ = project.run("voice", str(project.episode_dir), capsys=capsys)
    assert code == 0
    speech = _speech(project)["lines"]
    total_lines = sum(len(s["lines"]) for s in project.episode()["shots"])
    assert len(speech) == total_lines == len(fake.calls)
    bramble = speech["s05-l01"]
    assert (bramble["voice"], bramble["speed"]) == ("bm_george", 0.9)
    assert (project.episode_dir / "build" / "audio" / "s05-l01.wav").is_file()


def test_leading_silence_is_trimmed(project, capsys, fake):
    project.run("voice", str(project.episode_dir), capsys=capsys)
    first_word = _speech(project)["lines"]["s01-l01"]["words"][0]
    assert first_word["start"] == pytest.approx(voice.LEAD_TRIM, abs=0.001)


def test_pronunciation_changes_spoken_text_only(project, capsys, fake):
    project.run("voice", str(project.episode_dir), capsys=capsys)
    line = _speech(project)["lines"]["s01-l01"]
    assert "THISS-ul-wick" in line["spoken"] and "Thistlewick" not in line["spoken"]
    assert "Thistlewick" in [w["text"] for w in line["words"]]
    assert any("THISS-ul-wick" in text for text, _, _ in fake.calls)


def test_visemes_are_recorded(project, capsys, fake):
    project.run("voice", str(project.episode_dir), capsys=capsys)
    keys = _speech(project)["lines"]["s02-l01"]["visemes"]
    assert keys[0][1] == "closed" and keys[-1][1] == "rest"
    assert [t for t, _ in keys] == sorted(t for t, _ in keys)


def test_cache_regenerates_only_changed_lines(project, capsys, fake):
    project.run("voice", str(project.episode_dir), capsys=capsys)
    fake.calls.clear()
    project.run("voice", str(project.episode_dir), capsys=capsys)
    assert fake.calls == []
    doc = project.episode()
    doc["shots"][2]["lines"][0]["text"] = "Pip! Old Bramble needs your light tonight!"
    project.write_episode(doc)
    project.run("voice", str(project.episode_dir), capsys=capsys)
    assert [c[0] for c in fake.calls] == ["Pip! Old Bramble needs your light tonight!"]
    fake.calls.clear()
    project.run("voice", str(project.episode_dir), "--force", capsys=capsys)
    assert len(fake.calls) == len(_speech(project)["lines"])


def test_missing_kokoro_is_actionable(project, capsys, monkeypatch):
    def unavailable(*_):
        raise voice.VoiceUnavailable(f"Kokoro is not installed (kokoro); install it with: {voice.VOICE_INSTALL}")
    monkeypatch.setattr(voice, "synthesize", unavailable)
    code, _, err = project.run("voice", str(project.episode_dir), capsys=capsys)
    assert code == 1 and ".[voice]" in err


def test_invalid_episode_produces_nothing(project, capsys, fake):
    doc = project.episode()
    doc["shots"][0]["camera"]["move"] = "dolly_zoom"
    project.write_episode(doc)
    code, _, err = project.run("voice", str(project.episode_dir), capsys=capsys)
    assert code == 1 and "nothing was produced" in err and fake.calls == []
