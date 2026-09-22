"""Pass 1: structural validation against the JSON Schemas, with plain-language messages.

Raw jsonschema messages ("Additional properties are not allowed ('x' was unexpected)")
are rewritten so that a report can be pasted straight back into ChatGPT.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .findings import ERROR, Finding, format_path

SERIES_SCHEMA = "story-series/v1"
EPISODE_SCHEMA = "story-episode/v1"
_SCHEMA_FILES = {
    SERIES_SCHEMA: "story-series.v1.schema.json",
    EPISODE_SCHEMA: "story-episode.v1.schema.json",
}

_TIMING_FIELDS = {
    "duration", "durations", "seconds", "start", "end", "start_time", "end_time",
    "timestamp", "time", "frame", "frames", "fps",
}
_LAYOUT_FIELDS = {"x", "y", "width", "height", "path", "file", "image", "voice", "kokoro_voice"}

_PATTERN_HINTS = {
    "\\S": "must not be empty",
    "^[a-z][a-z0-9]*(-[a-z0-9]+)*$": "must be lowercase kebab-case, for example 'old-oak'",
    "^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$": "must look like YYYY-MM-DD-kebab-slug, for example '2026-10-01-the-brave-seed'",
    "^s[0-9]{2}$": "must look like s01, s02, ...",
    "^[A-Za-z0-9._/-]+$": "must be a relative path using only letters, digits, '.', '_', '/' and '-'",
}


def schema_dir(root: Path) -> Path:
    return root / "schemas"


@lru_cache(maxsize=None)
def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_vocabulary(root: Path) -> dict[str, list[str]]:
    data = _load_json(str(schema_dir(root) / "vocabulary.v1.json"))
    return {name: list(d["enum"]) for name, d in data["$defs"].items()}


def load_voices(root: Path) -> list[dict]:
    return list(_load_json(str(schema_dir(root) / "kokoro-voices.en.json"))["voices"])


def _validator(root: Path, schema_name: str) -> Draft202012Validator:
    resources = []
    for f in sorted(schema_dir(root).glob("*.json")):
        doc = _load_json(str(f))
        if "$id" in doc:
            resources.append((doc["$id"], Resource.from_contents(doc)))
    registry = Registry().with_resources(resources)
    schema = _load_json(str(schema_dir(root) / _SCHEMA_FILES[schema_name]))
    return Draft202012Validator(schema, registry=registry)


def check_version(doc, expected: str, file: str) -> list[Finding]:
    """Return a stopping error when the document is not a mapping of the expected version."""
    if not isinstance(doc, dict):
        return [Finding(ERROR, file, "", "schema.not-mapping", "the file must contain a YAML mapping (key: value pairs) at the top level")]
    declared = doc.get("schema")
    if declared != expected:
        shown = "missing" if declared is None else f"'{declared}'"
        return [Finding(ERROR, file, "schema", "schema.version",
                        f"unsupported schema version {shown}; this pipeline supports only '{expected}'")]
    return []


def _type_name(value) -> str:
    return {bool: "boolean", int: "number", float: "number", str: "string",
            list: "list", dict: "mapping", type(None): "nothing (null)"}.get(type(value), type(value).__name__)


def _messages(error) -> list[tuple[list, str, str]]:
    """Translate one jsonschema error into (path, rule, message) tuples."""
    path = list(error.absolute_path)
    kind = error.validator
    value = error.validator_value
    inst = error.instance
    schema = error.schema

    if kind == "additionalProperties" and value is False and isinstance(inst, dict):
        out = []
        for key in inst:
            if key in schema.get("properties", {}):
                continue
            msg = f"unknown field '{key}'"
            if key == "id" and len(path) >= 2 and path[-2] == "lines":
                msg += "; line ids are derived from position as <shot id>-l<NN> (for example s03-l02), never authored"
            elif key in _TIMING_FIELDS:
                msg += "; durations and timing are derived from the recorded audio, never authored"
            elif key in _LAYOUT_FIELDS:
                msg += "; layout, file paths and voices are decided by the pipeline and the series bible"
            allowed = sorted(schema.get("properties", {}))
            if allowed:
                msg += f" (allowed fields: {', '.join(allowed)})"
            out.append((path + [key], "schema.unknown-field", msg))
        return out
    if kind == "required":
        return [(path + [name], "schema.required", f"missing required field '{name}'")
                for name in value if isinstance(inst, dict) and name not in inst]
    if kind == "enum":
        return [(path, "schema.enum", f"'{inst}' is not allowed; allowed values: {', '.join(map(str, value))}")]
    if kind == "const":
        if path == ["language"]:
            return [(path, "schema.const", f"'{inst}' is not supported; only 'en' is supported")]
        return [(path, "schema.const", f"must be '{value}', got '{inst}'")]
    if kind == "type":
        msg = f"expected a {value if isinstance(value, str) else ' or '.join(value)}, got {_type_name(inst)}"
        if isinstance(inst, bool) and value == "string":
            msg += " (unquoted yes/no/on/off/true/false become booleans in YAML; put the text in quotes)"
        return [(path, "schema.type", msg)]
    if kind == "pattern":
        return [(path, "schema.pattern", f"'{inst}' {_PATTERN_HINTS.get(value, f'must match {value}')}")]
    if kind == "maxLength":
        return [(path, "schema.max-length", f"is {len(inst)} characters; the limit is {value}")]
    if kind in ("minimum", "maximum"):
        lo, hi = schema.get("minimum"), schema.get("maximum")
        rng = f"{lo} to {hi}" if lo is not None and hi is not None else (f"at least {lo}" if lo is not None else f"at most {hi}")
        return [(path, "schema.range", f"{inst} is out of range; allowed: {rng}")]
    if kind == "minItems":
        return [(path, "schema.min-items", "must contain at least one item" if value == 1 else f"must contain at least {value} items")]
    if kind == "maxItems":
        return [(path, "schema.max-items", f"has {len(inst)} items; the maximum is {value}")]
    if kind == "uniqueItems":
        return [(path, "schema.unique", "contains duplicate items")]
    return [(path, f"schema.{kind}", error.message)]


def validate_structure(doc: dict, schema_name: str, root: Path, file: str) -> list[Finding]:
    findings = []
    for error in _validator(root, schema_name).iter_errors(doc):
        for path, rule, message in _messages(error):
            findings.append(Finding(ERROR, file, format_path(path), rule, message))
    return findings
