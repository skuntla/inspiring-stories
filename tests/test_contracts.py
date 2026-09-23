import json
import re

import pytest
from jsonschema import Draft202012Validator

from conftest import REPO

SCHEMAS = ["vocabulary.v1.json", "story-series.v1.schema.json", "story-episode.v1.schema.json"]


@pytest.mark.parametrize("name", SCHEMAS)
def test_schema_files_are_valid_json_schema(name):
    Draft202012Validator.check_schema(json.loads((REPO / "schemas" / name).read_text()))


def test_voice_allowlist_ids_are_english_presets_without_duplicates():
    voices = json.loads((REPO / "schemas" / "kokoro-voices.en.json").read_text())["voices"]
    ids = [v["id"] for v in voices]
    assert ids and len(ids) == len(set(ids))
    for voice in voices:
        assert re.fullmatch(r"[ab][fm]_[a-z]+", voice["id"])
        assert voice["accent"] == {"a": "american", "b": "british"}[voice["id"][0]]
        assert voice["gender"] == {"f": "female", "m": "male"}[voice["id"][1]]


def test_vocabulary_matches_design():
    vocab = json.loads((REPO / "schemas" / "vocabulary.v1.json").read_text())["$defs"]
    assert vocab["cameraMove"]["enum"] == ["static", "push_in", "pull_out", "pan_left", "pan_right", "tilt_up", "tilt_down"]
    assert vocab["facing"]["enum"] == ["left", "right", "camera", "away"]
    assert set(vocab) == {"cameraMove", "cameraIntensity", "atmosphere", "ambience", "delivery", "position", "facing",
                          "timeOfDay", "stance", "mood"}
    assert "perch" in vocab["stance"]["enum"] and "thoughtful" in vocab["mood"]["enum"]
