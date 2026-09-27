import pytest
import yaml

from story import reel


def _reel(tmp_path, **over):
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "a.png").write_bytes(b"png")
    doc = {"schema": "story-reel/v1", "id": "day-1", "voices": {"narrator": {"kokoro": "af_heart", "speed": 0.95}},
           "slides": [{"image": "images/a.png", "lines": [{"speaker": "narrator", "text": "Once."}]}]}
    doc.update(over)
    (tmp_path / "reel.yaml").write_text(yaml.safe_dump(doc))
    return tmp_path


def test_valid_reel_loads(tmp_path):
    assert reel.load(_reel(tmp_path))["id"] == "day-1"


@pytest.mark.parametrize("over, needle", [
    ({"voices": {"narrator": {"kokoro": "xx_nobody", "speed": 1}}}, "unknown Kokoro voice"),
    ({"slides": [{"image": "images/missing.png", "lines": [{"speaker": "narrator", "text": "x"}]}]}, "not found"),
    ({"slides": [{"image": "images/a.png", "lines": [{"speaker": "hanuman", "text": "x"}]}]}, "has no voice"),
    ({"slides": [{"image": "images/a.png", "motion": "spin", "lines": [{"speaker": "narrator", "text": "x"}]}]}, "motion"),
])
def test_problems_are_named(tmp_path, over, needle):
    with pytest.raises(reel.ReelError, match=needle):
        reel.load(_reel(tmp_path, **over))


def test_slides_become_shots_and_voices_a_cast(tmp_path):
    doc, bible = reel._as_episode(reel.load(_reel(tmp_path)))
    assert doc["shots"][0]["id"] == "s01" and bible["characters"][0]["id"] == "narrator"


def test_caption_pages_are_balanced_without_stranded_words():
    words = [[w, 0, 0] for w in "It was early morning in the forest. Little Hanuman opened his eyes… and his tummy rumbled.".split()]
    pages = reel._balanced(words)
    lengths = [len(" ".join(w[0] for w in p)) for p in pages]
    assert all(n <= reel.PAGE_CHARS for n in lengths)
    assert min(lengths) >= 12  # no lone word left on a page of its own
    assert [w for p in pages for w in p] == words
