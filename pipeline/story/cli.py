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
from .approvals import CHECKPOINT, FILE as APPROVALS_FILE, append, collect_inputs, load_entries, status
from .findings import ERROR, Finding
from .images import intake, write_contact_sheet, write_metadata
from .load import StrictYAMLError, find_root, load_yaml, rel
from .prompts import EpisodeContext, SeriesContext, episode_pack, series_pack, write_pack
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


def _checked(kind: str, target: Path, root: Path) -> tuple[Result, SeriesContext | None]:
    """Validate the target; return its findings and, when valid, a prompt context."""
    if kind == "episode":
        check = check_episode(target / EPISODE_FILE, root, expected_id=target.resolve().name)
        result = Result(findings=check.findings, estimate=check.estimate)
        if result.errors:
            return result, None
        doc = load_yaml(target / EPISODE_FILE)
        return result, EpisodeContext(root, root / "series" / doc["series"], check.series.bible, target, doc)
    check = check_series(target, root)
    result = Result(findings=check.findings)
    return result, (None if result.errors else SeriesContext(root, target, check.bible))


def cmd_validate(args) -> int:
    kind, target, root = _target(args)
    result, _ = _checked(kind, target, root)
    _emit(result, args.json)
    return result.exit_code


def cmd_prompts(args) -> int:
    kind, target, root = _target(args)
    result, ctx = _checked(kind, target, root)
    if ctx is None:
        print("error: no prompts were written because of these errors:", file=sys.stderr)
        _emit(result, False, sys.stderr)
        return EXIT_ERRORS
    shown = rel(target, root)
    if kind == "episode":
        files = episode_pack(ctx)
        heading = f"Gemini prompt pack: {ctx.doc['title']}"
        steps = [f"Run `story images {shown}`.", f"Review `{shown}/build/contact-sheet.png`.",
                 f"Run `story approve {shown} images`.", f"Commit `{shown}/images/` and `{shown}/approvals.yaml`."]
        built_from = ctx.digests(target / EPISODE_FILE)
    else:
        files = series_pack(ctx)
        heading = f"Gemini reference pack: {ctx.bible['title']}"
        steps = [f"Run `story images {shown}`.", f"Review `{shown}/build/contact-sheet.png`.",
                 f"Run `story approve {shown} references`.",
                 f"Commit the reference images and `{shown}/approvals.yaml`."]
        built_from = ctx.digests()
    out, missing = write_pack(target, files, heading, steps, built_from)
    print(f"wrote {len(files)} prompt files and index.md to {rel(out, root)}")
    if kind == "episode" and missing:
        print(f"warning: {len(missing)} attachment(s) do not exist yet; generate the series references and "
              f"location anchors first:", file=sys.stderr)
        for a in missing:
            print(f"  {a.path}", file=sys.stderr)
    return EXIT_OK


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


def _intake(kind, target, root):
    """Validate, then check images; returns (result, ctx, records, inputs) or stops on validation errors."""
    result, ctx = _checked(kind, target, root)
    if ctx is None:
        return result, None, [], {}
    findings, records = intake(kind, ctx)
    inputs = collect_inputs(kind, ctx, records)
    try:
        entries = load_entries(target)
    except StrictYAMLError as exc:
        findings.append(Finding(ERROR, rel(target / APPROVALS_FILE, root), "", "approvals", exc.message))
        entries = []
    return Result(findings=findings, approval=status(entries, CHECKPOINT[kind], inputs)), ctx, records, inputs


def cmd_images(args) -> int:
    kind, target, root = _target(args)
    result, ctx, records, _ = _intake(kind, target, root)
    if ctx is not None:
        manifest = [target / EPISODE_FILE] if kind == "episode" else []
        write_metadata(target, manifest + [ctx.series_dir / SERIES_FILE], records, root)
        sheet = write_contact_sheet(target, records)
        print(f"wrote {rel(target / 'build' / 'images.json', root)} and {rel(sheet, root)}", file=sys.stderr)
    _emit(result, args.json)
    return result.exit_code


def cmd_approve(args) -> int:
    kind, target, root = _target(args)
    if args.checkpoint != CHECKPOINT[kind]:
        raise UsageError(f"unknown checkpoint '{args.checkpoint}' for {'an episode' if kind == 'episode' else 'a series'};"
                         f" supported: {CHECKPOINT[kind]} (episodes: images; series: references)")
    result, ctx, _, inputs = _intake(kind, target, root)
    if result.errors:
        print(f"error: not approved; `story images {rel(target, root)}` must report no errors first:", file=sys.stderr)
        result.approval = None
        _emit(result, False, sys.stderr)
        return EXIT_ERRORS
    entry = append(target, args.checkpoint, inputs)
    print(f"approved {args.checkpoint} at {entry['approved_at']} ({len(inputs)} inputs, {entry['digest'][:19]}…); "
          f"recorded in {rel(target / APPROVALS_FILE, root)}")
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
    pr = sub.add_parser("prompts", help="write the Gemini prompt pack for an episode or a series")
    pr.add_argument("path")
    pr.set_defaults(func=cmd_prompts)

    im = sub.add_parser("images", help="check the images of an episode or series and build the contact sheet")
    im.add_argument("path")
    im.add_argument("--json", action="store_true", help="machine-readable output")
    im.set_defaults(func=cmd_images)

    ap = sub.add_parser("approve", help="record approval of an episode's images or a series' references")
    ap.add_argument("path")
    ap.add_argument("checkpoint", help="images (episode) or references (series)")
    ap.set_defaults(func=cmd_approve)
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
