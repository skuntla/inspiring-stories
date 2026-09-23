"""Episode manifest rules: the golden episode is clean, and each mutation trips its rule."""
import copy

import pytest

from conftest import EPISODE_ID, rules
from story.lint_episode import check_episode


def _check(project, expected=EPISODE_ID):
    return check_episode(project.episode_dir / "episode.yaml", project.root, expected)


def _episode_findings(result):
    return [f for f in result.findings if f.file.endswith("episode.yaml")]


def test_golden_episode_is_clean(project):
    result = _check(project)
    assert _episode_findings(result) == []


# --- one mutation per rule ---------------------------------------------------

def _unknown_series(d): d["series"] = "moonlit-tales"
def _wrong_id(d): d["id"] = "2026-01-02-the-lantern-seed"
def _bad_id_format(d): d["id"] = "the-lantern-seed"
def _owl_in_cast(d): d["cast"].append("owl")
def _undeclared_location(d): d["shots"][0]["location"] = "river-bank"
def _undeclared_prop(d): d["shots"][1]["props"] = ["golden-key"]
def _dup_location(d): d["locations"].append(copy.deepcopy(d["locations"][0]))
def _shot_gap(d): d["shots"][2]["id"] = "s04"
def _visible_not_in_cast(d):
    d["cast"].remove("wren")
    d["shots"][2]["lines"][0]["speaker"] = "narrator"
    del d["shots"][2]["lines"][0]["on_screen"]
def _narrator_visible(d): d["shots"][0]["characters"].append({"id": "narrator", "position": "left", "pose": "p", "expression": "e", "facing": "camera"})
def _duplicate_visible(d): d["shots"][0]["characters"].append(copy.deepcopy(d["shots"][0]["characters"][0]))
def _on_screen_not_visible(d): d["shots"][2]["lines"][0]["on_screen"] = True
def _on_screen_facing_away(d): d["shots"][1]["characters"][0]["facing"] = "away"
def _narrator_on_screen(d): d["shots"][0]["lines"][0]["on_screen"] = True
def _character_line_without_on_screen(d): del d["shots"][1]["lines"][0]["on_screen"]
def _speaker_not_in_cast(d): d["shots"][0]["lines"][0]["speaker"] = "owl"
def _long_line(d): d["shots"][0]["lines"][0]["text"] = " ".join(["word"] * 75)
def _multi_word_pronunciation(d): d["pronunciations"]["Old Oak"] = "old oak"
def _long_tags(d): d["publishing"]["tags"] = [f"tag number {i:03d}" for i in range(40)]
def _long_pose(d): d["shots"][0]["characters"][0]["pose"] = " ".join(["very"] * 13)
def _unknown_camera(d): d["shots"][1]["camera"]["move"] = "dolly_zoom"
def _duration(d): d["shots"][0]["duration"] = 8
def _pause(d): d["shots"][0]["lines"][0]["pause_after"] = 5
def _language(d): d["language"] = "te"
def _long_title(d): d["publishing"]["title"] = "x" * 120
def _no_made_for_kids(d): del d["publishing"]["made_for_kids"]
def _boolean_text(d): d["shots"][0]["emotion"] = True
def _stub(d): d["shots"] = []
def _line_id(d): d["shots"][0]["lines"][0]["id"] = "greeting"


