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


# recurring locations and expression sheets -------------------------------------------

def _with_location(doc, lid="meadow-path", refs=None):
    doc.setdefault("locations", []).append({
        "id": lid, "description": "A pale-earth path through tall grass.",
        "references": refs if refs is not None else [f"locations/{lid}/ref-01.png"],
    })
    return doc


def test_recurring_location_is_valid(project):
    project.write_series(_with_location(project.series()))
    result = _check(project)
    assert rules(result.findings, "error") == set()
    assert "locations[0].references[0]" in {f.path for f in result.findings if f.rule == "series.reference-missing"}


def test_expression_sheet_is_valid_and_presence_checked(project):
    doc = project.series()
    doc["characters"][1]["references"]["expressions"] = "characters/pip/expressions.png"
    project.write_series(doc)
    result = _check(project)
    assert rules(result.findings, "error") == set()
    assert "characters[1].references.expressions" in {
        f.path for f in result.findings if f.rule == "series.reference-missing"}


def _dup_location(d):
    _with_location(d)
    _with_location(d)


def _location_collides_with_character(d):
    _with_location(d, lid="pip", refs=["locations/pip/ref-01.png"])


def _location_ref_outside(d):
    _with_location(d, refs=["characters/pip/ref-front.png"])


def _too_many_location_refs(d):
    _with_location(d, refs=[f"locations/meadow-path/ref-0{i}.png" for i in range(1, 5)])


def _expressions_outside(d):
    d["characters"][1]["references"]["expressions"] = "style/ref-01.png"


def _narrator_expressions(d):
    d["characters"][0]["references"] = {"front": "a.png", "three_quarter": "b.png", "side": "c.png",
                                        "expressions": "characters/narrator/expressions.png"}


def _location_unknown_field(d):
    _with_location(d)
    d["locations"][0]["time_of_day"] = "dusk"


@pytest.mark.parametrize("mutate, rule, path", [
    (_dup_location, "series.duplicate-location", "locations[1].id"),
    (_location_collides_with_character, "series.location-id-collision", "locations[0].id"),
    (_location_ref_outside, "series.reference-location", "locations[0].references[0]"),
    (_too_many_location_refs, "schema.max-items", "locations[0].references"),
    (_expressions_outside, "series.reference-location", "characters[1].references.expressions"),
    (_narrator_expressions, "series.narrator-visual", "characters[0].references"),
    (_location_unknown_field, "schema.unknown-field", "locations[0].time_of_day"),
])
def test_location_and_expression_rules(project, mutate, rule, path):
    doc = project.series()
    mutate(doc)
    project.write_series(doc)
    errors = [f for f in _check(project).findings if f.severity == "error"]
    assert (rule, path) in {(f.rule, f.path) for f in errors}, errors
