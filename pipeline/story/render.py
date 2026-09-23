"""Render: resolve the SVG components an episode needs, refuse when any is missing, write the
generated registry, run Remotion, and check the output duration."""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .timeline import FPS, TIMELINE_FILE

RENDER_DIR = Path("render")
REGISTRY_FILE = RENDER_DIR / "src" / "generated" / "registry.ts"
COMMON_DIR = "common"  # render/src/common/{locations,props}: reusable by every series and episode
_ABOUT = re.compile(r'^export const about = "([^"]+)";$', re.M)
PREVIEW_FILE = Path("build") / "preview.mp4"
FINAL_FILE = Path("build") / "final.mp4"
PROPS_FILE = Path("build") / "render-props.json"

# Rigs declare what they support as one-line literal arrays (see render/STYLE.md), e.g.
#   stances: ['stand', 'walk', 'sit'],
_LIST = r"{key}\s*:\s*\[([^\]]*)\]"


def rig_support(source: str, key: str) -> set[str] | None:
    m = re.search(_LIST.format(key=key), source)
    return None if m is None else set(re.findall(r"['\"]([a-z_]+)['\"]", m.group(1)))


@dataclass
class Plan:
    components: dict[str, dict[str, Path]] = field(default_factory=lambda: {"characters": {}, "locations": {}, "props": {}})
    problems: list[str] = field(default_factory=list)
    thumbnail: Path | None = None  # render/src/episodes/<episode>/thumbnail.tsx, when the episode has one

    def files(self) -> list[Path]:
        return sorted(p for kind in self.components.values() for p in kind.values())


def common_library(root: Path) -> dict[str, dict[str, str]]:
    """The shared components any episode can use by id: {"locations": {id: about}, "props": {...}}."""
    out: dict[str, dict[str, str]] = {"locations": {}, "props": {}}
    for kind in out:
        for path in sorted((root / RENDER_DIR / "src" / COMMON_DIR / kind).glob("*.tsx")):
            about = _ABOUT.search(path.read_text(encoding="utf-8"))
            out[kind][path.stem] = about.group(1) if about else ""
    return out


def plan(root: Path, timeline: dict, series_locations: set[str]) -> Plan:
    """Map every character, location and prop the timeline uses to its component file."""
    series_dir = root / RENDER_DIR / "src" / "series" / timeline["series"]
    episode_dir = root / RENDER_DIR / "src" / "episodes" / timeline["episode"]
    common_dir = root / RENDER_DIR / "src" / COMMON_DIR
    out = Plan()
    used: dict[str, dict[str, set[str]]] = {}
    for shot in timeline["shots"]:
        for kind, ids in (("locations", [shot["location"]]), ("props", shot["props"])):
            for cid in ids:
                if cid in out.components[kind]:
                    continue
                # the most specific wins: this episode, then its series, then the shared library
                candidates = [episode_dir / kind / f"{cid}.tsx", series_dir / kind / f"{cid}.tsx",
                              common_dir / kind / f"{cid}.tsx"]
                found = next((c for c in candidates if c.is_file()), None)
                if found:
                    out.components[kind][cid] = found
                else:
                    where = candidates[1] if kind == "locations" and cid in series_locations else candidates[0]
                    hint = "" if kind == "locations" else f" (or {candidates[1].relative_to(root)} to share it)"
                    out.problems.append(f"missing {kind[:-1]} '{cid}' (first used in {shot['id']}): "
                                        f"write {where.relative_to(root)}{hint}")
                    out.components[kind][cid] = None  # type: ignore[assignment]
        for c in shot["cast"]:
            use = used.setdefault(c["id"], {"stance": set(), "mood": set(), "shots": set()})
            use["stance"].add(c["stance"])
            use["mood"].add(c["mood"])
            use["shots"].add(shot["id"])
    for cid in sorted(used):
        path = series_dir / "characters" / f"{cid}.tsx"
        if not path.is_file():
            out.problems.append(f"missing character rig '{cid}': write {path.relative_to(root)}")
            continue
        out.components["characters"][cid] = path
        source = path.read_text(encoding="utf-8")
        for key in ("stance", "mood"):
            supported = rig_support(source, key + "s")
            if supported is None:
                out.problems.append(f"{path.relative_to(root)} must declare `{key}s: [...]` on one line")
                continue
            for value in sorted(used[cid][key] - supported):
                shots = [s["id"] for s in timeline["shots"] for c in s["cast"] if c["id"] == cid and c[key] == value]
                out.problems.append(f"'{cid}' does not support {key} '{value}' (used in {', '.join(shots)}); "
                                    f"add it to {path.relative_to(root)} or change the manifest")
    for kind in out.components:
        out.components[kind] = {k: v for k, v in out.components[kind].items() if v is not None}
    thumb = episode_dir / THUMBNAIL_FILE
    out.thumbnail = thumb if thumb.is_file() else None
    return out


