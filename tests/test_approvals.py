"""Hash-bound approvals: records, staleness, the approve command."""
import yaml

from conftest import EPISODE_ID
from test_images import fill_episode, fill_series, make_image


def approve(project, capsys, target=None, checkpoint="images"):
    return project.run("approve", str(target or project.episode_dir), checkpoint, capsys=capsys)


def status_line(project, capsys, target=None):
    _, out, _ = project.run("images", str(target or project.episode_dir), capsys=capsys)
    return out[out.index("Approval ("):]


def test_first_approval_records_inputs(project, capsys):
    fill_episode(project)
    code, out, _ = approve(project, capsys)
    assert code == 0 and "approved images" in out
    doc = yaml.safe_load((project.episode_dir / "approvals.yaml").read_text())
    assert doc["schema"] == "story-approvals/v1" and len(doc["approvals"]) == 1
    entry = doc["approvals"][0]
    assert entry["checkpoint"] == "images" and entry["digest"].startswith("sha256:")
    assert entry["approved_at"].endswith("Z")
    inputs = entry["inputs"]
    assert f"episodes/{EPISODE_ID}/episode.yaml" in inputs and "series/example-meadow/series.yaml" in inputs
    assert f"episodes/{EPISODE_ID}/images/thumbnail.png" in inputs
    assert f"episodes/{EPISODE_ID}/images/locations/meadow-edge.png" in inputs
    # attached series references are covered too (missing ones recorded as such)
    assert inputs["series/example-meadow/characters/pip/ref-3q.png"] == "missing"
    assert status_line(project, capsys).startswith("Approval (images): approved at ")


def test_reapproval_appends(project, capsys):
    fill_episode(project)
    approve(project, capsys)
    first = (project.episode_dir / "approvals.yaml").read_text()
    make_image(project.episode_dir / "images" / "s03.png", color=(1, 2, 3))
    approve(project, capsys)
    doc = yaml.safe_load((project.episode_dir / "approvals.yaml").read_text())
    assert len(doc["approvals"]) == 2
    assert (project.episode_dir / "approvals.yaml").read_text().startswith(first.rstrip("\n").split("\n  - ")[0])
    assert doc["approvals"][0]["inputs"] != doc["approvals"][1]["inputs"]


def test_replaced_image_is_stale(project, capsys):
    fill_episode(project)
    approve(project, capsys)
    make_image(project.episode_dir / "images" / "s03.png", color=(1, 2, 3))
    line = status_line(project, capsys)
    assert "stale" in line and f"episodes/{EPISODE_ID}/images/s03.png (changed)" in line


def test_replaced_anchor_is_stale(project, capsys):
    fill_episode(project)
    approve(project, capsys)
    make_image(project.episode_dir / "images" / "locations" / "meadow-edge.png", color=(9, 9, 9))
    assert "images/locations/meadow-edge.png (changed)" in status_line(project, capsys)


def test_relocked_manifest_is_stale(project, capsys):
    fill_episode(project)
    approve(project, capsys)
    doc = project.episode()
    doc["title"] = "A New Title"
    project.write_episode(doc)
    assert f"episodes/{EPISODE_ID}/episode.yaml (changed)" in status_line(project, capsys)


def test_regenerated_reference_is_stale(project, capsys):
    fill_episode(project)
    fill_series(project)
    approve(project, capsys)
    make_image(project.series_dir / "characters" / "pip" / "ref-3q.png", (1024, 1536), color=(5, 5, 5))
    assert "series/example-meadow/characters/pip/ref-3q.png (changed)" in status_line(project, capsys)


def test_approval_blocked_by_missing_thumbnail(project, capsys):
    fill_episode(project, skip=("thumbnail",))
    code, _, err = approve(project, capsys)
    assert code == 1 and "not approved" in err and "thumbnail" in err
    assert not (project.episode_dir / "approvals.yaml").exists()


def test_unknown_checkpoint_is_usage_error(project, capsys):
    code, _, err = approve(project, capsys, checkpoint="audio")
    assert code == 2 and "supported: images" in err
    code, _, err = approve(project, capsys, target=project.series_dir, checkpoint="images")
    assert code == 2 and "supported: references" in err


def test_series_references_checkpoint(project, capsys):
    fill_series(project)
    code, _, _ = approve(project, capsys, target=project.series_dir, checkpoint="references")
    assert code == 0
    assert status_line(project, capsys, project.series_dir).startswith("Approval (references): approved")
    make_image(project.series_dir / "style" / "ref-01.png", color=(7, 7, 7))
    assert "series/example-meadow/style/ref-01.png (changed)" in status_line(project, capsys, project.series_dir)


def test_unchanged_stays_approved(project, capsys):
    fill_episode(project)
    approve(project, capsys)
    project.run("prompts", str(project.episode_dir), capsys=capsys)   # regenerating build/ changes nothing
    assert status_line(project, capsys).startswith("Approval (images): approved")
