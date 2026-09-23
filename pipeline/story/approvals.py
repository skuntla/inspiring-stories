"""Hash-bound approvals. An approval records the SHA-256 of every input it covers, so any
later change is detected as stale instead of silently carrying the approval over."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .images import Record
from .load import StrictYAMLError, load_yaml, rel
from .prompts import EpisodeContext, SeriesContext, sha256_file, shot_attachments, thumbnail_attachments

SCHEMA = "story-approvals/v1"
FILE = "approvals.yaml"
CHECKPOINT = {"episode": "images", "series": "references"}
MISSING = "missing"


def collect_inputs(kind: str, ctx: SeriesContext, records: list[Record]) -> dict[str, str]:
    root = ctx.root

    def digest(path: Path) -> str:
        return sha256_file(path) if path.is_file() else MISSING

    inputs = {rel(ctx.series_dir / "series.yaml", root): digest(ctx.series_dir / "series.yaml")}
    if kind == "episode":
        manifest = ctx.episode_dir / "episode.yaml"
        inputs[rel(manifest, root)] = digest(manifest)
        attached = [a for shot in ctx.doc["shots"] for a in shot_attachments(ctx, shot)[0]]
        attached += thumbnail_attachments(ctx)[0]
        for a in attached:
            if a.kind != "anchor":  # anchors are episode images, recorded below
                inputs[a.path] = digest(root / a.path)
    for r in records:
        path = r.path or r.expected.stem
        inputs[rel(path, root)] = digest(path)
    return dict(sorted(inputs.items()))


def overall_digest(inputs: dict[str, str]) -> str:
    canonical = json.dumps(inputs, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_entries(target: Path) -> list[dict]:
    path = target / FILE
    if not path.is_file():
        return []
    doc = load_yaml(path)
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or not isinstance(doc.get("approvals"), list):
        raise StrictYAMLError(f"{FILE} must declare schema '{SCHEMA}' and an 'approvals' list")
    return doc["approvals"]


def status(entries: list[dict], checkpoint: str, inputs: dict[str, str]) -> dict:
    latest = next((e for e in reversed(entries) if e.get("checkpoint") == checkpoint), None)
    if latest is None:
        return {"checkpoint": checkpoint, "status": "not approved", "changes": []}
    old = latest.get("inputs") or {}
    changes = []
    for key in sorted(set(old) | set(inputs)):
        if key not in old:
            changes.append(f"{key} (added)")
        elif key not in inputs:
            changes.append(f"{key} (removed)")
        elif old[key] != inputs[key]:
            changes.append(f"{key} (changed)")
    return {"checkpoint": checkpoint, "status": "stale" if changes else "approved", "changes": changes,
            "approved_at": latest.get("approved_at")}


def append(target: Path, checkpoint: str, inputs: dict[str, str], now: datetime | None = None) -> dict:
    entries = load_entries(target)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"checkpoint": checkpoint, "approved_at": stamp, "digest": overall_digest(inputs), "inputs": inputs}
    entries.append(entry)
    q = json.dumps  # JSON strings are valid double-quoted YAML scalars
    lines = [f"schema: {q(SCHEMA)}", "approvals:"]
    for e in entries:
        lines += [f"  - checkpoint: {q(e['checkpoint'])}", f"    approved_at: {q(e['approved_at'])}",
                  f"    digest: {q(e['digest'])}", "    inputs:"]
        lines += [f"      {q(k)}: {q(v)}" for k, v in e["inputs"].items()]
    (target / FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return entry


def describe(state: dict) -> str:
    head = f"Approval ({state['checkpoint']}): {state['status']}"
    if state["status"] == "approved" and state.get("approved_at"):
        head += f" at {state['approved_at']}"
    if state["changes"]:
        head += " — changed since approval:\n" + "\n".join(f"  {c}" for c in state["changes"])
    return head