def write_registry(root: Path, p: Plan) -> Path:
    target = root / REGISTRY_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    export = {"characters": "rig", "locations": "location", "props": "prop"}
    imports, maps = [], {}
    n = 0
    for kind in ("characters", "locations", "props"):
        entries = []
        for cid, path in sorted(p.components[kind].items()):
            rel = Path("..") / path.relative_to(root / RENDER_DIR / "src")
            imports.append(f"import {{{export[kind]} as c{n}}} from '{rel.with_suffix('').as_posix()}';")
            entries.append(f"\t\t'{cid}': c{n},")
            n += 1
        maps[kind] = "\n".join(entries)
    if p.thumbnail:
        thumb = (Path("..") / p.thumbnail.relative_to(root / RENDER_DIR / "src")).with_suffix("").as_posix()
        thumb_line = f"export {{thumbnail}} from '{thumb}';"
    else:
        thumb_line = "export const thumbnail: ThumbnailSpec | undefined = undefined;"
    body = ["// Generated by `story render` for one episode. Do not edit; it is rewritten on every render.",
            "import type {Registry} from '../kit/types';",
            "import type {ThumbnailSpec} from '../thumbnail/Thumbnail';", *imports, "", thumb_line, "",
            "export const registry: Registry = {",
            *[f"\t{kind}: {{\n{maps[kind]}\n\t}}," for kind in ("characters", "locations", "props")], "};", ""]
    target.write_text("\n".join(body), encoding="utf-8")
    return target


def run_remotion(root: Path, episode_dir: Path, timeline: dict, preview: bool, log=print) -> Path:
    props = episode_dir / PROPS_FILE
    props.write_text(json.dumps({"timeline": timeline}), encoding="utf-8")
    out = episode_dir / (PREVIEW_FILE if preview else FINAL_FILE)
    cmd = ["npx", "remotion", "render", "src/index.ts", "Episode", str(out.resolve()),
           f"--props={props.resolve()}", f"--public-dir={(episode_dir / 'build').resolve()}",
           "--codec=h264", "--audio-codec=aac", "--crf=18", "--overwrite", "--log=error"]
    if preview:
        cmd.append("--scale=0.5")
    log(f"rendering {'preview (960x540)' if preview else 'final (1920x1080)'} … this takes a while")
    subprocess.run(cmd, cwd=root / RENDER_DIR, check=True)
    return out


THUMBNAIL_FILE = "thumbnail.tsx"
THUMBNAIL_SIZE = (1280, 720)       # YouTube's recommended size
THUMBNAIL_MAX_BYTES = 2 * 1024 * 1024  # YouTube's upload limit


def thumbnail_variants(path: Path) -> int:
    """How many headline variants a thumbnail spec declares (`headlines: [...]` on one line)."""
    m = re.search(r"headlines\s*:\s*\[(.*)\]", path.read_text(encoding="utf-8"))
    return len(re.findall(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", m.group(1))) if m else 0


def run_thumbnails(root: Path, episode_dir: Path, plan: Plan, log=print) -> list[Path]:
    """Render build/thumbnail-<n>.jpg for each headline variant of the episode's thumbnail spec."""
    count = thumbnail_variants(plan.thumbnail) if plan.thumbnail else 0
    outs = []
    for i in range(count):
        out = episode_dir / "build" / f"thumbnail-{i + 1}.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["npx", "remotion", "still", "src/index.ts", "Thumbnail", str(out.resolve()),
                        f"--props={json.dumps({'variant': i})}", "--image-format=jpeg", "--jpeg-quality=90",
                        "--overwrite", "--log=error"], cwd=root / RENDER_DIR, check=True)
        outs.append(out)
    return outs


def duration_seconds(path: Path) -> float:
    # the video stream, not the container: AAC pads the audio out to whole 1024-sample frames
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def check_duration(path: Path, timeline: dict) -> str | None:
    expected = timeline["durationInFrames"] / FPS
    actual = duration_seconds(path)
    if abs(actual - expected) > 1.5 / FPS:  # within a frame
        return f"{path.name} lasts {actual:.3f} s but the timeline is {expected:.3f} s"
    return None


def load_timeline(episode_dir: Path) -> dict:
    path = episode_dir / TIMELINE_FILE
    if not path.is_file():
        raise FileNotFoundError("no build/timeline.json yet; run `story timeline` first")
    return json.loads(path.read_text(encoding="utf-8"))
