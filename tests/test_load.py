import pytest

from story.load import StrictYAMLError, find_root, load_yaml


def test_duplicate_key_is_rejected(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("title: one\nlogline: x\ntitle: two\n")
    with pytest.raises(StrictYAMLError) as exc:
        load_yaml(f)
    assert "duplicate key 'title'" in exc.value.message
    assert exc.value.line == 3


def test_duplicate_key_in_nested_mapping_is_rejected(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("camera:\n  move: static\n  move: push_in\n")
    with pytest.raises(StrictYAMLError, match="duplicate key 'move'"):
        load_yaml(f)


def test_alias_is_rejected(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("a: &x hello\nb: *x\n")
    with pytest.raises(StrictYAMLError, match="anchors and aliases"):
        load_yaml(f)


def test_anchor_alone_is_rejected(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("a: &x hello\n")
    with pytest.raises(StrictYAMLError, match="anchors and aliases"):
        load_yaml(f)


def test_syntax_error_reports_line(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text("a: [1, 2\nb: 3\n")
    with pytest.raises(StrictYAMLError) as exc:
        load_yaml(f)
    assert exc.value.message.startswith("invalid YAML")
    assert exc.value.line is not None


def test_plain_document_loads(tmp_path):
    f = tmp_path / "a.yaml"
    f.write_text('a: "x"\nb: [1, 2]\n')
    assert load_yaml(f) == {"a": "x", "b": [1, 2]}


def test_find_root_walks_up_to_schemas(project):
    nested = project.episode_dir
    assert find_root(nested) == project.root.resolve()


def test_find_root_returns_none_outside_a_project(tmp_path):
    assert find_root(tmp_path) is None
