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
                    render_brief, render_project_instructions, render_story_prompt)
from .lint_episode import EPISODE_FILE, check_episode
from .lint_series import SERIES_FILE, check_series
from . import approvals, render, timeline, voice
from .load import find_root, load_yaml, rel
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


def _episode(args) -> tuple[Result, Path, Path, dict | None, dict | None]:
    """Resolve and validate an episode; returns (result, folder, root, manifest, bible), manifest None on errors."""
    kind, target, root = _target(args)
    if kind != "episode":
        raise UsageError(f"{args.path} is a series folder; this command needs an episode folder")
    check = check_episode(target / EPISODE_FILE, root, expected_id=target.resolve().name)
    result = Result(findings=check.findings, estimate=check.estimate)
    if result.errors:
        print("error: the episode has validation errors; nothing was produced:", file=sys.stderr)
        _emit(result, False, sys.stderr)
        return result, target, root, None, None
    return result, target, root, load_yaml(target / EPISODE_FILE), check.series.bible


def cmd_voice(args) -> int:
    result, target, root, doc, bible = _episode(args)
    if doc is None:
        return EXIT_ERRORS
    try:
        voice.generate(target, doc, bible, force=args.force)
    except voice.VoiceUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERRORS
    return EXIT_OK


def cmd_timeline(args) -> int:
    result, target, root, doc, bible = _episode(args)
    if doc is None:
        return EXIT_ERRORS
    try:
        timeline.generate(target, doc, bible)
    except timeline.StaleSpeech as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERRORS
    return EXIT_OK


def _prepared(args):
    """Validate, check the timeline is current and every component exists; returns a context dict or None."""
    result, target, root, doc, bible = _episode(args)
    if doc is None:
        return None
    try:
        tl = render.load_timeline(target)
        current = timeline.build(doc, bible, timeline.load_speech(target, doc, bible))
    except (FileNotFoundError, timeline.StaleSpeech) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return None
    if current != tl:
        print("error: build/timeline.json is out of date with the manifest; run `story timeline` first", file=sys.stderr)
        return None
    plan = render.plan(root, tl, {loc["id"] for loc in bible.get("locations") or []})
    if plan.problems:
        print(f"error: {len(plan.problems)} component problem(s); nothing was rendered:", file=sys.stderr)
        for problem in plan.problems:
            print(f"  {problem}", file=sys.stderr)
        return None
    render.write_registry(root, plan)
    return {"target": target, "root": root, "timeline": tl, "plan": plan,
            "series_dir": root / "series" / doc["series"]}


def _approval_state(ctx) -> dict:
    inputs = approvals.collect_inputs(ctx["root"], ctx["target"], ctx["series_dir"], ctx["plan"])
    return approvals.status(approvals.load_entries(ctx["target"]), inputs)


def cmd_render(args) -> int:
    ctx = _prepared(args)
    if ctx is None:
        return EXIT_ERRORS
    tl, plan = ctx["timeline"], ctx["plan"]
    if args.check:
        print(f"all {sum(len(v) for v in plan.components.values())} components present "
              f"({', '.join(f'{len(v)} {k}' for k, v in plan.components.items())})")
    else:
        final = getattr(args, "final", False)
        state = _approval_state(ctx)
        if final and state["status"] != "approved":
            print(f"warning: rendering the final while the preview is {state['status']}", file=sys.stderr)
        out = render.run_remotion(ctx["root"], ctx["target"], tl, preview=not final)
        problem = render.check_duration(out, tl)
        if problem:
            print(f"error: {problem}", file=sys.stderr)
            return EXIT_ERRORS
        print(f"wrote {rel(out, ctx['root'])} ({tl['durationInFrames'] / timeline.FPS:.1f} s)")
    print(approvals.describe(_approval_state(ctx)))
    return EXIT_OK


