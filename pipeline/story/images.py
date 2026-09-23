"""Image intake: check the images the producer brings back from Gemini, record their
metadata in build/images.json, and draw a labelled contact sheet for approval."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .findings import ERROR, WARNING, Finding
from .load import rel
from .prompts import IMAGE_EXTS, EpisodeContext, SeriesContext, sha256_file

IGNORED_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
ASPECT = 16 / 9
ASPECT_TOLERANCE = 0.02
MIN_SHORT_SIDE = 720
FULL_HD = (1920, 1080)
FORMATS = {"PNG", "JPEG"}

TILE_W, IMG_H, LABEL_H, GAP, COLUMNS = 480, 270, 44, 8, 4


@dataclass(frozen=True)
class Expected:
    id: str  # tile label: location id, shot id, "thumbnail", or reference slot
    stem: Path  # episode: path without extension; series: the exact declared path
    exact: bool  # series references must exist at exactly the declared path
    wide: bool  # must be 16:9
    caption: str = ""


@dataclass
class Record:
    expected: Expected
    path: Path | None = None  # the file found, if any
    format: str | None = None
    width: int | None = None
    height: int | None = None
    readable: bool = False


def episode_expected(ctx: EpisodeContext) -> list[Expected]:
    images = ctx.episode_dir / "images"
    out = [Expected(lid, images / "locations" / lid, False, True, "location anchor") for lid in ctx.anchors]
    out += [Expected(s["id"], images / s["id"], False, True, " ".join(s["action"].split())) for s in ctx.doc["shots"]]
    out.append(Expected("thumbnail", images / "thumbnail", False, True, "thumbnail"))
    return out


def series_expected(ctx: SeriesContext) -> list[Expected]:
    sd = ctx.series_dir
    out = [Expected(f"style {i}", sd / ref, True, True, "style reference")
           for i, ref in enumerate(ctx.bible["style"]["references"], 1)]
    for c in ctx.bible["characters"]:
        if c["kind"] != "character":
            continue
        for slot in ("front", "three_quarter", "side", "expressions"):
            if c["references"].get(slot):
                out.append(Expected(f"{c['id']} {slot.replace('_', '-')}", sd / c["references"][slot], True, False,
                                    c["name"]))
    for loc in ctx.bible.get("locations", []) or []:
        out += [Expected(f"{loc['id']} {j}", sd / ref, True, True, "location reference")
                for j, ref in enumerate(loc["references"], 1)]
    return out


def _scan(folders: list[Path]) -> list[Path]:
    files = []
    for folder in folders:
        if folder.is_dir():
            files += [p for p in folder.rglob("*") if p.is_file()]
    return sorted(p for p in files if p.name not in IGNORED_FILES and not p.name.startswith("._"))


def intake(kind: str, ctx: SeriesContext) -> tuple[list[Finding], list[Record]]:
    root = ctx.root
    if kind == "episode":
        expected = episode_expected(ctx)
        scanned = _scan([ctx.episode_dir / "images"])
    else:
        expected = series_expected(ctx)
        scanned = _scan([ctx.series_dir / d for d in ("style", "characters", "locations")])
    findings: list[Finding] = []
    records: list[Record] = []
    matched: set[Path] = set()
    for exp in expected:
        record = Record(exp)
        records.append(record)
        if exp.exact:
            candidates = [exp.stem] if exp.stem.is_file() else []
            shown = exp.stem
        else:
            candidates = [exp.stem.with_name(exp.stem.name + ext) for ext in IMAGE_EXTS
                          if exp.stem.with_name(exp.stem.name + ext).is_file()]
            shown = exp.stem.with_name(exp.stem.name + ".png")
        matched.update(candidates)
        if not candidates:
            findings.append(Finding(ERROR, rel(shown, root), "", "image.missing", f"{exp.id}: expected image is missing"))
            continue
        if len(candidates) > 1:
            findings.append(Finding(ERROR, rel(candidates[0], root), "", "image.duplicate",
                                    f"{exp.id}: more than one file for the same image: "
                                    f"{', '.join(rel(c, root) for c in candidates)}; keep exactly one"))
            continue
        record.path = candidates[0]
        findings += _check_image(record, root)
    for path in scanned:
        if path not in matched:
            findings.append(Finding(WARNING, rel(path, root), "", "image.unexpected",
                                    "not an expected image for this folder; remove or rename it"))
    return findings, records


def _check_image(record: Record, root: Path) -> list[Finding]:
    file = rel(record.path, root)
    exp = record.expected
    try:
        with Image.open(record.path) as im:
            im.verify()
        with Image.open(record.path) as im:
            im.load()
            record.format, (record.width, record.height) = im.format, im.size
    except Exception:  # noqa: BLE001 - any decode failure means the file is unusable
        return [Finding(ERROR, file, "", "image.unreadable", f"{exp.id}: the file cannot be decoded as an image")]
    record.readable = True
    out = []
    w, h = record.width, record.height
    if record.format not in FORMATS:
        out.append(Finding(ERROR, file, "", "image.format", f"{exp.id}: {record.format} is not supported; use PNG or JPEG"))
    wide_ok = abs((w / h) / ASPECT - 1) <= ASPECT_TOLERANCE
    if exp.wide and not wide_ok:
        out.append(Finding(ERROR, file, "", "image.aspect",
                           f"{exp.id}: {w}×{h} (ratio {w / h:.2f}) is not 16:9; allowed within 2% of 1.78"))
    if min(w, h) < MIN_SHORT_SIDE:
        out.append(Finding(ERROR, file, "", "image.too-small",
                           f"{exp.id}: {w}×{h} is too small; the shorter side must be at least {MIN_SHORT_SIDE} px"))
    elif exp.wide and wide_ok and (w < FULL_HD[0] or h < FULL_HD[1]):
        out.append(Finding(WARNING, file, "", "image.small",
                           f"{exp.id}: {w}×{h} is below 1920×1080; it will be upscaled and camera movement limited"))
    return out


def write_metadata(target: Path, inputs: list[Path], records: list[Record], root: Path) -> Path:
    doc = {
        "schema": "story-images/v1",
        "inputs": {rel(p, root): sha256_file(p) for p in inputs},
        "images": [{"id": r.expected.id, "path": rel(r.path, root), "sha256": sha256_file(r.path),
                    "format": r.format, "width": r.width, "height": r.height}
                   for r in records if r.path is not None],
    }
    out = target / "build" / "images.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def write_contact_sheet(target: Path, records: list[Record]) -> Path:
    rows = max(1, -(-len(records) // COLUMNS))
    tile_h = IMG_H + LABEL_H
    sheet = Image.new("RGB", (COLUMNS * TILE_W + (COLUMNS + 1) * GAP, rows * tile_h + (rows + 1) * GAP), "#1e1e1e")
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.load_default(size=16)
    small_font = ImageFont.load_default(size=13)
    for n, record in enumerate(records):
        x = GAP + (n % COLUMNS) * (TILE_W + GAP)
        y = GAP + (n // COLUMNS) * (tile_h + GAP)
        if record.readable:
            with Image.open(record.path) as im:
                im = im.convert("RGB")
                im.thumbnail((TILE_W, IMG_H))
                sheet.paste(im, (x + (TILE_W - im.width) // 2, y + (IMG_H - im.height) // 2))
        else:
            draw.rectangle([x, y, x + TILE_W - 1, y + IMG_H - 1], fill="#5a5a5a")
            status = "MISSING" if record.path is None else "UNREADABLE"
            draw.text((x + TILE_W // 2, y + IMG_H // 2), status, fill="#ffffff", font=title_font, anchor="mm")
        caption = record.expected.caption
        if len(caption) > 62:
            caption = caption[:61] + "…"
        draw.text((x + 4, y + IMG_H + 4), record.expected.id, fill="#ffffff", font=title_font)
        draw.text((x + 4, y + IMG_H + 24), caption, fill="#bbbbbb", font=small_font)
    out = target / "build" / "contact-sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out