@pytest.mark.parametrize("mutate, rule, path", [
    (_unknown_series, "episode.unknown-series", "series"),
    (_wrong_id, "episode.id-matches-folder", "id"),
    (_bad_id_format, "schema.pattern", "id"),
    (_owl_in_cast, "episode.cast-in-bible", "cast[4]"),
    (_undeclared_location, "episode.unknown-location", "shots[0].location"),
    (_undeclared_prop, "episode.unknown-prop", "shots[1].props[0]"),
    (_dup_location, "episode.duplicate-location", "locations[2].id"),
    (_shot_gap, "episode.shot-sequence", "shots[2].id"),
    (_visible_not_in_cast, "episode.visible-in-cast", "shots[5].characters[2].id"),
    (_narrator_visible, "episode.narrator-visible", "shots[0].characters[1].id"),
    (_duplicate_visible, "episode.duplicate-visible", "shots[0].characters[1].id"),
    (_on_screen_not_visible, "episode.on-screen-speaker", "shots[2].lines[0].on_screen"),
    (_on_screen_facing_away, "episode.on-screen-speaker", "shots[1].lines[0].on_screen"),
    (_narrator_on_screen, "episode.on-screen-speaker", "shots[0].lines[0].on_screen"),
    (_character_line_without_on_screen, "episode.on-screen-required", "shots[1].lines[0].on_screen"),
    (_speaker_not_in_cast, "episode.speaker-in-cast", "shots[0].lines[0].speaker"),
    (_long_line, "episode.line-length", "shots[0].lines[0].text"),
    (_multi_word_pronunciation, "episode.pronunciation-key", "pronunciations.Old Oak"),
    (_long_tags, "episode.tags-length", "publishing.tags"),
    (_long_pose, "episode.free-text-length", "shots[0].characters[0].pose"),
    (_unknown_camera, "schema.enum", "shots[1].camera.move"),
    (_duration, "schema.unknown-field", "shots[0].duration"),
    (_pause, "schema.range", "shots[0].lines[0].pause_after"),
    (_language, "schema.const", "language"),
    (_long_title, "schema.max-length", "publishing.title"),
    (_no_made_for_kids, "schema.required", "publishing.made_for_kids"),
    (_boolean_text, "schema.type", "shots[0].emotion"),
    (_stub, "episode.stub", "shots"),
    (_line_id, "schema.unknown-field", "shots[0].lines[0].id"),
])
def test_each_error_rule(project, mutate, rule, path):
    doc = project.episode()
    mutate(doc)
    project.write_episode(doc)
    errors = [f for f in _episode_findings(_check(project)) if f.severity == "error"]
    assert (rule, path) in {(f.rule, f.path) for f in errors}, errors


def _unused_location(d): d["locations"].append({"id": "river-bank", "description": "A slow river."})
def _unused_pronunciation(d): d["pronunciations"]["Zephyrine"] = "ZEF-ih-reen"
def _many_shots(d):
    for i in range(6, 20):
        shot = copy.deepcopy(d["shots"][0])
        shot["id"] = f"s{i + 1:02d}"
        d["shots"].append(shot)


@pytest.mark.parametrize("mutate, rule, path", [
    (_unused_location, "episode.unused-location", "locations[2]"),
    (_unused_pronunciation, "episode.unused-pronunciation", "pronunciations.Zephyrine"),
    (_many_shots, "episode.shot-count", "shots"),
])
def test_each_warning_rule_without_errors(project, mutate, rule, path):
    doc = project.episode()
    mutate(doc)
    project.write_episode(doc)
    findings = _episode_findings(_check(project))
    assert [f for f in findings if f.severity == "error"] == []
    assert (rule, path) in {(f.rule, f.path) for f in findings if f.severity == "warning"}


def test_messages_are_actionable(project):
    doc = project.episode()
    _unknown_camera(doc)
    _duration(doc)
    _owl_in_cast(doc)
    _language(doc)
    project.write_episode(doc)
    by_rule = {f.rule: f.message for f in _check(project).findings}
    assert "static, push_in, pull_out" in by_rule["schema.enum"]
    assert "derived from the recorded audio" in by_rule["schema.unknown-field"]
    assert "add 'owl' to the series bible first" in by_rule["episode.cast-in-bible"]
    assert "only 'en' is supported" in by_rule["schema.const"]


def test_unsupported_version_stops_further_checks(project):
    doc = project.episode()
    doc["schema"] = "story-episode/v2"
    doc["cast"].append("owl")
    project.write_episode(doc)
    assert [f.rule for f in _check(project).findings] == ["schema.version"]


def test_narrator_line_needs_no_on_screen(project):
    doc = project.episode()
    assert "on_screen" not in doc["shots"][0]["lines"][0]
    assert _episode_findings(_check(project)) == []


