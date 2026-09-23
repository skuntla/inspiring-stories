"""Hash-bound approval of the rendered preview. An approval records the SHA-256 of every input it
covers, so any later change shows up as stale instead of silently carrying the approval over."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .load import StrictYAMLError, load_yaml, rel
from .render import PREVIEW_FILE, RENDER_DIR, Plan
from .timeline import TIMELINE_FILE
from .voice import SPEECH_FILE

SCHEMA = "story-approvals/v1"
FILE = "approvals.yaml"
CHECKPOINTS = ("preview",)


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"


def collect_inputs(root: Path, episode_dir: Path, series_dir: Path, plan: Plan) -> dict[str, str]:
    """Everything the preview was made from: story, speech, timeline, the MP4 and renderer source."""
    files = [episode_dir / "episode.yaml", series_dir / "series.yaml", episode_dir / SPEECH_FILE,
             episode_dir / TIMELINE_FILE, episode_dir / PREVIEW_FILE, *plan.files()]
    src = root / RENDER_DIR / "src"
    files += sorted((src / "kit").glob("*.ts*")) + [src / "Episode.tsx"]
    return {rel(p, root): _sha(p) for p in sorted(set(files))}


def digest(inputs: dict[str, str]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_entries(episode_dir: Path) -> list[dict]:
    path = episode_dir / FILE
    if not path.is_file():
        return []
    doc = load_yaml(path)
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA or not isinstance(doc.get("approvals"), list):
        raise StrictYAMLError(f"{FILE} must declare schema '{SCHEMA}' and an 'approvals' list")
    return doc["approvals"]


def status(entries: list[dict], inputs: dict[str, str], checkpoint: str = "preview") -> dict:
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


def describe(state: dict) -> str:
    head = f"Approval ({state['checkpoint']}): {state['status']}"
    if state["status"] == "approved" and state.get("approved_at"):
        head += f" at {state['approved_at']}"
    if state["changes"]:
        head += " — changed since approval:\n" + "\n".join(f"  {c}" for c in state["changes"])
    return head


def append(episode_dir: Path, checkpoint: str, inputs: dict[str, str], now: datetime | None = None) -> dict:
    entries = load_entries(episode_dir)
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries.append({"checkpoint": checkpoint, "approved_at": stamp, "digest": digest(inputs), "inputs": inputs})
    q = json.dumps  # JSON strings are valid double-quoted YAML scalars
    lines = [f"schema: {q(SCHEMA)}", "approvals:"]
    for e in entries:
        lines += [f"  - checkpoint: {q(e['checkpoint'])}", f"    approved_at: {q(e['approved_at'])}",
                  f"    digest: {q(e['digest'])}", "    inputs:"]
        lines += [f"      {q(k)}: {q(v)}" for k, v in e["inputs"].items()]
    (episode_dir / FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return entries[-1]
