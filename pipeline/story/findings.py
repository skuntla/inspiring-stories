"""Finding model shared by every validation pass."""
from __future__ import annotations

import re
from dataclasses import dataclass

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    severity: str  # ERROR | WARNING
    file: str  # path relative to the project root, POSIX separators
    path: str  # field path such as "shots[2].lines[0].speaker"; "" for the whole file
    rule: str  # stable rule id such as "schema.enum" or "episode.cast-in-bible"
    message: str

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "file": self.file,
            "path": self.path,
            "rule": self.rule,
            "message": self.message,
        }


def _natural_key(text: str) -> tuple:
    # "shots[10]" must sort after "shots[2]".
    return tuple(int(p) if p.isdigit() else p for p in re.split(r"(\d+)", text))


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        set(findings),
        key=lambda f: (f.file, _natural_key(f.path), f.rule, f.message, f.severity),
    )


def format_path(parts) -> str:
    """Render a sequence of keys/indexes as `a.b[0].c`."""
    out = ""
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += ("." if out else "") + str(part)
    return out
