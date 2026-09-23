"""Render the per-series ChatGPT documents from the schema vocabulary, the series bible and the
series' example episode, so they can never drift from what the validator accepts.

Two renderings:
- compact Project instructions (`render_project_instructions`), sized to fit ChatGPT's
  Project-instructions field (hard limit PROJECT_INSTRUCTIONS_MAX characters);
- the full reference contract (`render_brief`) with tables and a complete example episode,
  kept in the repo and optionally uploaded as a Project file.
"""
from __future__ import annotations

from importlib import resources
from pathlib import Path
from string import Template

from .lint_episode import MAX_FREE_TEXT_WORDS, MAX_LINE_WORDS, SHOT_COUNT_SOFT
from .schema import load_vocabulary

EXAMPLE_FILE = "example-episode.yaml"
PROJECT_INSTRUCTIONS_FILE = "chatgpt-project-instructions.md"
REFERENCE_FILE = "chatgpt-reference.md"
SHOT_MAX = 30
# ChatGPT's Project-instructions field accepts at most 8,000 characters.
PROJECT_INSTRUCTIONS_MAX = 8000
PROJECT_INSTRUCTIONS_TARGET = 7500

_FIELD_FOR_VOCAB = {
    "timeOfDay": "shots[].time_of_day",
    "position": "shots[].characters[].position",
    "stance": "shots[].characters[].stance",
    "mood": "shots[].characters[].mood",
    "facing": "shots[].characters[].facing",
    "cameraMove": "shots[].camera.move",
    "cameraIntensity": "shots[].camera.intensity",
    "framing": "shots[].camera.framing",
    "atmosphere": "shots[].atmosphere[]",
    "ambience": "shots[].ambience",
    "delivery": "shots[].lines[].delivery",
    "music": "music",
}


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def _template(name: str) -> Template:
    return Template(resources.files("story").joinpath(f"templates/{name}").read_text(encoding="utf-8"))


def _common(bible: dict) -> dict:
    audience = bible.get("audience")
    defaults = bible.get("defaults") if isinstance(bible.get("defaults"), dict) else {}
    default_mfk = defaults.get("made_for_kids")
    return {
        "series_id": bible["id"],
        "series_title": bible["title"],
        "shot_soft_min": SHOT_COUNT_SOFT[0],
        "shot_soft_max": SHOT_COUNT_SOFT[1],
        "shot_max": SHOT_MAX,
        "max_line_words": MAX_LINE_WORDS,
        "max_free_words": MAX_FREE_TEXT_WORDS,
        "audience_sentence": f" Audience: {' '.join(audience.split())}" if isinstance(audience, str) else "",
        "default_mfk": str(default_mfk).lower() if isinstance(default_mfk, bool) else None,
    }


def _locations(bible: dict) -> list[tuple[str, str]]:
    locs = bible.get("locations") if isinstance(bible.get("locations"), list) else []
    return [(loc["id"], " ".join(loc["description"].split())) for loc in locs]


def _shared(root: Path) -> list[tuple[str, str]]:
    """Reusable close-ups and cards from the shared component library (render/src/common/locations)."""
    from .render import common_library
    return sorted(common_library(root)["locations"].items())


def render_brief(bible: dict, series_dir: Path, root: Path) -> str:
    """The full reference contract."""
    ctx = _common(bible)
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
    value = ctx.pop("default_mfk")
    if value is not None:
        mfk_blocking = ""
        mfk_note = (f"\n   `made_for_kids` is **not** blocking in this series: use the series default "
                    f"`{value}` unless the producer explicitly says otherwise.")
        mfk_comment = f"series default is {value}; change only if the producer says so"
    else:
        mfk_blocking = ("   - Whether the video is **made for kids** (primarily aimed at children, as YouTube defines\n"
                        "     it) has not been stated in this conversation.\n")
        mfk_note = ""
        mfk_comment = "exactly as the producer stated it"
    return _template("brief.md.tmpl").substitute(
        ctx,
        vocabulary_rows=vocab_rows,
        cast_rows=cast_rows,
        locations_section=((
            "\n## Recurring locations\n\n"
            "These places recur across the series. When a shot takes place in one, use its id as the shot's\n"
            "`location` and do **not** declare it under `locations`.\n\n"
            "| id | description |\n|---|---|\n"
            + "\n".join(f"| `{lid}` | {_cell(desc)} |" for lid, desc in _locations(bible)) + "\n"
        ) if _locations(bible) else "") + ((
            "\n## Ready-made shots\n\n"
            "These close-ups and cards are already drawn and work in any episode. To use one, declare it under\n"
            "`locations` with exactly this id (and a short description), then use it as a shot's `location`.\n"
            "They show no characters: a line spoken over one is off-screen (`on_screen: false`) or narration.\n\n"
            "| id | what it shows |\n|---|---|\n"
            + "\n".join(f"| `{lid}` | {_cell(desc)} |" for lid, desc in _shared(root)) + "\n"
        ) if _shared(root) else ""),
        example=(series_dir / EXAMPLE_FILE).read_text(encoding="utf-8").rstrip("\n"),
        made_for_kids_blocking=mfk_blocking,
        made_for_kids_default_note=mfk_note,
        made_for_kids_comment=mfk_comment,
    )


def render_project_instructions(bible: dict, root: Path) -> str:
    """The compact rendering installed as ChatGPT Project instructions."""
    ctx = _common(bible)
    vocab = load_vocabulary(root)
    vocab_lines = "\n".join(
        f"- {field.removeprefix('shots[].')}: {', '.join(vocab[name])}"
        for name, field in _FIELD_FOR_VOCAB.items()
    )
    cast_lines = "\n".join(
        f"- {c['id']}: {' '.join(c['name'].split())}"
        + (" (narrator, never drawn)" if c["kind"] == "narrator" else f". {' '.join(c.get('description', '').split())}")
        for c in bible["characters"]
    )
    value = ctx.pop("default_mfk")
    if value is not None:
        mfk_blocking = ""
        mfk_note = f" made_for_kids is not blocking: use the series default {value} unless the producer says otherwise."
        mfk_value = value
    else:
        mfk_blocking = "   - made_for_kids (video primarily aimed at children, per YouTube) not stated\n"
        mfk_note = ""
        mfk_value = "false            # exactly as the producer stated"
    return _template("project-instructions.md.tmpl").substitute(
        ctx,
        vocabulary_lines=vocab_lines,
        cast_lines=cast_lines,
        locations_section=((
            "\n## Recurring locations\nUse these ids directly as a shot's location; never redeclare them.\n"
            + "\n".join(f"- {lid}: {desc}" for lid, desc in _locations(bible)) + "\n"
        ) if _locations(bible) else "") + ((
            "\n## Ready-made shots\nAlready drawn, any episode: declare under locations with this id, then use it. "
            "No characters appear; lines over them are off-screen or narration.\n"
            + "\n".join(f"- {lid}: {desc}" for lid, desc in _shared(root)) + "\n"
        ) if _shared(root) else ""),
        made_for_kids_blocking=mfk_blocking,
        made_for_kids_default_note=mfk_note,
        made_for_kids_value=mfk_value,
    )
