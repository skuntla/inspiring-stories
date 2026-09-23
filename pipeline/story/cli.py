"""`story` command-line entry point.

Exit codes: 0 success (warnings allowed), 1 validation or command errors, 2 usage errors.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from .brief import (EXAMPLE_FILE, PROJECT_INSTRUCTIONS_MAX, PROJECT_INSTRUCTIONS_TARGET,
                    render_brief, render_project_instructions)
from .lint_episode import EPISODE_FILE, check_episode
from .lint_series import SERIES_FILE, check_series
from .load import find_root
from .report import EXIT_ERRORS, EXIT_OK, EXIT_USAGE, Result, render_json, render_text


class UsageError(Exception):
    pass


def slugify(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")


def _root(args, near: Path | None = None) -> Path:
    if args.root:
        root = Path(args.root).resolve()
        if not (root / "schemas").is_dir():
            raise UsageError(f"--root {args.root} has no schemas/ directory")
        return root
    root = (near and find_root(near)) or find_root(Path.cwd())
    if root is None:
        raise UsageError("could not find the project root (a directory containing schemas/); pass --root")
    return root


def _emit(result: Result, as_json: bool, stream=None) -> None:
    (stream or sys.stdout).write(render_json(result) if as_json else render_text(result))


def _target(args) -> tuple[str, Path, Path]:
    """Resolve args.path to ("episode" | "series", folder, project root)."""
    target = Path(args.path)
    if not target.exists():
        raise UsageError(f"path not found: {args.path}")
    if target.is_file():
        target = target.parent
    root = _root(args, target)
    if (target / EPISODE_FILE).is_file():
        return "episode", target, root
    if (target / SERIES_FILE).is_file():
        return "series", target, root
    raise UsageError(f"{args.path} contains neither {EPISODE_FILE} nor {SERIES_FILE}")


def _checked(kind: str, target: Path, root: Path) -> Result:
    if kind == "episode":
        check = check_episode(target / EPISODE_FILE, root, expected_id=target.resolve().name)
        return Result(findings=check.findings, estimate=check.estimate)
    return Result(findings=check_series(target, root).findings)


def cmd_validate(args) -> int:
    kind, target, root = _target(args)
    result = _checked(kind, target, root)
    _emit(result, args.json)
    return result.exit_code


def _series_dir(root: Path, series_id: str) -> Path | None:
    d = root / "series" / series_id
    return d if (d / SERIES_FILE).is_file() else None


_STUB = """\
# Stub created by `story new`. Generate the full manifest with:
#   story brief {series}
# paste the brief into ChatGPT, then replace this file's contents with its YAML answer,
# keeping the id below. Check it with: story validate {folder}
schema: "story-episode/v1"
id: "{id}"
series: "{series}"
title: "{title}"
logline: ""
language: "en"
content_rating: "all-ages"
source:
  kind: "original"
cast: []
locations: []
shots: []
publishing:
  title: "{title}"
  description: ""
  tags: []
  made_for_kids: false
  thumbnail:
    hook: ""
    concept: ""
"""


def cmd_new(args) -> int:
    root = _root(args)
    try:
        day = date.fromisoformat(args.date) if args.date else date.today()
    except ValueError:
        raise UsageError(f"--date must be YYYY-MM-DD, got '{args.date}'")
    slug = slugify(args.title)
    if not slug:
        raise UsageError("the title must contain at least one letter or digit")
    if _series_dir(root, args.series) is None:
        print(f"error: series '{args.series}' does not exist (expected series/{args.series}/{SERIES_FILE})", file=sys.stderr)
        return EXIT_ERRORS
    episode_id = f"{day.isoformat()}-{slug}"
    folder = root / "episodes" / episode_id
    manifest = folder / EPISODE_FILE
    if manifest.exists():
        print(f"error: {manifest.relative_to(root)} already exists; refusing to overwrite it", file=sys.stderr)
        return EXIT_ERRORS
    folder.mkdir(parents=True, exist_ok=True)
    title = args.title.replace("\\", "\\\\").replace('"', '\\"')
    manifest.write_text(_STUB.format(id=episode_id, series=args.series, title=title,
                                     folder=f"episodes/{episode_id}"), encoding="utf-8")
    print(f"created {manifest.relative_to(root)}")
    return EXIT_OK


def cmd_brief(args) -> int:
    root = _root(args)
    series_dir = _series_dir(root, args.series)
    if series_dir is None:
        print(f"error: series '{args.series}' does not exist (expected series/{args.series}/{SERIES_FILE})", file=sys.stderr)
        return EXIT_ERRORS
    series = check_series(series_dir, root)
    result = Result(findings=list(series.findings))
    example = series_dir / EXAMPLE_FILE
    if not example.is_file():
        print(f"error: series '{args.series}' has no {EXAMPLE_FILE}; the brief needs a valid example", file=sys.stderr)
        return EXIT_ERRORS
    ex = check_episode(example, root, expected_id=None)
    result.findings += [f for f in ex.findings if f not in result.findings]
    if result.errors:
        print("error: the brief was not written because the series or its example has errors:", file=sys.stderr)
        _emit(result, False, sys.stderr)
        return EXIT_ERRORS
    if args.full:
        text = render_brief(series.bible, series_dir, root)
    else:
        text = render_project_instructions(series.bible, root)
        if len(text) > PROJECT_INSTRUCTIONS_MAX:
            print(f"error: the Project instructions are {len(text)} characters; ChatGPT accepts at most "
                  f"{PROJECT_INSTRUCTIONS_MAX}. Shorten the series (e.g. character descriptions); nothing was written",
                  file=sys.stderr)
            return EXIT_ERRORS
        if len(text) > PROJECT_INSTRUCTIONS_TARGET:
            print(f"warning: the Project instructions are {len(text)} characters, above the "
                  f"{PROJECT_INSTRUCTIONS_TARGET}-character safety target (hard limit {PROJECT_INSTRUCTIONS_MAX})",
                  file=sys.stderr)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({len(text)} characters)", file=sys.stderr)
    else:
        sys.stdout.write(text)
    if result.warnings:
        print(f"note: {result.warnings} warning(s); run `story validate series/{args.series}` for details", file=sys.stderr)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="story", description="Local story-to-video pipeline.")
    p.add_argument("--root", help="project root (default: nearest directory containing schemas/)")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="validate an episode folder or a series folder")
    v.add_argument("path")
    v.add_argument("--json", action="store_true", help="machine-readable output")
    v.set_defaults(func=cmd_validate)

    n = sub.add_parser("new", help="scaffold a new episode")
    n.add_argument("series")
    n.add_argument("title")
    n.add_argument("--date", help="episode date YYYY-MM-DD (default: today)")
    n.set_defaults(func=cmd_new)

    b = sub.add_parser("brief", help="generate the ChatGPT Project instructions for a series")
    b.add_argument("series")
    b.add_argument("--full", action="store_true",
                   help="render the full reference contract instead of the compact Project instructions")
    b.add_argument("--out", help="write to this file instead of stdout")
    b.set_defaults(func=cmd_brief)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse exits 2 on usage errors, 0 on --help
        return int(exc.code or 0)
    try:
        return args.func(args)
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
