"""Prompt packs: anchors, attachment selection, prompt content, thumbnails, series packs."""
import pytest

from conftest import EPISODE_ID, SERIES_ID
from story.cli import _checked
from story.prompts import (MAX_ATTACHMENTS, anchored_locations, episode_pack, series_pack, shot_attachments,
                           shot_prompt, thumbnail_attachments, thumbnail_prompt)


def _ctx(project, kind="episode"):
    target = project.episode_dir if kind == "episode" else project.series_dir
    result, ctx = _checked(kind, target, project.root)
    assert ctx is not None, [f for f in result.findings if f.severity == "error"]
    return ctx


def _with_expressions(project):
    doc = project.series()
    for c in doc["characters"]:
        if c["kind"] == "character":
            c["references"]["expressions"] = f"characters/{c['id']}/expressions.png"
    project.write_series(doc)


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")


# --- anchors ---------------------------------------------------------------------

def test_anchors_are_episode_locations_used_by_two_or_more_shots(project):
    # the example uses meadow-edge in s01-s04 and bramble-burrow in s05-s06
    assert _ctx(project).anchors == ["meadow-edge", "bramble-burrow"]


def test_single_use_location_gets_no_anchor(project):
    doc = project.episode()
    doc["locations"].append({"id": "old-fence", "description": "A crooked fence."})
    doc["shots"][0]["location"] = "old-fence"
    project.write_episode(doc)
    assert "old-fence" not in _ctx(project).anchors


def test_series_location_gets_no_anchor(project):
    series = project.series()
    series["locations"] = [{"id": "old-oak", "description": "A huge oak.", "references": ["locations/old-oak/ref-01.png"]}]
    project.write_series(series)
    doc = project.episode()
    doc["shots"][4]["location"] = doc["shots"][5]["location"] = "old-oak"
    doc["locations"] = [loc for loc in doc["locations"] if loc["id"] != "bramble-burrow"]
    project.write_episode(doc)
    ctx = _ctx(project)
    assert ctx.anchors == ["meadow-edge"]
    kept, _ = shot_attachments(ctx, ctx.doc["shots"][4])
    assert [a.kind for a in kept[:2]] == ["style", "location"]
    assert kept[1].path == "series/example-meadow/locations/old-oak/ref-01.png"


def test_anchored_locations_counts_only_episode_locations():
    doc = {"locations": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
           "shots": [{"location": x} for x in ("a", "a", "b", "c", "c", "s", "s")]}
    assert anchored_locations(doc, {"c"}) == ["a"]


# --- attachments -------------------------------------------------------------------

@pytest.mark.parametrize("facing, view", [("camera", "ref-front.png"), ("left", "ref-3q.png"),
                                          ("right", "ref-3q.png"), ("away", "ref-side.png")])
def test_view_follows_facing(project, facing, view):
    doc = project.episode()
    doc["shots"][0]["characters"][0]["facing"] = facing
    project.write_episode(doc)
    ctx = _ctx(project)
    kept, _ = shot_attachments(ctx, ctx.doc["shots"][0])
    assert kept[2].path == f"series/example-meadow/characters/pip/{view}"


def test_anchor_comes_right_after_style(project):
    ctx = _ctx(project)
    kept, _ = shot_attachments(ctx, ctx.doc["shots"][0])
    assert kept[0].path == "series/example-meadow/style/ref-01.png"
    assert kept[1].path == f"episodes/{EPISODE_ID}/images/locations/meadow-edge.png" and kept[1].kind == "anchor"


def test_expression_sheet_only_for_on_screen_speakers(project):
    _with_expressions(project)
    ctx = _ctx(project)
    # s05: bramble and pip both speak on screen; s03: wren speaks off screen, pip is silent
    kinds_s05 = [a.label for a in shot_attachments(ctx, ctx.doc["shots"][4])[0]]
    assert "Pip expression sheet" in kinds_s05 and "Old Bramble expression sheet" in kinds_s05
    labels_s03 = [a.label for a in shot_attachments(ctx, ctx.doc["shots"][2])[0]]
    assert not any("expression" in l for l in labels_s03)


