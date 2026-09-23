"""Series bible rules: the golden series is clean, and each mutation trips exactly its rule."""
import pytest

from conftest import rules
from story.lint_series import check_series


def _check(project):
    return check_series(project.series_dir, project.root)


def test_golden_series_is_clean(project):
    assert _check(project).findings == []


def _set_id(d):
    d["id"] = "examplemeadow"


def _dup_id(d):
    d["characters"][2]["id"] = "pip"


def _no_narrator(d):
    d["characters"] = [c for c in d["characters"] if c["kind"] != "narrator"]


def _two_narrators(d):
    d["characters"][1] = {"id": "second", "kind": "narrator", "name": "Two", "voice": {"kokoro": "af_heart", "speed": 1}}


def _narrator_outfit(d):
    d["characters"][0]["outfit"] = "a cloak"


def _character_without_outfit(d):
    del d["characters"][1]["outfit"]


def _bad_voice(d):
    d["characters"][1]["voice"]["kokoro"] = "zf_xiaobei"


def _fast_voice(d):
    d["characters"][1]["voice"]["speed"] = 2.5


def _unknown_field(d):
    d["characters"][1]["hair_colour_hex"] = "#aa7744"


def _style_references(d):
    d["style"]["references"] = ["style/ref-01.png"]


def _character_references(d):
    d["characters"][1]["references"] = {"front": "characters/pip/ref-front.png"}


def _location_references(d):
    _with_location(d)
    d["locations"][0]["references"] = ["locations/meadow-path/ref-01.png"]


def _empty_style(d):
    d["style"]["description"] = "   "


def _wrong_rating(d):
    d["content_rating"] = "teen"


def _with_location(doc, lid="meadow-path"):
    doc.setdefault("locations", []).append({"id": lid, "description": "A pale-earth path through tall grass."})
    return doc


def _dup_location(d):
    _with_location(d)
    _with_location(d)


def _location_collides_with_character(d):
    _with_location(d, lid="pip")


def _location_time_of_day(d):
    _with_location(d)
    d["locations"][0]["time_of_day"] = "dusk"


@pytest.mark.parametrize("mutate, rule, path", [
    (_set_id, "series.id-matches-folder", "id"),
    (_dup_id, "series.duplicate-id", "characters[2].id"),
    (_no_narrator, "series.one-narrator", "characters"),
    (_two_narrators, "series.one-narrator", "characters"),
    (_narrator_outfit, "series.narrator-visual", "characters[0].outfit"),
    (_character_without_outfit, "series.character-visual", "characters[1].outfit"),
    (_bad_voice, "series.voice-allowlist", "characters[1].voice.kokoro"),
    (_fast_voice, "schema.range", "characters[1].voice.speed"),
    (_unknown_field, "schema.unknown-field", "characters[1].hair_colour_hex"),
    (_style_references, "schema.unknown-field", "style.references"),
    (_character_references, "schema.unknown-field", "characters[1].references"),
    (_location_references, "schema.unknown-field", "locations[0].references"),
    (_empty_style, "schema.pattern", "style.description"),
    (_wrong_rating, "schema.const", "content_rating"),
    (_dup_location, "series.duplicate-location", "locations[1].id"),
    (_location_collides_with_character, "series.location-id-collision", "locations[0].id"),
    (_location_time_of_day, "schema.unknown-field", "locations[0].time_of_day"),
])
def test_each_rule(project, mutate, rule, path):
    doc = project.series()
    mutate(doc)
    project.write_series(doc)
    errors = [f for f in _check(project).findings if f.severity == "error"]
    assert (rule, path) in {(f.rule, f.path) for f in errors}, errors


def test_folder_mismatch_message_names_both(project):
    doc = project.series()
    _set_id(doc)
    project.write_series(doc)
    msg = next(f.message for f in _check(project).findings if f.rule == "series.id-matches-folder")
    assert "examplemeadow" in msg and "example-meadow" in msg


def test_voice_error_lists_allowed_voices(project):
    doc = project.series()
    _bad_voice(doc)
    project.write_series(doc)
    msg = next(f.message for f in _check(project).findings if f.rule == "series.voice-allowlist")
    assert "af_heart" in msg and "bm_george" in msg


def test_unsupported_version_stops_further_checks(project):
    doc = project.series()
    doc["schema"] = "story-series/v2"
    doc["id"] = "wrong"
    project.write_series(doc)
    findings = _check(project).findings
    assert [f.rule for f in findings] == ["schema.version"]


def test_audience_and_made_for_kids_default_are_valid(project):
    doc = project.series()
    doc["audience"] = "General audience of all ages."
    doc["defaults"] = {"made_for_kids": False}
    project.write_series(doc)
    assert rules(_check(project).findings, "error") == set()


def test_non_boolean_default_is_a_type_error(project):
    doc = project.series()
    doc["defaults"] = {"made_for_kids": "no"}
    project.write_series(doc)
    errors = {(f.rule, f.path) for f in _check(project).findings if f.severity == "error"}
    assert ("schema.type", "defaults.made_for_kids") in errors


def test_recurring_location_is_valid(project):
    project.write_series(_with_location(project.series()))
    assert _check(project).findings == []
