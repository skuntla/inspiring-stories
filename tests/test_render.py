"""Render planning, the missing-component check, the duration check, approvals and `story produce`."""
import json
import subprocess

import pytest
import yaml

from conftest import EPISODE_ID, SERIES_ID
from story import cli, render
from story.render import check_duration, plan, rig_support, write_registry
from test_timeline import voiced  # noqa: F401  (fixture)

ALL_MOODS = "['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired']"
RIGS = {"pip": "['stand', 'walk', 'sit', 'kneel', 'reach', 'hold', 'hug']",
        "bramble": "['stand', 'sit', 'hold']",
        "wren": "['stand', 'perch', 'fly']"}


def write_components(project, skip=()):
    """A minimal component library for the example episode (Python only reads the files)."""
    src = project.root / "render" / "src"
    series = src / "series" / SERIES_ID
    episode = src / "episodes" / EPISODE_ID
    files = {series / "characters" / f"{cid}.tsx": f"export const rig = {{\n\tstances: {st},\n\tmoods: {ALL_MOODS},\n}};\n"
             for cid, st in RIGS.items()}
    files[episode / "locations" / "meadow-edge.tsx"] = "export const location = {};\n"
    files[episode / "locations" / "bramble-burrow.tsx"] = "export const location = {};\n"
    files[episode / "props" / "lantern-seed.tsx"] = "export const prop = {};\n"
    for path, text in files.items():
        if path.stem in skip:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    (src / "kit").mkdir(parents=True, exist_ok=True)
    (src / "kit" / "style.tsx").write_text("export const INK = '#3b2a20';\n")
    (src / "Episode.tsx").write_text("export const Episode = null;\n")
    return src


@pytest.fixture
def ready(voiced, capsys):  # noqa: F811
    code, _, _ = voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    assert code == 0
    write_components(voiced)
    return voiced


def _timeline(project):
    return json.loads((project.episode_dir / "build" / "timeline.json").read_text())


# --- planning ------------------------------------------------------------------------------

def test_rig_support_reads_one_line_arrays():
    assert rig_support("x = {\n\tstances: ['stand', \"sit\"],\n}", "stances") == {"stand", "sit"}
    assert rig_support("no declaration here", "stances") is None


def test_all_components_present(ready, capsys):
    code, out, _ = ready.run("render", str(ready.episode_dir), "--check", capsys=capsys)
    assert code == 0 and "all 6 components present (3 characters, 2 locations, 1 props)" in out
    assert "Approval (preview): not approved" in out


@pytest.mark.parametrize("skip, needle", [
    ("meadow-edge", f"write render/src/episodes/{EPISODE_ID}/locations/meadow-edge.tsx"),
    ("lantern-seed", f"write render/src/episodes/{EPISODE_ID}/props/lantern-seed.tsx"),
    ("wren", f"missing character rig 'wren': write render/src/series/{SERIES_ID}/characters/wren.tsx"),
])
def test_missing_component_is_named_with_its_path(voiced, capsys, skip, needle):  # noqa: F811
    voiced.run("timeline", str(voiced.episode_dir), capsys=capsys)
    write_components(voiced, skip=(skip,))
    code, out, err = voiced.run("render", str(voiced.episode_dir), "--check", capsys=capsys)
    assert code == 1 and needle in err and "nothing was rendered" in err


def test_unsupported_stance_is_named(ready, capsys):
    doc = ready.episode()
    doc["shots"][5]["characters"][2]["stance"] = "kneel"   # wren in s06
    ready.write_episode(doc)
    ready.run("timeline", str(ready.episode_dir), capsys=capsys)
    code, _, err = ready.run("render", str(ready.episode_dir), "--check", capsys=capsys)
    assert code == 1 and "'wren' does not support stance 'kneel' (used in s06)" in err


def test_series_location_missing_points_to_series_folder(ready):
    tl = _timeline(ready)
    tl["shots"][0]["location"] = "old-oak"
    p = plan(ready.root, tl, series_locations={"old-oak"})
    assert any(f"write render/src/series/{SERIES_ID}/locations/old-oak.tsx" in m for m in p.problems)


