"""Checks on the real series in this repo (not temporary copies).

Every series must validate, its example episode must validate, and any committed
ChatGPT instructions must match a fresh render, so what is on GitHub is never stale.
Regenerate with: story brief <series> --out series/<series>/chatgpt-instructions.md
"""
import pytest

from conftest import REPO
from story.brief import render_brief
from story.lint_episode import check_episode
from story.lint_series import check_series

SERIES_DIRS = sorted(p.parent for p in (REPO / "series").glob("*/series.yaml"))


@pytest.mark.parametrize("series_dir", SERIES_DIRS, ids=lambda p: p.name)
def test_series_and_example_validate(series_dir):
    series = check_series(series_dir, REPO)
    assert [f for f in series.findings if f.severity == "error"] == []
    example = check_episode(series_dir / "example-episode.yaml", REPO, expected_id=None)
    assert [f for f in example.findings if f.severity == "error"] == []


@pytest.mark.parametrize("series_dir", SERIES_DIRS, ids=lambda p: p.name)
def test_committed_instructions_are_current(series_dir):
    committed = series_dir / "chatgpt-instructions.md"
    if not committed.exists():
        pytest.skip("no committed instructions for this series")
    fresh = render_brief(check_series(series_dir, REPO).bible, series_dir, REPO)
    assert committed.read_text(encoding="utf-8") == fresh, (
        f"{committed.relative_to(REPO)} is stale; run "
        f"`story brief {series_dir.name} --out {committed.relative_to(REPO)}`")


def test_production_series_is_present():
    assert (REPO / "series" / "willow-meadow" / "series.yaml").is_file()
