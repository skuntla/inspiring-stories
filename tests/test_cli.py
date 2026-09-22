import json

from conftest import SERIES_ID
from story.cli import slugify
from story.lint_episode import check_episode


# validate ------------------------------------------------------------------------

def test_validate_valid_episode_exits_zero(project, capsys):
    code, out, _ = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert code == 0
    assert "0 errors" in out


def test_validate_series_folder(project, capsys):
    code, out, _ = project.run("validate", str(project.series_dir), capsys=capsys)
    assert code == 0
    assert "series.reference-missing" in out


def test_validate_episode_reports_broken_bible(project, capsys):
    doc = project.series()
    doc["characters"][1]["voice"]["kokoro"] = "nope"
    project.write_series(doc)
    code, out, _ = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert code == 1
    assert "series.voice-allowlist" in out and "series/example-meadow/series.yaml" in out


def test_validate_reports_every_problem(project, capsys):
    doc = project.episode()
    doc["shots"][1]["camera"]["move"] = "dolly_zoom"
    del doc["title"]
    project.write_episode(doc)
    code, out, _ = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert code == 1
    assert "shots[1].camera.move" in out and "title" in out
    assert "2 errors" in out


def test_validate_json(project, capsys):
    doc = project.episode()
    doc["language"] = "te"
    project.write_episode(doc)
    code, out, _ = project.run("validate", str(project.episode_dir), "--json", capsys=capsys)
    data = json.loads(out)
    assert code == 1
    assert data["errors"] == 1
    finding = next(f for f in data["findings"] if f["severity"] == "error")
    assert set(finding) == {"severity", "file", "path", "rule", "message"}
    assert finding["path"] == "language"


def test_validate_bad_path_exits_two(project, capsys):
    code, _, err = project.run("validate", "does/not/exist", capsys=capsys)
    assert code == 2 and "path not found" in err


def test_validate_folder_without_manifest_exits_two(project, capsys):
    code, _, _ = project.run("validate", str(project.root / "schemas"), capsys=capsys)
    assert code == 2


def test_unknown_command_exits_two(project, capsys):
    code, _, _ = project.run("frobnicate", capsys=capsys)
    assert code == 2


def test_yaml_error_is_reported_not_raised(project, capsys):
    (project.episode_dir / "episode.yaml").write_text("title: a\ntitle: b\n")
    code, out, _ = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert code == 1 and "duplicate key 'title'" in out


# new -----------------------------------------------------------------------------

def test_slugify():
    assert slugify("The Brave Little Seed") == "the-brave-little-seed"
    assert slugify("  Pip's Café — Night! ") == "pip-s-cafe-night"


def test_new_creates_stub_that_validates_as_stub(project, capsys):
    code, out, _ = project.run("new", SERIES_ID, "The Brave Little Seed", "--date", "2026-10-01", capsys=capsys)
    folder = project.root / "episodes" / "2026-10-01-the-brave-little-seed"
    assert code == 0 and (folder / "episode.yaml").is_file()
    doc = (folder / "episode.yaml").read_text()
    assert 'series: "example-meadow"' in doc and 'id: "2026-10-01-the-brave-little-seed"' in doc
    result = check_episode(folder / "episode.yaml", project.root, folder.name)
    assert "episode.stub" in {f.rule for f in result.findings}
    assert "episode.id-matches-folder" not in {f.rule for f in result.findings}


def test_new_refuses_to_overwrite(project, capsys):
    project.run("new", SERIES_ID, "Twice", "--date", "2026-10-01", capsys=capsys)
    manifest = project.root / "episodes" / "2026-10-01-twice" / "episode.yaml"
    manifest.write_text("# hand edited\n")
    code, _, err = project.run("new", SERIES_ID, "Twice", "--date", "2026-10-01", capsys=capsys)
    assert code == 1 and "refusing to overwrite" in err
    assert manifest.read_text() == "# hand edited\n"


def test_new_unknown_series_creates_nothing(project, capsys):
    code, _, err = project.run("new", "moonlit-tales", "A Story", "--date", "2026-10-01", capsys=capsys)
    assert code == 1 and "does not exist" in err
    assert not (project.root / "episodes" / "2026-10-01-a-story").exists()


def test_new_bad_date_is_usage_error(project, capsys):
    code, _, _ = project.run("new", SERIES_ID, "A Story", "--date", "01/10/2026", capsys=capsys)
    assert code == 2


# brief ---------------------------------------------------------------------------

def test_brief_contains_vocabulary_cast_and_example(project, capsys):
    code, out, _ = project.run("brief", SERIES_ID, capsys=capsys)
    assert code == 0
    assert "`push_in`" in out and "`night_crickets`" in out
    assert "| `bramble` | Old Bramble |" in out
    assert 'id: "2026-01-01-the-lantern-seed"' in out


def test_brief_writes_file(project, capsys, tmp_path):
    target = tmp_path / "brief.md"
    code, out, _ = project.run("brief", SERIES_ID, "--out", str(target), capsys=capsys)
    assert code == 0 and out == "" and target.read_text().startswith("# ChatGPT Project instructions")


def test_brief_refuses_invalid_bible(project, capsys, tmp_path):
    doc = project.series()
    doc["characters"] = [c for c in doc["characters"] if c["kind"] != "narrator"]
    project.write_series(doc)
    target = tmp_path / "brief.md"
    code, out, err = project.run("brief", SERIES_ID, "--out", str(target), capsys=capsys)
    assert code == 1 and not target.exists() and out == ""
    assert "series.one-narrator" in err


def test_brief_follows_the_bible(project, capsys):
    doc = project.series()
    doc["characters"].append({
        "id": "owl", "kind": "character", "name": "Hazel the Owl",
        "description": "A wise tawny owl with ear tufts.", "outfit": "A tiny blue shawl.",
        "features": ["ear tufts"],
        "references": {"front": "characters/owl/f.png", "three_quarter": "characters/owl/q.png", "side": "characters/owl/s.png"},
        "voice": {"kokoro": "bf_alice", "speed": 1.0},
    })
    project.write_series(doc)
    code, out, _ = project.run("brief", SERIES_ID, capsys=capsys)
    assert code == 0
    assert "| `owl` | Hazel the Owl | character | A wise tawny owl with ear tufts. |" in out


def test_brief_example_is_valid_against_its_series(project):
    """Golden check: the example embedded in the brief must always pass validation."""
    result = check_episode(project.series_dir / "example-episode.yaml", project.root, expected_id=None)
    assert [f for f in result.findings if f.severity == "error"] == []


def test_brief_defines_creative_and_lock_modes(project, capsys):
    code, out, _ = project.run("brief", SERIES_ID, capsys=capsys)
    assert code == 0
    # creative mode is the default and never emits YAML
    assert "Creative mode is the default" in out
    assert "Never output YAML in creative mode" in out
    assert "storyboard" in out
    # lock trigger, pre-flight with the blocking-decision list, single YAML block
    assert '"Lock this story"' in out
    assert "ask **only** the\n   minimum question" in out
    for blocking in ("not in the cast", "storyboard or the ending has not been agreed", "made for kids"):
        assert blocking in out
    assert "exactly **one** fenced" in out
    # relock produces a complete replacement
    assert "complete replacement" in out and "never a partial patch" in out
    # derived artifacts are not ChatGPT's job
    assert "image-generation prompts" in out and "line ids" in out
