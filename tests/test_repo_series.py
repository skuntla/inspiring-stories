"""Checks on the real series in this repo (not temporary copies).

Every series must validate, its example episode must validate, and any committed
ChatGPT documents must match a fresh render, so what is on GitHub is never stale.
Regenerate with:
  story brief <series> --out series/<series>/chatgpt-project-instructions.md
  story brief <series> --full --out series/<series>/chatgpt-reference.md
  story brief <series> --story --out series/<series>/chatgpt-story-prompt.md
"""
import pytest

from conftest import REPO
from story.brief import (PROJECT_INSTRUCTIONS_FILE, PROJECT_INSTRUCTIONS_MAX, REFERENCE_FILE, STORY_PROMPT_FILE,
                         render_brief, render_project_instructions, render_story_prompt)
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
def test_committed_reference_is_current(series_dir):
    committed = series_dir / REFERENCE_FILE
    if not committed.exists():
        pytest.skip("no committed reference for this series")
    fresh = render_brief(check_series(series_dir, REPO).bible, series_dir, REPO)
    assert committed.read_text(encoding="utf-8") == fresh, (
        f"{committed.relative_to(REPO)} is stale; run "
        f"`story brief {series_dir.name} --full --out {committed.relative_to(REPO)}`")


@pytest.mark.parametrize("series_dir", SERIES_DIRS, ids=lambda p: p.name)
def test_committed_project_instructions_are_current_and_fit(series_dir):
    committed = series_dir / PROJECT_INSTRUCTIONS_FILE
    if not committed.exists():
        pytest.skip("no committed Project instructions for this series")
    text = committed.read_text(encoding="utf-8")
    assert len(text) <= PROJECT_INSTRUCTIONS_MAX, f"{len(text)} characters; ChatGPT accepts {PROJECT_INSTRUCTIONS_MAX}"
    fresh = render_project_instructions(check_series(series_dir, REPO).bible, REPO)
    assert text == fresh, (
        f"{committed.relative_to(REPO)} is stale; run "
        f"`story brief {series_dir.name} --out {committed.relative_to(REPO)}`")


@pytest.mark.parametrize("series_dir", SERIES_DIRS, ids=lambda p: p.name)
def test_committed_story_prompt_is_current(series_dir):
    committed = series_dir / STORY_PROMPT_FILE
    if not committed.exists():
        pytest.skip("no committed story prompt for this series")
    fresh = render_story_prompt(check_series(series_dir, REPO).bible)
    assert committed.read_text(encoding="utf-8") == fresh, (
        f"{committed.relative_to(REPO)} is stale; run "
        f"`story brief {series_dir.name} --story --out {committed.relative_to(REPO)}`")


@pytest.mark.parametrize("name", ["willow-meadow", "quiet-lessons"])
def test_production_series_has_a_story_prompt(name):
    """ChatGPT writes plain stories; each production series ships the prompt that asks for them."""
    assert (REPO / "series" / name / STORY_PROMPT_FILE).is_file()


def test_production_series_is_present():
    assert (REPO / "series" / "willow-meadow" / "series.yaml").is_file()