def test_id_rule_skipped_when_no_folder_expected(project):
    doc = project.episode()
    _wrong_id(doc)
    project.write_episode(doc)
    assert "episode.id-matches-folder" not in rules(_check(project, expected=None).findings)


def test_line_id_message_explains_derivation(project):
    doc = project.episode()
    _line_id(doc)
    project.write_episode(doc)
    msg = next(f.message for f in _check(project).findings if f.path == "shots[0].lines[0].id")
    assert "derived from position" in msg and "s03-l02" in msg


def test_made_for_kids_deviating_from_series_default_warns(project):
    series = project.series()
    series["defaults"] = {"made_for_kids": False}
    project.write_series(series)
    assert "episode.made-for-kids-default" not in rules(_check(project).findings)
    doc = project.episode()
    doc["publishing"]["made_for_kids"] = True
    project.write_episode(doc)
    findings = _episode_findings(_check(project))
    assert [f for f in findings if f.severity == "error"] == []
    assert ("episode.made-for-kids-default", "publishing.made_for_kids") in {
        (f.rule, f.path) for f in findings if f.severity == "warning"}


# series locations ------------------------------------------------------------------

def _add_series_location(project, lid="meadow-edge"):
    series = project.series()
    series["locations"] = [{"id": lid, "description": "Tall golden grass at the meadow's edge.",
                            "references": [f"locations/{lid}/ref-01.png"]}]
    project.write_series(series)


def test_series_location_used_directly(project):
    _add_series_location(project, "old-oak")
    doc = project.episode()
    doc["shots"][0]["location"] = "old-oak"
    project.write_episode(doc)
    assert _episode_findings(_check(project)) == []


def test_episode_may_rely_only_on_series_locations(project):
    _add_series_location(project, "old-oak")
    doc = project.episode()
    for shot in doc["shots"]:
        shot["location"] = "old-oak"
    doc["locations"] = []
    project.write_episode(doc)
    assert _episode_findings(_check(project)) == []


def test_redeclaring_a_series_location_is_an_error(project):
    _add_series_location(project, "meadow-edge")   # the episode also declares meadow-edge
    errors = [f for f in _episode_findings(_check(project)) if f.severity == "error"]
    assert ("episode.redeclared-series-location", "locations[0].id") in {(f.rule, f.path) for f in errors}
    msg = next(f.message for f in errors if f.rule == "episode.redeclared-series-location")
    assert "remove this declaration" in msg


def test_unknown_location_names_both_sources(project):
    _add_series_location(project, "old-oak")
    doc = project.episode()
    doc["shots"][0]["location"] = "river-bank"
    project.write_episode(doc)
    msg = next(f.message for f in _check(project).findings if f.rule == "episode.unknown-location")
    assert "neither under the episode's locations nor as a series location" in msg


# thumbnail characters ------------------------------------------------------------------

def _thumb(d, chars):
    d["publishing"]["thumbnail"]["characters"] = chars


@pytest.mark.parametrize("mutate, rule, path", [
    (lambda d: d["publishing"]["thumbnail"].pop("characters"), "schema.required", "publishing.thumbnail.characters"),
    (lambda d: _thumb(d, ["owl"]), "episode.thumbnail-character-in-cast", "publishing.thumbnail.characters[0]"),
    (lambda d: _thumb(d, ["narrator"]), "episode.thumbnail-narrator", "publishing.thumbnail.characters[0]"),
    (lambda d: _thumb(d, ["pip", "pip"]), "schema.unique", "publishing.thumbnail.characters"),
])
def test_thumbnail_character_rules(project, mutate, rule, path):
    doc = project.episode()
    mutate(doc)
    project.write_episode(doc)
    errors = [f for f in _episode_findings(_check(project)) if f.severity == "error"]
    assert (rule, path) in {(f.rule, f.path) for f in errors}, errors


def test_scenery_only_thumbnail_is_valid(project):
    doc = project.episode()
    _thumb(doc, [])
    project.write_episode(doc)
    assert _episode_findings(_check(project)) == []
