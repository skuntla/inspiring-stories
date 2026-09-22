import json

from story.findings import ERROR, WARNING, Finding, sort_findings
from story.report import EXIT_ERRORS, EXIT_OK, Result, render_json, render_text


def _f(sev, path, rule="r", file="e.yaml"):
    return Finding(sev, file, path, rule, "msg")


def test_sort_is_natural_by_path():
    ordered = sort_findings([_f(ERROR, "shots[10].id"), _f(ERROR, "shots[2].id"), _f(ERROR, "cast[0]")])
    assert [f.path for f in ordered] == ["cast[0]", "shots[2].id", "shots[10].id"]


def test_duplicate_findings_collapse():
    assert len(sort_findings([_f(ERROR, "a"), _f(ERROR, "a")])) == 1


def test_exit_codes():
    assert Result([_f(WARNING, "a")]).exit_code == EXIT_OK
    assert Result([_f(WARNING, "a"), _f(ERROR, "b")]).exit_code == EXIT_ERRORS
    assert Result([]).exit_code == EXIT_OK


def test_text_report_counts():
    text = render_text(Result([_f(WARNING, "a"), _f(ERROR, "b"), _f(ERROR, "c")]))
    assert text.rstrip().endswith("2 errors, 1 warning")


def test_json_report_shape():
    doc = json.loads(render_json(Result([_f(ERROR, "b")], estimate={"shots": [], "total_seconds": 0})))
    assert doc["errors"] == 1 and doc["warnings"] == 0
    assert doc["findings"][0] == {"severity": "error", "file": "e.yaml", "path": "b", "rule": "r", "message": "msg"}


def test_validation_output_is_identical_across_runs(project, capsys):
    doc = project.episode()
    doc["shots"][1]["camera"]["move"] = "dolly_zoom"
    del doc["title"]
    project.write_episode(doc)
    first = project.run("validate", str(project.episode_dir), capsys=capsys)
    second = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert first == second
    first_json = project.run("validate", str(project.episode_dir), "--json", capsys=capsys)
    second_json = project.run("validate", str(project.episode_dir), "--json", capsys=capsys)
    assert first_json == second_json
