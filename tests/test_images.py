"""Image intake: expected files, per-image checks, metadata, contact sheet, CLI."""
import json

import pytest
from PIL import Image

from conftest import EPISODE_ID

SHOTS = [f"s0{i}" for i in range(1, 7)]
ANCHORS = ["meadow-edge", "bramble-burrow"]


def make_image(path, size=(1920, 1080), fmt="PNG", color=(90, 120, 80)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, fmt)


def fill_episode(project, skip=(), size=(1920, 1080)):
    images = project.episode_dir / "images"
    for lid in ANCHORS:
        if lid not in skip:
            make_image(images / "locations" / f"{lid}.png", size)
    for name in SHOTS + ["thumbnail"]:
        if name not in skip:
            make_image(images / f"{name}.png", size)


def fill_series(project):
    for rel in ["style/ref-01.png"]:
        make_image(project.series_dir / rel)
    for c in ("pip", "bramble", "wren"):
        for view in ("ref-front", "ref-3q", "ref-side"):
            make_image(project.series_dir / "characters" / c / f"{view}.png", (1024, 1536))


def run_images(project, capsys, *extra):
    return project.run("images", str(project.episode_dir), *extra, capsys=capsys)


def test_clean_intake(project, capsys):
    fill_episode(project)
    code, out, err = run_images(project, capsys)
    assert code == 0, out
    assert "0 errors, 0 warnings" in out and "Approval (images): not approved" in out
    assert "images.json" in err


@pytest.mark.parametrize("missing, shown", [
    ("s06", f"episodes/{EPISODE_ID}/images/s06.png"),
    ("thumbnail", f"episodes/{EPISODE_ID}/images/thumbnail.png"),
    ("meadow-edge", f"episodes/{EPISODE_ID}/images/locations/meadow-edge.png"),
])
def test_missing_images_are_errors(project, capsys, missing, shown):
    fill_episode(project, skip=(missing,))
    code, out, _ = run_images(project, capsys, "--json")
    data = json.loads(out)
    assert code == 1
    assert {"severity": "error", "file": shown, "rule": "image.missing"}.items() <= next(
        f for f in data["findings"] if f["rule"] == "image.missing").items()


def test_duplicate_image(project, capsys):
    fill_episode(project)
    make_image(project.episode_dir / "images" / "s03.jpg", fmt="JPEG")
    code, out, _ = run_images(project, capsys)
    assert code == 1 and "image.duplicate" in out and "s03.jpg" in out and "s03.png" in out


def test_jpeg_is_accepted(project, capsys):
    fill_episode(project, skip=("s03",))
    make_image(project.episode_dir / "images" / "s03.jpg", fmt="JPEG")
    code, out, _ = run_images(project, capsys)
    assert code == 0, out


def test_unexpected_file_warns_and_system_files_are_ignored(project, capsys):
    fill_episode(project)
    make_image(project.episode_dir / "images" / "s03-old.png")
    (project.episode_dir / "images" / ".DS_Store").write_bytes(b"x")
    code, out, _ = run_images(project, capsys)
    assert code == 0 and "image.unexpected" in out and "s03-old.png" in out and ".DS_Store" not in out


@pytest.mark.parametrize("size, rules, code", [
    ((1920, 1080), set(), 0),
    ((1344, 768), {"image.small"}, 0),
    ((1024, 1024), {"image.aspect"}, 1),
    ((1000, 500), {"image.aspect", "image.too-small"}, 1),
])
def test_image_checks(project, capsys, size, rules, code):
    fill_episode(project)
    make_image(project.episode_dir / "images" / "s05.png", size)
    rc, out, _ = run_images(project, capsys, "--json")
    found = {f["rule"] for f in json.loads(out)["findings"] if f["file"].endswith("s05.png")}
    assert found == rules and rc == code


def test_corrupt_file(project, capsys):
    fill_episode(project)
    (project.episode_dir / "images" / "s05.png").write_bytes(b"not an image")
    code, out, _ = run_images(project, capsys)
    assert code == 1 and "image.unreadable" in out


def test_invalid_manifest_stops_before_images(project, capsys):
    fill_episode(project)
    doc = project.episode()
    doc["shots"][0]["camera"]["move"] = "dolly_zoom"
    project.write_episode(doc)
    code, out, _ = run_images(project, capsys, "--json")
    data = json.loads(out)
    assert code == 1 and not any(f["rule"].startswith("image.") for f in data["findings"])
    assert not (project.episode_dir / "build" / "images.json").exists()


def test_metadata_is_canonical_and_repeatable(project, capsys):
    fill_episode(project)
    run_images(project, capsys)
    first = (project.episode_dir / "build" / "images.json").read_bytes()
    run_images(project, capsys)
    assert (project.episode_dir / "build" / "images.json").read_bytes() == first
    doc = json.loads(first)
    assert [i["id"] for i in doc["images"]] == ANCHORS + SHOTS + ["thumbnail"]
    assert doc["images"][0]["width"] == 1920 and doc["images"][0]["sha256"].startswith("sha256:")
    assert set(doc["inputs"]) == {f"episodes/{EPISODE_ID}/episode.yaml", "series/example-meadow/series.yaml"}


def test_contact_sheet_has_a_tile_per_expected_image(project, capsys):
    fill_episode(project, skip=("s06",))
    run_images(project, capsys)
    sheet = Image.open(project.episode_dir / "build" / "contact-sheet.png")
    # 9 expected images (2 anchors, 6 shots, thumbnail) -> 4 columns x 3 rows of 480x(270+44) tiles, 8 px gaps
    assert sheet.size == (4 * 480 + 5 * 8, 3 * (270 + 44) + 4 * 8)
    # the s06 tile (8th, row 2 col 4) is a grey placeholder
    assert sheet.getpixel((8 + 3 * 488 + 20, 8 + 322 + 20)) == (90, 90, 90)


def test_series_intake(project, capsys):
    code, out, _ = project.run("images", str(project.series_dir), capsys=capsys)
    assert code == 1 and out.count("image.missing") == 10
    fill_series(project)
    code, out, _ = project.run("images", str(project.series_dir), capsys=capsys)
    assert code == 0, out
    assert "Approval (references): not approved" in out


def test_character_references_may_be_portrait(project, capsys):
    fill_series(project)
    code, out, _ = project.run("images", str(project.series_dir), "--json", capsys=capsys)
    assert not any(f["rule"] == "image.aspect" for f in json.loads(out)["findings"])
