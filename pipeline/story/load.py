"""Strict YAML loading and project-root discovery.

PyYAML's safe_load silently keeps the last of two duplicate keys, and anchors/aliases
let one part of a manifest quietly depend on another. Both are rejected here.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from yaml.events import AliasEvent
from yaml.nodes import MappingNode

ROOT_MARKER = Path("schemas") / "story-episode.v1.schema.json"


class StrictYAMLError(Exception):
    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.message = message
        self.line = line


class _StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        event = self.peek_event()
        if isinstance(event, AliasEvent) or getattr(event, "anchor", None):
            raise StrictYAMLError(
                "YAML anchors and aliases (&name / *name) are not allowed; write values out in full",
                event.start_mark.line + 1,
            )
        return super().compose_node(parent, index)

    def construct_mapping(self, node: MappingNode, deep: bool = False):
        seen: dict = {}
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError:
                raise StrictYAMLError("mapping keys must be plain values", key_node.start_mark.line + 1)
            if key in seen:
                raise StrictYAMLError(
                    f"duplicate key '{key}' (first defined on line {seen[key]})",
                    key_node.start_mark.line + 1,
                )
            seen[key] = key_node.start_mark.line + 1
        return super().construct_mapping(node, deep=deep)


def load_yaml(path: Path):
    """Load one YAML document strictly. Raises StrictYAMLError on any problem."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise StrictYAMLError("file is not valid UTF-8")
    try:
        return yaml.load(text, Loader=_StrictLoader)  # noqa: S506 - _StrictLoader derives from SafeLoader
    except StrictYAMLError:
        raise
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        problem = getattr(exc, "problem", None) or str(exc)
        raise StrictYAMLError(f"invalid YAML: {problem}", mark.line + 1 if mark else None)


def find_root(start: Path) -> Path | None:
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / ROOT_MARKER).is_file():
            return candidate
    return None


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