def test_episode_component_overrides_series(ready):
    src = ready.root / "render" / "src"
    shared = src / "series" / SERIES_ID / "props" / "lantern-seed.tsx"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text("export const prop = {};\n")
    p = plan(ready.root, _timeline(ready), set())
    assert p.components["props"]["lantern-seed"] == src / "episodes" / EPISODE_ID / "props" / "lantern-seed.tsx"


def test_shared_library_is_used_when_nothing_more_specific_exists(ready):
    src = ready.root / "render" / "src"
    common = src / "common" / "locations" / "compass-closeup.tsx"
    common.parent.mkdir(parents=True, exist_ok=True)
    common.write_text('export const about = "A compass.";\nexport const location = {};\n')
    tl = _timeline(ready)
    tl["shots"][0]["location"] = "compass-closeup"
    assert plan(ready.root, tl, set()).components["locations"]["compass-closeup"] == common
    mine = src / "series" / SERIES_ID / "locations" / "compass-closeup.tsx"
    mine.parent.mkdir(parents=True, exist_ok=True)
    mine.write_text("export const location = {};\n")
    assert plan(ready.root, tl, set()).components["locations"]["compass-closeup"] == mine


def test_shared_library_lists_ids_and_descriptions(tmp_path):
    loc = tmp_path / "render" / "src" / "common" / "locations"
    loc.mkdir(parents=True)
    (loc / "notebook-page.tsx").write_text('import React from "react";\nexport const about = "A notebook.";\n')
    (loc / "plain.tsx").write_text("export const location = {};\n")
    assert render.common_library(tmp_path) == {"locations": {"notebook-page": "A notebook.", "plain": ""}, "props": {}}


def test_thumbnail_spec_is_exported_when_present(ready):
    src = ready.root / "render" / "src"
    p = plan(ready.root, _timeline(ready), set())
    assert p.thumbnail is None
    assert "export const thumbnail: ThumbnailSpec | undefined = undefined;" in write_registry(ready.root, p).read_text()
    spec = src / "episodes" / EPISODE_ID / "thumbnail.tsx"
    spec.write_text("export const thumbnail = {\n\theadlines: ['WHY *THIS*', \"IT'S *YOURS*\\nNOW\"],\n};\n")
    p = plan(ready.root, _timeline(ready), set())
    assert p.thumbnail == spec and render.thumbnail_variants(spec) == 2
    assert f"export {{thumbnail}} from '../episodes/{EPISODE_ID}/thumbnail';" in write_registry(ready.root, p).read_text()
    assert spec not in p.files()  # the thumbnail is not an approval input


def test_thumbnail_command_names_the_missing_spec(ready, capsys):
    code, _, err = ready.run("thumbnail", str(ready.episode_dir), capsys=capsys)
    assert code == 1 and f"render/src/episodes/{EPISODE_ID}/thumbnail.tsx" in err


def test_registry_is_deterministic(ready):
    p = plan(ready.root, _timeline(ready), set())
    first = write_registry(ready.root, p).read_text()
    assert write_registry(ready.root, plan(ready.root, _timeline(ready), set())).read_text() == first
    assert "import {rig as c0} from '../series/example-meadow/characters/bramble';" in first
    assert "'meadow-edge': " in first and "'lantern-seed': " in first


def test_stale_timeline_is_refused(ready, capsys):
    doc = ready.episode()
    doc["shots"][0]["camera"]["move"] = "pan_left"
    ready.write_episode(doc)
    code, _, err = ready.run("render", str(ready.episode_dir), "--check", capsys=capsys)
    assert code == 1 and "out of date" in err


# --- duration check --------------------------------------------------------------------------

def _mp4(path, seconds):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=size=16x16:rate=30:duration={seconds}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def test_duration_check(tmp_path):
    clip = _mp4(tmp_path / "a.mp4", 2)
    assert check_duration(clip, {"durationInFrames": 60}) is None
    assert "timeline is 3.000 s" in check_duration(clip, {"durationInFrames": 90})


# --- approvals --------------------------------------------------------------------------------

def _fake_preview(project):
    _mp4(project.episode_dir / "build" / "preview.mp4", 1)


