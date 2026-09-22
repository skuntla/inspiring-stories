from conftest import rules
from story.lint_episode import check_episode, count_words, estimate_runtime
from story.lint_series import check_series


def test_count_words_ignores_punctuation_only_tokens():
    # "—" is not a word; "100%" is.
    assert count_words("Oh! It's glowing — truly, 100% glowing.") == 6


def test_estimate_matches_hand_computation(project):
    series = check_series(project.series_dir, project.root)
    doc = {
        "shots": [
            {"id": "s01", "lines": [
                # narrator speed 0.95: 14 words / (140 * 0.95) * 60 = 6.3158 s, + pause 1.0, + gap 0.4
                {"speaker": "narrator", "text": " ".join(["word"] * 14), "pause_after": 1.0},
                # pip speed 1.05: 7 words / (140 * 1.05) * 60 = 2.8571 s, + gap 0.4
                {"speaker": "pip", "text": " ".join(["word"] * 7), "on_screen": True},
            ]},
            {"id": "s02", "lines": [
                # bramble speed 0.9: 21 words / (140 * 0.9) * 60 = 10.0 s, last line: no gap
                {"speaker": "bramble", "text": " ".join(["word"] * 21), "on_screen": True},
            ]},
        ]
    }
    est = estimate_runtime(doc, series)
    s01 = 14 / (140 * 0.95) * 60 + 1.0 + 0.4 + 7 / (140 * 1.05) * 60 + 0.4
    assert est["shots"][0]["seconds"] == round(s01, 1) == 11.0
    assert est["shots"][1]["seconds"] == 10.0
    assert est["total_seconds"] == 21.0


def test_long_shot_warns(project):
    doc = project.episode()
    doc["shots"][0]["lines"] = [
        {"speaker": "narrator", "text": " ".join(["word"] * 50), "delivery": "warm", "pause_after": 3}
        for _ in range(2)
    ]
    project.write_episode(doc)
    result = check_episode(project.episode_dir / "episode.yaml", project.root, None)
    assert "episode.long-shot" in rules(result.findings, "warning")


def test_estimate_is_reported_by_validate(project, capsys):
    code, out, _ = project.run("validate", str(project.episode_dir), capsys=capsys)
    assert code == 0
    assert "Estimated spoken runtime" in out and "s01" in out and "total" in out
