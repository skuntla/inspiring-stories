"""Series bible rules: the golden series is clean, and each mutation trips exactly its rule."""
import shutil

import pytest

from conftest import rules
from story.lint_series import check_series


def _check(project):
    return check_series(project.series_dir, project.root)


def test_golden_series_has_no_errors_only_missing_image_warnings(project):
    result = _check(project)
    assert rules(result.findings, "error") == set()
    assert rules(result.findings, "warning") == {"series.reference-missing"}


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


def _style_ref_outside(d):
    d["style"]["references"] = ["characters/pip/ref-front.png"]


def _char_ref_outside(d):
    d["characters"][1]["references"]["front"] = "characters/bramble/ref-front.png"


def _empty_style(d):
    d["style"]["description"] = "   "


def _wrong_rating(d):
    d["content_rating"] = "teen"


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
    (_style_ref_outside, "series.reference-location", "style.references[0]"),
    (_char_ref_outside, "series.reference-location", "characters[1].references.front"),
    (_empty_style, "schema.pattern", "style.description"),
    (_wrong_rating, "schema.const", "content_rating"),
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


def test_present_reference_image_is_not_warned(project):
    ref = project.series_dir / "characters" / "pip" / "ref-front.png"
    ref.parent.mkdir(parents=True)
    ref.write_bytes(b"png")
    warned = {f.path for f in _check(project).findings if f.rule == "series.reference-missing"}
    assert "characters[1].references.front" not in warned
    assert "characters[1].references.side" in warned


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
