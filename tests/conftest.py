"""Test fixtures.

Every test runs against a throwaway project root built from the repo's real schemas and
the golden example series (series/example-meadow). Invalid cases are produced by applying
one mutation to the golden documents, so each rule is exercised in isolation.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from story.cli import main

REPO = Path(__file__).resolve().parents[1]
SERIES_ID = "example-meadow"
EPISODE_ID = "2026-01-01-the-lantern-seed"


class Project:
    def __init__(self, root: Path):
        self.root = root
        self.series_dir = root / "series" / SERIES_ID
        self.episode_dir = root / "episodes" / EPISODE_ID

    # documents -----------------------------------------------------------------
    def series(self) -> dict:
        return yaml.safe_load((self.series_dir / "series.yaml").read_text())

    def episode(self) -> dict:
        return yaml.safe_load((self.episode_dir / "episode.yaml").read_text())

    def write_series(self, doc: dict) -> None:
        (self.series_dir / "series.yaml").write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

    def write_episode(self, doc: dict, folder: Path | None = None) -> Path:
        folder = folder or self.episode_dir
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "episode.yaml").write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
        return folder

    # running the CLI -----------------------------------------------------------
    def run(self, *args: str, capsys) -> tuple[int, str, str]:
        code = main(["--root", str(self.root), *args])
        out = capsys.readouterr()
        return code, out.out, out.err


@pytest.fixture
def project(tmp_path: Path) -> Project:
    root = tmp_path / "proj"
    shutil.copytree(REPO / "schemas", root / "schemas")
    shutil.copytree(REPO / "series" / SERIES_ID, root / "series" / SERIES_ID)
    p = Project(root)
    p.episode_dir.mkdir(parents=True)
    shutil.copy(p.series_dir / "example-episode.yaml", p.episode_dir / "episode.yaml")
    return p


def rules(findings, severity: str | None = None) -> set[str]:
    return {f.rule for f in findings if severity is None or f.severity == severity}
