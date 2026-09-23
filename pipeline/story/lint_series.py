"""Series bible validation: pass 1 (schema) plus the rules a schema cannot express."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .findings import ERROR, Finding
from .load import StrictYAMLError, load_yaml, rel
from .schema import SERIES_SCHEMA, check_version, load_voices, validate_structure

SERIES_FILE = "series.yaml"
_VISUAL_FIELDS = ("description", "outfit", "features")


@dataclass
class SeriesCheck:
    findings: list[Finding] = field(default_factory=list)
    bible: dict | None = None  # the loaded document, when it could be parsed as a mapping

    def characters(self) -> dict[str, dict]:
        """Characters by id, skipping malformed entries."""
        if not self.bible or not isinstance(self.bible.get("characters"), list):
            return {}
        return {c["id"]: c for c in self.bible["characters"]
                if isinstance(c, dict) and isinstance(c.get("id"), str)}

    def locations(self) -> dict[str, dict]:
        """Recurring series locations by id, skipping malformed entries."""
        if not self.bible or not isinstance(self.bible.get("locations"), list):
            return {}
        return {loc["id"]: loc for loc in self.bible["locations"]
                if isinstance(loc, dict) and isinstance(loc.get("id"), str)}


def check_series(series_dir: Path, root: Path) -> SeriesCheck:
    file_path = series_dir / SERIES_FILE
    file = rel(file_path, root)
    out = SeriesCheck()
    try:
        doc = load_yaml(file_path)
    except StrictYAMLError as exc:
        out.findings.append(Finding(ERROR, file, f"line {exc.line}" if exc.line else "", "yaml", exc.message))
        return out
    stop = check_version(doc, SERIES_SCHEMA, file)
    if stop:
        out.findings += stop
        return out
    out.bible = doc
    out.findings += validate_structure(doc, SERIES_SCHEMA, root, file)
    out.findings += _lint(doc, series_dir, root, file)
    return out


def _lint(doc: dict, series_dir: Path, root: Path, file: str) -> list[Finding]:
    f: list[Finding] = []

    def err(path, rule, msg):
        f.append(Finding(ERROR, file, path, rule, msg))

    declared = doc.get("id")
    if isinstance(declared, str) and declared != series_dir.name:
        err("id", "series.id-matches-folder",
            f"id '{declared}' does not match its folder name '{series_dir.name}'")

    chars = doc.get("characters")
    if not isinstance(chars, list):
        return f
    allowed_voices = [v["id"] for v in load_voices(root)]
    seen: dict[str, int] = {}
    narrators = []
    for i, c in enumerate(chars):
        if not isinstance(c, dict):
            continue
        base = f"characters[{i}]"
        cid = c.get("id")
        if isinstance(cid, str):
            if cid in seen:
                err(f"{base}.id", "series.duplicate-id",
                    f"character id '{cid}' is already used by characters[{seen[cid]}]")
            else:
                seen[cid] = i
        kind = c.get("kind")
        if kind == "narrator":
            narrators.append(i)
            for key in _VISUAL_FIELDS:
                if key in c:
                    err(f"{base}.{key}", "series.narrator-visual",
                        f"the narrator is never drawn, so it must not define '{key}'")
        elif kind == "character":
            for key in _VISUAL_FIELDS:
                if key not in c:
                    err(f"{base}.{key}", "series.character-visual",
                        f"on-screen character '{cid}' must define '{key}' so it can be drawn consistently")
            if isinstance(c.get("features"), list) and not c["features"]:
                err(f"{base}.features", "series.character-visual",
                    "list at least one distinguishing feature")
        voice = c.get("voice")
        if isinstance(voice, dict) and isinstance(voice.get("kokoro"), str) and voice["kokoro"] not in allowed_voices:
            err(f"{base}.voice.kokoro", "series.voice-allowlist",
                f"'{voice['kokoro']}' is not an allowed English Kokoro voice; allowed: {', '.join(allowed_voices)}")

    _lint_locations(doc, set(seen), err)

    if not narrators:
        err("characters", "series.one-narrator", "exactly one character must have kind: narrator; none found")
    elif len(narrators) > 1:
        err("characters", "series.one-narrator",
            f"exactly one character must have kind: narrator; found {len(narrators)} "
            f"(characters[{'], characters['.join(map(str, narrators))}])")
    return f


def _lint_locations(doc: dict, character_ids: set[str], err) -> None:
    locations = doc.get("locations")
    if not isinstance(locations, list):
        return
    seen: dict[str, int] = {}
    for i, loc in enumerate(locations):
        if not isinstance(loc, dict) or not isinstance(loc.get("id"), str):
            continue
        base = f"locations[{i}]"
        lid = loc["id"]
        if lid in seen:
            err(f"{base}.id", "series.duplicate-location",
                f"location id '{lid}' is already used by locations[{seen[lid]}]")
        else:
            seen[lid] = i
        if lid in character_ids:
            err(f"{base}.id", "series.location-id-collision",
                f"location id '{lid}' is also a character id; ids must be unique across characters and locations")
