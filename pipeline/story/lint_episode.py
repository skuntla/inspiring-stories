"""Episode manifest validation: pass 1 (schema), pass 2 (cross-references and rules a
schema cannot express), and the informational runtime estimate."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .findings import ERROR, WARNING, Finding
from .lint_series import SeriesCheck, check_series
from .load import StrictYAMLError, load_yaml, rel
from .schema import EPISODE_SCHEMA, check_version, validate_structure

EPISODE_FILE = "episode.yaml"

MAX_LINE_WORDS = 60
MAX_FREE_TEXT_WORDS = 12
SHOT_COUNT_SOFT = (4, 16)
MAX_TAGS_CHARS = 500
# Estimate constants: a calm all-ages pace. Informational only, never written anywhere.
REFERENCE_WPM = 140
GAP_BETWEEN_LINES = 0.4
LONG_SHOT_SECONDS = 30.0

_WORD = re.compile(r"[A-Za-z0-9]")


def count_words(text: str) -> int:
    return sum(1 for token in text.split() if _WORD.search(token))


def _tokens(text: str) -> set[str]:
    return {t.strip(".,!?;:\"'()[]—–-…") for t in text.split()}


@dataclass
class EpisodeCheck:
    findings: list[Finding] = field(default_factory=list)
    series: SeriesCheck | None = None
    estimate: dict | None = None


def check_episode(file_path: Path, root: Path, expected_id: str | None) -> EpisodeCheck:
    """Validate an episode manifest and its series bible.

    expected_id is the folder name the id must match; None skips that rule (used for the
    example episode embedded in a series brief, which does not live in episodes/).
    """
    file = rel(file_path, root)
    out = EpisodeCheck()
    try:
        doc = load_yaml(file_path)
    except StrictYAMLError as exc:
        out.findings.append(Finding(ERROR, file, f"line {exc.line}" if exc.line else "", "yaml", exc.message))
        return out
    stop = check_version(doc, EPISODE_SCHEMA, file)
    if stop:
        out.findings += stop
        return out

    series_id = doc.get("series")
    if isinstance(series_id, str):
        series_dir = root / "series" / series_id
        if (series_dir / "series.yaml").is_file():
            out.series = check_series(series_dir, root)
            out.findings += out.series.findings
        else:
            out.findings.append(Finding(ERROR, file, "series", "episode.unknown-series",
                                        f"series '{series_id}' does not exist (expected {rel(series_dir / 'series.yaml', root)})"))

    out.findings += validate_structure(doc, EPISODE_SCHEMA, root, file)
    out.findings += _lint(doc, out.series, file, expected_id)
    out.estimate = estimate_runtime(doc, out.series)
    if out.estimate:
        for shot in out.estimate["shots"]:
            if shot["seconds"] > LONG_SHOT_SECONDS:
                out.findings.append(Finding(
                    WARNING, file, f"shots[{shot['index']}]", "episode.long-shot",
                    f"shot {shot['id']} is estimated at {shot['seconds']:.1f} s of speech; "
                    f"consider splitting it (one still image held over {LONG_SHOT_SECONDS:.0f} s feels static)"))
    return out


def _lint(doc: dict, series: SeriesCheck | None, file: str, expected_id: str | None) -> list[Finding]:
    f: list[Finding] = []

    def err(path, rule, msg):
        f.append(Finding(ERROR, file, path, rule, msg))

    def warn(path, rule, msg):
        f.append(Finding(WARNING, file, path, rule, msg))

    ep_id = doc.get("id")
    if expected_id is not None and isinstance(ep_id, str) and ep_id != expected_id:
        err("id", "episode.id-matches-folder", f"id '{ep_id}' does not match its folder name '{expected_id}'")

    bible_chars = series.characters() if series and series.bible else None
    cast = [c for c in doc.get("cast", []) if isinstance(c, str)] if isinstance(doc.get("cast"), list) else []
    if bible_chars is not None:
        for i, cid in enumerate(doc.get("cast", []) if isinstance(doc.get("cast"), list) else []):
            if isinstance(cid, str) and cid not in bible_chars:
                err(f"cast[{i}]", "episode.cast-in-bible",
                    f"'{cid}' is not in series '{doc.get('series')}'; add '{cid}' to the series bible first "
                    f"(characters cannot be defined inside an episode)")
    narrators = {cid for cid, c in (bible_chars or {}).items() if c.get("kind") == "narrator"}

    declared_locations = _declared(doc, "locations", err)
    series_locations = series.locations() if series and series.bible else {}
    for loc_id, idx in declared_locations.items():
        if loc_id in series_locations:
            err(f"locations[{idx}].id", "episode.redeclared-series-location",
                f"'{loc_id}' is a recurring location of series '{doc.get('series')}'; remove this declaration "
                f"and use the series location (its description and reference images keep it consistent)")
    known_locations = set(declared_locations) | set(series_locations)
    declared_props = _declared(doc, "props", err)
    used_locations: set[str] = set()
    used_props: set[str] = set()

    shots = doc.get("shots")
    if isinstance(shots, list):
        if not shots:
            err("shots", "episode.stub",
                "the episode has no shots yet; it is still a stub. Generate the manifest with "
                f"`story brief {doc.get('series', '<series>')}` and ChatGPT, then paste it here")
        elif not SHOT_COUNT_SOFT[0] <= len(shots) <= SHOT_COUNT_SOFT[1]:
            warn("shots", "episode.shot-count",
                 f"{len(shots)} shots; most stories work best with {SHOT_COUNT_SOFT[0]}–{SHOT_COUNT_SOFT[1]}")
        for i, shot in enumerate(shots):
            if isinstance(shot, dict):
                _lint_shot(i, shot, cast, narrators, known_locations, declared_props,
                           used_locations, used_props, err)

    for loc_id, idx in declared_locations.items():
        if loc_id not in used_locations:
            warn(f"locations[{idx}]", "episode.unused-location", f"location '{loc_id}' is declared but no shot uses it")
    for prop_id, idx in declared_props.items():
        if prop_id not in used_props:
            warn(f"props[{idx}]", "episode.unused-prop", f"prop '{prop_id}' is declared but no shot uses it")

    _lint_pronunciations(doc, err, warn)

    pub = doc.get("publishing")
    thumb = pub.get("thumbnail") if isinstance(pub, dict) else None
    if isinstance(thumb, dict) and isinstance(thumb.get("characters"), list):
        for j, cid in enumerate(thumb["characters"]):
            path = f"publishing.thumbnail.characters[{j}]"
            if not isinstance(cid, str):
                continue
            if cid in narrators:
                err(path, "episode.thumbnail-narrator", "the narrator is never drawn, so it cannot appear in the thumbnail")
            elif cid not in cast:
                err(path, "episode.thumbnail-character-in-cast",
                    f"'{cid}' is not in the episode cast; list only cast members visible in the thumbnail")
    defaults = series.bible.get("defaults") if series and series.bible else None
    default_mfk = defaults.get("made_for_kids") if isinstance(defaults, dict) else None
    if (isinstance(pub, dict) and isinstance(pub.get("made_for_kids"), bool)
            and isinstance(default_mfk, bool) and pub["made_for_kids"] != default_mfk):
        warn("publishing.made_for_kids", "episode.made-for-kids-default",
             f"made_for_kids is {str(pub['made_for_kids']).lower()} but series '{doc.get('series')}' defaults to "
             f"{str(default_mfk).lower()}; confirm this episode really differs before uploading")
    if isinstance(pub, dict) and isinstance(pub.get("tags"), list):
        tags = [t for t in pub["tags"] if isinstance(t, str)]
        # YouTube counts separating commas, and quotes around tags that contain spaces.
        total = sum(len(t) + (2 if " " in t else 0) for t in tags) + max(len(tags) - 1, 0)
        if total > MAX_TAGS_CHARS:
            err("publishing.tags", "episode.tags-length",
                f"tags use {total} characters as YouTube counts them; the limit is {MAX_TAGS_CHARS}")
    return f


def _declared(doc: dict, key: str, err) -> dict[str, int]:
    out: dict[str, int] = {}
    items = doc.get(key)
    if not isinstance(items, list):
        return out
    for i, item in enumerate(items):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            if item["id"] in out:
                err(f"{key}[{i}].id", f"episode.duplicate-{key[:-1]}",
                    f"'{item['id']}' is already declared at {key}[{out[item['id']]}]")
            else:
                out[item["id"]] = i
    return out


def _lint_shot(i, shot, cast, narrators, known_locations, declared_props, used_locations, used_props, err):
    base = f"shots[{i}]"
    expected = f"s{i + 1:02d}"
    if isinstance(shot.get("id"), str) and shot["id"] != expected:
        err(f"{base}.id", "episode.shot-sequence",
            f"shot ids must run s01, s02, ... without gaps; expected '{expected}', got '{shot['id']}'")

    loc = shot.get("location")
    if isinstance(loc, str):
        used_locations.add(loc)
        if loc not in known_locations:
            err(f"{base}.location", "episode.unknown-location",
                f"location '{loc}' is declared neither under the episode's locations nor as a series location")
    if isinstance(shot.get("props"), list):
        for j, prop in enumerate(shot["props"]):
            if isinstance(prop, str):
                used_props.add(prop)
                if prop not in declared_props:
                    err(f"{base}.props[{j}]", "episode.unknown-prop", f"prop '{prop}' is not declared under props")

    for key in ("emotion",):
        _limit_words(shot.get(key), f"{base}.{key}", err)

    visible: dict[str, dict] = {}
    if isinstance(shot.get("characters"), list):
        for j, ch in enumerate(shot["characters"]):
            if not isinstance(ch, dict):
                continue
            cid = ch.get("id")
            path = f"{base}.characters[{j}]"
            _limit_words(ch.get("pose"), f"{path}.pose", err)
            _limit_words(ch.get("expression"), f"{path}.expression", err)
            if not isinstance(cid, str):
                continue
            if cid in visible:
                err(f"{path}.id", "episode.duplicate-visible", f"'{cid}' appears twice in this shot")
            visible[cid] = ch
            if cid in narrators:
                err(f"{path}.id", "episode.narrator-visible", "the narrator is never drawn, so it cannot be visible in a shot")
            elif cid not in cast:
                err(f"{path}.id", "episode.visible-in-cast", f"'{cid}' is visible in this shot but is not in the episode cast")

    if isinstance(shot.get("lines"), list):
        for j, line in enumerate(shot["lines"]):
            if isinstance(line, dict):
                _lint_line(f"{base}.lines[{j}]", line, cast, narrators, visible, err)


def _limit_words(value, path, err):
    if isinstance(value, str) and count_words(value) > MAX_FREE_TEXT_WORDS:
        err(path, "episode.free-text-length",
            f"{count_words(value)} words; keep it to {MAX_FREE_TEXT_WORDS} words or fewer")


def _lint_line(path, line, cast, narrators, visible, err):
    speaker = line.get("speaker")
    text = line.get("text")
    if isinstance(text, str) and count_words(text) > MAX_LINE_WORDS:
        err(f"{path}.text", "episode.line-length",
            f"{count_words(text)} words; the limit is {MAX_LINE_WORDS}. Split it into two lines")
    if not isinstance(speaker, str):
        return
    if speaker not in cast:
        err(f"{path}.speaker", "episode.speaker-in-cast", f"speaker '{speaker}' is not in the episode cast")
        return
    on_screen = line.get("on_screen")
    if speaker in narrators:
        if on_screen is True:
            err(f"{path}.on_screen", "episode.on-screen-speaker", "the narrator is never drawn, so its lines cannot be on_screen")
        return
    if on_screen is None:
        err(f"{path}.on_screen", "episode.on-screen-required",
            f"lines spoken by a character must say on_screen: true (mouth visible) or false (voice only)")
    elif on_screen is True:
        if speaker not in visible:
            err(f"{path}.on_screen", "episode.on-screen-speaker",
                f"'{speaker}' speaks on_screen but is not visible in this shot; add them to the shot or set on_screen: false")
        elif visible[speaker].get("facing") == "away":
            err(f"{path}.on_screen", "episode.on-screen-speaker",
                f"'{speaker}' speaks on_screen but faces away; change facing or set on_screen: false")


def _lint_pronunciations(doc, err, warn):
    pron = doc.get("pronunciations")
    if not isinstance(pron, dict):
        return
    spoken_tokens: set[str] = set()
    for shot in doc.get("shots", []) if isinstance(doc.get("shots"), list) else []:
        if isinstance(shot, dict) and isinstance(shot.get("lines"), list):
            for line in shot["lines"]:
                if isinstance(line, dict) and isinstance(line.get("text"), str):
                    spoken_tokens |= _tokens(line["text"])
    for key in pron:
        path = f"pronunciations.{key}"
        if not isinstance(key, str) or len(key.split()) != 1 or not key.strip():
            err(path, "episode.pronunciation-key", f"'{key}' must be a single word (overrides map one display word to its spoken form)")
        elif key not in spoken_tokens:
            warn(path, "episode.unused-pronunciation", f"'{key}' does not appear as a word in any line")


def estimate_runtime(doc: dict, series: SeriesCheck | None) -> dict | None:
    """Words / (REFERENCE_WPM x voice speed) + pause_after, plus a fixed gap between lines."""
    shots = doc.get("shots")
    if not isinstance(shots, list) or not shots:
        return None
    chars = series.characters() if series and series.bible else {}
    per_shot = []
    all_lines = []
    for i, shot in enumerate(shots):
        per_shot.append({"index": i, "id": shot.get("id") if isinstance(shot, dict) else None, "seconds": 0.0})
        lines = shot.get("lines") if isinstance(shot, dict) else None
        for line in lines if isinstance(lines, list) else []:
            if isinstance(line, dict) and isinstance(line.get("text"), str):
                all_lines.append((i, line))
    for n, (i, line) in enumerate(all_lines):
        voice = chars.get(line.get("speaker"), {}).get("voice")
        speed = voice.get("speed") if isinstance(voice, dict) else None
        speed = speed if isinstance(speed, (int, float)) and not isinstance(speed, bool) and speed > 0 else 1.0
        seconds = count_words(line["text"]) / (REFERENCE_WPM * speed) * 60
        pause = line.get("pause_after")
        if isinstance(pause, (int, float)) and not isinstance(pause, bool) and 0 <= pause <= 3:
            seconds += pause
        if n < len(all_lines) - 1:
            seconds += GAP_BETWEEN_LINES
        per_shot[i]["seconds"] += seconds
    for shot in per_shot:
        shot["seconds"] = round(shot["seconds"], 1)
    total = round(sum(s["seconds"] for s in per_shot), 1)
    return {"shots": per_shot, "total_seconds": total}
