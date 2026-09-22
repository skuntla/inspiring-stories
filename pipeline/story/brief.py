"""Render the per-series ChatGPT brief from the schema vocabulary, the series bible and the
series' example episode, so the brief can never drift from what the validator accepts."""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from string import Template

from .lint_episode import MAX_FREE_TEXT_WORDS, MAX_LINE_WORDS, SHOT_COUNT_SOFT
from .schema import load_vocabulary

EXAMPLE_FILE = "example-episode.yaml"
SHOT_MAX = 30

_FIELD_FOR_VOCAB = {
    "timeOfDay": "shots[].time_of_day",
    "position": "shots[].characters[].position",
    "facing": "shots[].characters[].facing",
    "cameraMove": "shots[].camera.move",
    "cameraIntensity": "shots[].camera.intensity",
    "atmosphere": "shots[].atmosphere[]",
    "ambience": "shots[].ambience",
    "delivery": "shots[].lines[].delivery",
}


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def render_brief(bible: dict, series_dir: Path, root: Path) -> str:
    vocab = load_vocabulary(root)
    vocab_rows = "\n".join(
        f"| `{field}` | {', '.join(f'`{v}`' for v in vocab[name])} |"
        for name, field in _FIELD_FOR_VOCAB.items()
    )
    cast_rows = "\n".join(
        f"| `{c['id']}` | {_cell(c['name'])} | {'narrator (never drawn)' if c['kind'] == 'narrator' else 'character'} "
        f"| {_cell(c.get('description', 'Voice only.'))} |"
        for c in bible["characters"]
    )
    example = (series_dir / EXAMPLE_FILE).read_text(encoding="utf-8").rstrip("\n")
    template = Template(resources.files("story").joinpath("templates/brief.md.tmpl").read_text(encoding="utf-8"))
    return template.substitute(
        series_id=bible["id"],
        series_title=bible["title"],
        shot_soft_min=SHOT_COUNT_SOFT[0],
        shot_soft_max=SHOT_COUNT_SOFT[1],
        shot_max=SHOT_MAX,
        max_line_words=MAX_LINE_WORDS,
        max_free_words=MAX_FREE_TEXT_WORDS,
        vocabulary_rows=vocab_rows,
        cast_rows=cast_rows,
        example=example,
    )