def cmd_thumbnail(args) -> int:
    ctx = _prepared(args)
    if ctx is None:
        return EXIT_ERRORS
    plan, root = ctx["plan"], ctx["root"]
    if plan.thumbnail is None:
        where = f"render/src/episodes/{ctx['timeline']['episode']}/{render.THUMBNAIL_FILE}"
        print(f"error: no thumbnail spec; write {where} (see render/DIRECTING.md, Thumbnails)", file=sys.stderr)
        return EXIT_ERRORS
    if render.thumbnail_variants(plan.thumbnail) == 0:
        print(f"error: {rel(plan.thumbnail, root)} declares no `headlines: [...]` on one line", file=sys.stderr)
        return EXIT_ERRORS
    print(f"rendering {render.thumbnail_variants(plan.thumbnail)} thumbnail variant(s) …", file=sys.stderr)
    for out in render.run_thumbnails(root, ctx["target"], plan):
        size = out.stat().st_size
        note = "" if size <= render.THUMBNAIL_MAX_BYTES else "  (over YouTube's 2 MB limit)"
        print(f"wrote {rel(out, root)} ({size // 1024} KB){note}")
    return EXIT_OK


def cmd_approve(args) -> int:
    if args.checkpoint not in approvals.CHECKPOINTS:
        raise UsageError(f"unknown checkpoint '{args.checkpoint}'; supported: {', '.join(approvals.CHECKPOINTS)}")
    ctx = _prepared(args)
    if ctx is None:
        return EXIT_ERRORS
    preview = ctx["target"] / render.PREVIEW_FILE
    tl_file = ctx["target"] / timeline.TIMELINE_FILE
    if not preview.is_file() or preview.stat().st_mtime < tl_file.stat().st_mtime:
        print("error: not approved; build/preview.mp4 is missing or older than the timeline. "
              "Run `story render` (preview) first.", file=sys.stderr)
        return EXIT_ERRORS
    inputs = approvals.collect_inputs(ctx["root"], ctx["target"], ctx["series_dir"], ctx["plan"])
    entry = approvals.append(ctx["target"], args.checkpoint, inputs)
    print(f"approved {args.checkpoint} at {entry['approved_at']} ({len(inputs)} inputs); "
          f"recorded in {rel(ctx['target'] / approvals.FILE, ctx['root'])}")
    return EXIT_OK


def cmd_produce(args) -> int:
    """voice -> timeline -> preview render, stopping at the first failure."""
    for name, step in (("voice", cmd_voice), ("timeline", cmd_timeline), ("render", cmd_render)):
        print(f"== {name}")
        step_args = argparse.Namespace(**{**vars(args), "force": False, "check": False, "final": False, "preview": True})
        code = step(step_args)
        if code != EXIT_OK:
            print(f"error: stopped at `story {name}`", file=sys.stderr)
            return code
    folder = Path(args.path)
    print(f"\nReview {folder / render.PREVIEW_FILE}, then approve it with:\n  story approve {folder} preview")
    return EXIT_OK


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
    if args.story:
        text = render_story_prompt(series.bible)
    elif args.full:
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
    kind = b.add_mutually_exclusive_group()
    kind.add_argument("--story", action="store_true",
                      help="render the story-only prompt (ChatGPT writes plain prose; Claude directs it)")
    kind.add_argument("--full", action="store_true",
                      help="render the full reference contract instead of the compact Project instructions")
    b.add_argument("--out", help="write to this file instead of stdout")
    b.set_defaults(func=cmd_brief)
    th = sub.add_parser("thumbnail", help="render the episode's YouTube thumbnail variants (1280x720 JPEG)")
    th.add_argument("path")
    th.set_defaults(func=cmd_thumbnail)
    vo = sub.add_parser("voice", help="synthesize every line of an episode with Kokoro")
    vo.add_argument("path")
    vo.add_argument("--force", action="store_true", help="regenerate every line, ignoring the cache")
    vo.set_defaults(func=cmd_voice)

    tl = sub.add_parser("timeline", help="build the frame-exact timeline and mixed narration of an episode")
    tl.add_argument("path")
    tl.set_defaults(func=cmd_timeline)

    rd = sub.add_parser("render", help="render the episode's preview (default) or final MP4 from its timeline")
    rd.add_argument("path")
    mode = rd.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="960x540 preview (the default)")
    mode.add_argument("--final", action="store_true", help="1920x1080 final")
    rd.add_argument("--check", action="store_true", help="only check that every component exists")
    rd.set_defaults(func=cmd_render)

    ap = sub.add_parser("approve", help="record approval of the episode's rendered preview")
    ap.add_argument("path")
    ap.add_argument("checkpoint", help="preview")
    ap.set_defaults(func=cmd_approve)

    pr = sub.add_parser("produce", help="voice, timeline and preview render in one go")
    pr.add_argument("path")
    pr.set_defaults(func=cmd_produce)
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