def test_cap_drops_expressions_first_and_notes_them(project, capsys):
    _with_expressions(project)
    doc = project.episode()
    shot = doc["shots"][5]  # pip, bramble, wren visible
    for line in shot["lines"]:
        line.pop("pause_after", None)
    shot["lines"] = [{"speaker": c, "text": "Hello there.", "delivery": "warm", "on_screen": True}
                     for c in ("pip", "bramble", "wren")]
    project.write_episode(doc)
    ctx = _ctx(project)
    kept, dropped = shot_attachments(ctx, ctx.doc["shots"][5])
    assert len(kept) == MAX_ATTACHMENTS
    assert [a.kind for a in kept] == ["style", "anchor", "view", "view", "view", "expressions"]
    assert [a.label for a in dropped] == ["Old Bramble expression sheet", "Wren expression sheet"]
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    s06 = (project.episode_dir / "build" / "prompts" / "s06.md").read_text()
    assert "Not attached (six-attachment limit)" in s06 and "characters/wren/expressions.png" in s06


def test_missing_and_present_attachments_are_marked(project, capsys):
    _touch(project.series_dir / "style" / "ref-01.png")
    code, _, err = project.run("prompts", str(project.episode_dir), capsys=capsys)
    s01 = (project.episode_dir / "build" / "prompts" / "s01.md").read_text()
    assert code == 0
    assert "1. `series/example-meadow/style/ref-01.png` (style reference)\n" in s01
    assert "characters/pip/ref-3q.png` (Pip three-quarter view) — MISSING: generate it first" in s01
    assert "do not exist yet" in err and "series/example-meadow/style/ref-01.png" not in err


# --- prompt content ----------------------------------------------------------------

def test_identity_blocks_are_verbatim(project):
    ctx = _ctx(project)
    text = shot_prompt(ctx, ctx.doc["shots"][4], shot_attachments(ctx, ctx.doc["shots"][4])[0])
    bramble = ctx.characters["bramble"]
    assert " ".join(bramble["description"].split()) in text
    assert " ".join(bramble["outfit"].split()) in text
    for feature in bramble["features"]:
        assert feature in text


def test_atmosphere_split(project):
    doc = project.episode()
    doc["shots"][0]["atmosphere"] = ["fog", "fireflies", "rain"]
    project.write_episode(doc)
    ctx = _ctx(project)
    text = shot_prompt(ctx, ctx.doc["shots"][0], [])
    assert "Atmosphere: soft fog softening the distance; rainy conditions" in text
    assert "Do not draw fireflies and falling raindrops; they are animated later." in text


def test_no_spoken_text_in_any_prompt(project, capsys):
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    pack = "".join(p.read_text() for p in (project.episode_dir / "build" / "prompts").glob("*.md"))
    for shot in project.episode()["shots"]:
        for line in shot["lines"]:
            assert line["text"] not in pack


def test_speakers_and_eyes_in_animation_preparation(project):
    ctx = _ctx(project)
    text = shot_prompt(ctx, ctx.doc["shots"][4], [])
    assert "keep the eyes of Pip and Old Bramble clearly visible" in text
    assert "keep the faces and mouths of Pip and Old Bramble fully visible and unobstructed" in text


def test_scene_without_characters(project):
    doc = project.episode()
    doc["shots"][3]["characters"] = []
    doc["shots"][3]["lines"] = [{"speaker": "narrator", "text": "The night was quiet.", "delivery": "gentle"}]
    project.write_episode(doc)
    ctx = _ctx(project)
    text = shot_prompt(ctx, ctx.doc["shots"][3], [])
    assert "Characters: none. Show no characters or animals." in text and "Use the attached reference" not in text


def test_anchor_prompt(project, capsys):
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    text = (project.episode_dir / "build" / "prompts" / "location-meadow-edge.md").read_text()
    assert f"Save as: `episodes/{EPISODE_ID}/images/locations/meadow-edge.png`" in text
    assert "establishing view of this place, with no characters or animals" in text
    assert "1. `series/example-meadow/style/ref-01.png` (style reference)" in text


# --- thumbnail -----------------------------------------------------------------------

def test_thumbnail_uses_structured_characters_only(project):
    doc = project.episode()
    doc["publishing"]["thumbnail"]["characters"] = ["pip"]   # the concept still mentions Old Bramble
    project.write_episode(doc)
    ctx = _ctx(project)
    text = thumbnail_prompt(ctx)
    kept, _ = thumbnail_attachments(ctx)
    assert "Old Bramble" in ctx.doc["publishing"]["thumbnail"]["concept"]
    assert "- Pip:" in text and "- Old Bramble:" not in text
    assert [a.path for a in kept] == ["series/example-meadow/style/ref-01.png",
                                      "series/example-meadow/characters/pip/ref-front.png"]
    assert ctx.doc["publishing"]["thumbnail"]["hook"] not in text
    assert "Do not draw any text, letters or numbers." in text