def test_approve_records_every_input(ready, capsys):
    _fake_preview(ready)
    code, out, _ = ready.run("approve", str(ready.episode_dir), "preview", capsys=capsys)
    assert code == 0 and "approved preview" in out
    entry = yaml.safe_load((ready.episode_dir / "approvals.yaml").read_text())["approvals"][0]
    inputs = entry["inputs"]
    for key in (f"episodes/{EPISODE_ID}/episode.yaml", f"series/{SERIES_ID}/series.yaml",
                f"episodes/{EPISODE_ID}/build/speech.json", f"episodes/{EPISODE_ID}/build/timeline.json",
                f"episodes/{EPISODE_ID}/build/preview.mp4", f"render/src/series/{SERIES_ID}/characters/pip.tsx",
                f"render/src/episodes/{EPISODE_ID}/props/lantern-seed.tsx", "render/src/kit/style.tsx"):
        assert inputs[key].startswith("sha256:"), key
    _, out, _ = ready.run("render", str(ready.episode_dir), "--check", capsys=capsys)
    assert "Approval (preview): approved at" in out


def test_edited_rig_makes_approval_stale(ready, capsys):
    _fake_preview(ready)
    ready.run("approve", str(ready.episode_dir), "preview", capsys=capsys)
    rig = ready.root / "render" / "src" / "series" / SERIES_ID / "characters" / "pip.tsx"
    rig.write_text(rig.read_text() + "// tweak\n")
    _, out, _ = ready.run("render", str(ready.episode_dir), "--check", capsys=capsys)
    assert "stale" in out and f"render/src/series/{SERIES_ID}/characters/pip.tsx (changed)" in out


def test_approve_refuses_missing_or_old_preview(ready, capsys):
    code, _, err = ready.run("approve", str(ready.episode_dir), "preview", capsys=capsys)
    assert code == 1 and "missing or older than the timeline" in err
    _fake_preview(ready)
    ready.run("timeline", str(ready.episode_dir), capsys=capsys)   # a newer timeline than the preview
    code, _, err = ready.run("approve", str(ready.episode_dir), "preview", capsys=capsys)
    assert code == 1 and not (ready.episode_dir / "approvals.yaml").exists()


def test_unknown_checkpoint(ready, capsys):
    code, _, err = ready.run("approve", str(ready.episode_dir), "images", capsys=capsys)
    assert code == 2 and "supported: preview" in err


# --- produce ---------------------------------------------------------------------------------

def test_produce_runs_stages_in_order_and_stops_on_failure(project, capsys, monkeypatch):
    calls = []

    def stage(name, code=0):
        def run(args):
            calls.append((name, args.preview, args.final))
            return code
        return run

    monkeypatch.setattr(cli, "cmd_voice", stage("voice"))
    monkeypatch.setattr(cli, "cmd_timeline", stage("timeline"))
    monkeypatch.setattr(cli, "cmd_render", stage("render"))
    code, out, _ = project.run("produce", str(project.episode_dir), capsys=capsys)
    assert code == 0 and [c[0] for c in calls] == ["voice", "timeline", "render"]
    assert calls[-1][1:] == (True, False)                      # a preview, never the final
    assert "story approve" in out and "build/preview.mp4" in out
    calls.clear()
    monkeypatch.setattr(cli, "cmd_timeline", stage("timeline", code=1))
    code, _, err = project.run("produce", str(project.episode_dir), capsys=capsys)
    assert code == 1 and [c[0] for c in calls] == ["voice", "timeline"] and "stopped at `story timeline`" in err


def test_render_reports_output_for_a_relative_episode_path(ready, capsys, monkeypatch):
    """Regression: printing the output path must work when the episode path is relative."""
    monkeypatch.chdir(ready.root)
    monkeypatch.setattr(render, "run_remotion", lambda root, target, tl, preview: _mp4(
        target / "build" / "preview.mp4", tl["durationInFrames"] / 30))
    code = cli.main(["render", f"episodes/{EPISODE_ID}", "--preview"])
    out = capsys.readouterr().out
    assert code == 0 and f"wrote episodes/{EPISODE_ID}/build/preview.mp4" in out
