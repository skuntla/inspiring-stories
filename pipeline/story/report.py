"""Render validation results as text or JSON, and map them to exit codes."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .findings import ERROR, WARNING, Finding, sort_findings

EXIT_OK = 0
EXIT_ERRORS = 1
EXIT_USAGE = 2


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    estimate: dict | None = None  # {"shots": [{"id", "seconds"}], "total_seconds"}
    approval: dict | None = None  # {"checkpoint", "status", "changes", ...}

    @property
    def errors(self) -> int:
        return sum(f.severity == ERROR for f in self.findings)

    @property
    def warnings(self) -> int:
        return sum(f.severity == WARNING for f in self.findings)

    @property
    def exit_code(self) -> int:
        return EXIT_ERRORS if self.errors else EXIT_OK


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def render_text(result: Result) -> str:
    lines = []
    for f in sort_findings(result.findings):
        where = f"{f.file}" + (f"  {f.path}" if f.path else "")
        lines.append(f"{f.severity:<7}  {where}\n         {f.message}  [{f.rule}]")
    if result.estimate:
        lines.append("")
        lines.append("Estimated spoken runtime (informational):")
        for shot in result.estimate["shots"]:
            lines.append(f"  {shot['id']}  {shot['seconds']:6.1f} s")
        lines.append(f"  total {result.estimate['total_seconds']:6.1f} s")
    lines.append("")
    lines.append(f"{_plural(result.errors, 'error')}, {_plural(result.warnings, 'warning')}")
    if result.approval:
        from .approvals import describe  # local import: approvals depends on images, which is heavier
        lines.append(describe(result.approval))
    return "\n".join(lines) + "\n"


def render_json(result: Result) -> str:
    doc = {
        "findings": [f.as_dict() for f in sort_findings(result.findings)],
        "errors": result.errors,
        "warnings": result.warnings,
        "estimate": result.estimate,
    }
    if result.approval is not None:
        doc["approval"] = result.approval
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