def test_scenery_only_thumbnail(project):
    doc = project.episode()
    doc["publishing"]["thumbnail"]["characters"] = []
    project.write_episode(doc)
    ctx = _ctx(project)
    kept, _ = thumbnail_attachments(ctx)
    assert [a.kind for a in kept] == ["style"]
    assert "Draw no characters or animals." in thumbnail_prompt(ctx)


# --- episode pack command --------------------------------------------------------------

def _pack(project):
    d = project.episode_dir / "build" / "prompts"
    return {p.name: p.read_bytes() for p in sorted(d.iterdir())}


def test_episode_pack_files_and_index_order(project, capsys):
    code, out, _ = project.run("prompts", str(project.episode_dir), capsys=capsys)
    assert code == 0 and "wrote 9 prompt files" in out
    names = set(_pack(project))
    assert names == {"index.md", "location-meadow-edge.md", "location-bramble-burrow.md", "thumbnail.md",
                     *(f"s0{i}.md" for i in range(1, 7))}
    index = (project.episode_dir / "build" / "prompts" / "index.md").read_text()
    order = [index.index(n) for n in ("location-meadow-edge.md", "location-bramble-burrow.md", "s01.md", "s06.md",
                                      "thumbnail.md")]
    assert order == sorted(order)


def test_pack_is_byte_identical_on_regeneration(project, capsys):
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    first = _pack(project)
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    assert _pack(project) == first


def test_regeneration_removes_dropped_shot(project, capsys):
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    doc = project.episode()
    doc["shots"] = doc["shots"][:5]
    doc["props"] = [p for p in doc["props"]]
    project.write_episode(doc)
    project.run("prompts", str(project.episode_dir), capsys=capsys)
    assert "s06.md" not in _pack(project) and "s05.md" in _pack(project)


def test_invalid_episode_writes_nothing(project, capsys):
    doc = project.episode()
    doc["shots"][0]["camera"]["move"] = "dolly_zoom"
    project.write_episode(doc)
    code, out, err = project.run("prompts", str(project.episode_dir), capsys=capsys)
    assert code == 1 and "no prompts were written" in err and "dolly_zoom" in err
    assert not (project.episode_dir / "build" / "prompts").exists()


# --- series pack -----------------------------------------------------------------------

def test_series_pack_is_complete_ordered_and_chained(project, capsys):
    _with_expressions(project)
    series = project.series()
    series["locations"] = [{"id": "old-oak", "description": "A huge oak.",
                            "references": ["locations/old-oak/ref-01.png", "locations/old-oak/ref-02.png"]}]
    project.write_series(series)
    ctx = _ctx(project, "series")
    files = series_pack(ctx)
    saves = [f.save_as.removeprefix("series/example-meadow/") for f in files]
    assert saves == ["style/ref-01.png",
                     "characters/pip/ref-front.png", "characters/pip/ref-3q.png", "characters/pip/ref-side.png",
                     "characters/pip/expressions.png",
                     "characters/bramble/ref-front.png", "characters/bramble/ref-3q.png",
                     "characters/bramble/ref-side.png", "characters/bramble/expressions.png",
                     "characters/wren/ref-front.png", "characters/wren/ref-3q.png", "characters/wren/ref-side.png",
                     "characters/wren/expressions.png",
                     "locations/old-oak/ref-01.png", "locations/old-oak/ref-02.png"]
    by_save = {f.save_as.removeprefix("series/example-meadow/"): f for f in files}
    assert by_save["style/ref-01.png"].attachments == []
    assert [a.path.removeprefix("series/example-meadow/") for a in by_save["characters/pip/ref-3q.png"].attachments] \
        == ["style/ref-01.png", "characters/pip/ref-front.png"]
    assert [a.path.removeprefix("series/example-meadow/") for a in by_save["locations/old-oak/ref-02.png"].attachments] \
        == ["style/ref-01.png", "locations/old-oak/ref-01.png"]
    code, out, err = project.run("prompts", str(project.series_dir), capsys=capsys)
    assert code == 0 and "wrote 15 prompt files" in out and err == ""
    assert (project.series_dir / "build" / "prompts" / "01-style-01.md").is_file()
