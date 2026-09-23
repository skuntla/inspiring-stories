"""Gemini prompt packs, generated from the series bible and the locked manifest.

The producer pastes these by hand into Gemini. Everything here is derived, so identity and
style wording never drift between episodes, and a pack can always be regenerated.
"""
from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from string import Template

from .load import rel

MAX_ATTACHMENTS = 6
IMAGE_EXTS = (".png", ".jpg", ".jpeg")
PROMPTS_DIR = Path("build") / "prompts"

VIEW_FOR_FACING = {"camera": "front", "left": "three_quarter", "right": "three_quarter", "away": "side"}
VIEW_LABEL = {"front": "front view", "three_quarter": "three-quarter view", "side": "side view",
              "expressions": "expression sheet"}
POSITION = {"left": "on the left", "center_left": "left of center", "center": "in the center",
            "center_right": "right of center", "right": "on the right", "background": "in the background"}
FACING = {"camera": "facing the viewer", "left": "facing left", "right": "facing right",
          "away": "facing away from the viewer"}
TIME_OF_DAY = {"dawn": "soft pale-gold dawn light", "morning": "clear morning light", "midday": "bright midday light",
               "afternoon": "warm afternoon light", "dusk": "dusk light, warm orange fading to blue",
               "night": "night, moonlit with soft shadows"}
CAMERA = {"static": "the camera will hold with very subtle movement", "push_in": "the camera will slowly push in",
          "pull_out": "the camera will slowly pull out", "pan_left": "the camera will slowly pan left",
          "pan_right": "the camera will slowly pan right", "tilt_up": "the camera will slowly tilt up",
          "tilt_down": "the camera will slowly tilt down"}
# Atmosphere drawn into the still image...
SCENE_ATMOSPHERE = {"fog": "soft fog softening the distance", "mist": "light drifting mist",
                    "sun_rays": "sun rays streaming through the scene", "firelight_flicker": "warm firelight",
                    "wind": "windswept grass, leaves and fur",
                    "rain": "rainy conditions: wet surfaces and overcast light",
                    "snow": "snowy conditions: snow on the ground and cold light"}
# ...and atmosphere animated later as overlays, so never drawn.
ANIMATED_ATMOSPHERE = {"rain": "falling raindrops", "snow": "falling snowflakes", "dust_motes": "floating dust motes",
                       "fireflies": "fireflies", "embers": "floating embers", "falling_leaves": "falling leaves",
                       "sparkles": "sparkles"}
FIXED_EXCLUSIONS = ["text, letters, numbers, captions or speech bubbles", "borders, frames, signatures or watermarks",
                    "extra characters or animals not described here", "duplicate characters"]
EXPRESSIONS = ["neutral", "happy", "sad", "surprised", "worried", "determined"]


@dataclass(frozen=True)
class Attachment:
    path: str  # project-relative, POSIX
    label: str
    kind: str  # style | location | anchor | view | expressions
    exists: bool


@dataclass(frozen=True)
class PromptFile:
    name: str  # file name inside build/prompts/
    title: str
    save_as: str  # project-relative
    attachments: list[Attachment]
    prompt: str
    dropped: list[Attachment]


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def find_image(folder: Path, stem: str) -> Path | None:
    """The existing file for an image stem, trying each allowed extension in order."""
    for ext in IMAGE_EXTS:
        candidate = folder / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def _join(text: str) -> str:
    return " ".join(str(text).split())


def _names(names: list[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def identity_block(c: dict) -> str:
    return (f"{c['name']}: {_join(c['description'])} Outfit: {_join(c['outfit'])} "
            f"Distinguishing features: {'; '.join(_join(f) for f in c['features'])}.")


class SeriesContext:
    def __init__(self, root: Path, series_dir: Path, bible: dict):
        self.root, self.series_dir, self.bible = root, series_dir, bible
        self.characters = {c["id"]: c for c in bible["characters"]}
        self.locations = {loc["id"]: loc for loc in bible.get("locations", []) or []}

    def attachment(self, declared: str, label: str, kind: str) -> Attachment:
        path = self.series_dir / declared
        return Attachment(rel(path, self.root), label, kind, path.is_file())

    def style(self) -> Attachment:
        return self.attachment(self.bible["style"]["references"][0], "style reference", "style")

    def style_line(self) -> str:
        return f"Style: {_join(self.bible['style']['description'])}"

    def avoid_line(self, extra: list[str] | None = None) -> str:
        items = [_join(a) for a in self.bible["style"].get("avoid", [])] + (extra or FIXED_EXCLUSIONS)
        return "Avoid: " + "; ".join(items) + "."

    def digests(self, *extra: Path) -> str:
        files = [*extra, self.series_dir / "series.yaml"]
        return " · ".join(f"`{rel(p, self.root)}` {sha256_file(p)}" for p in files)


class EpisodeContext(SeriesContext):
    def __init__(self, root: Path, series_dir: Path, bible: dict, episode_dir: Path, doc: dict):
        super().__init__(root, series_dir, bible)
        self.episode_dir, self.doc = episode_dir, doc
        self.episode_locations = {loc["id"]: loc for loc in doc.get("locations", [])}
        self.props = {p["id"]: p for p in doc.get("props", []) or []}
        self.anchors = anchored_locations(doc, set(self.locations))

    def anchor(self, lid: str) -> Attachment:
        folder = self.episode_dir / "images" / "locations"
        path = find_image(folder, lid) or folder / f"{lid}.png"
        return Attachment(rel(path, self.root), f"{lid} location anchor", "anchor", path.is_file())

    def location_description(self, lid: str) -> str:
        loc = self.locations.get(lid) or self.episode_locations[lid]
        return _join(loc["description"])


def anchored_locations(doc: dict, series_location_ids: set[str]) -> list[str]:
    """Episode-only locations used by two or more shots, in declaration order."""
    uses: dict[str, int] = {}
    for shot in doc.get("shots", []):
        uses[shot["location"]] = uses.get(shot["location"], 0) + 1
    return [loc["id"] for loc in doc.get("locations", [])
            if loc["id"] not in series_location_ids and uses.get(loc["id"], 0) >= 2]


def shot_attachments(ctx: EpisodeContext, shot: dict) -> tuple[list[Attachment], list[Attachment]]:
    """Attachments in priority order, capped at MAX_ATTACHMENTS; returns (kept, dropped)."""
    lid = shot["location"]
    if lid in ctx.locations:
        location = [ctx.attachment(ref, f"{lid} location reference {n}", "location")
                    for n, ref in enumerate(ctx.locations[lid]["references"], 1)]
    elif lid in ctx.anchors:
        location = [ctx.anchor(lid)]
    else:
        location = []
    speakers = {line["speaker"] for line in shot["lines"] if line.get("on_screen") is True}
    views, expressions = [], []
    for visible in shot["characters"]:
        c = ctx.characters[visible["id"]]
        view = VIEW_FOR_FACING[visible["facing"]]
        views.append(ctx.attachment(c["references"][view], f"{c['name']} {VIEW_LABEL[view]}", "view"))
        if visible["id"] in speakers and c["references"].get("expressions"):
            expressions.append(ctx.attachment(c["references"]["expressions"],
                                              f"{c['name']} {VIEW_LABEL['expressions']}", "expressions"))
    dropped: list[Attachment] = []
    while 1 + len(location) + len(views) + len(expressions) > MAX_ATTACHMENTS:
        if expressions:
            dropped.insert(0, expressions.pop())
        elif len(location) > 1:
            dropped.insert(0, location.pop())
        else:
            dropped.insert(0, views.pop())
    return [ctx.style(), *location, *views, *expressions], dropped


def _identity_lock(names: list[str]) -> str:
    return (f"Use the attached reference images. Keep {_names(names)} exactly as in the references: same face, "
            f"body proportions, colors, markings and clothing.")


def shot_prompt(ctx: EpisodeContext, shot: dict, attachments: list[Attachment]) -> str:
    visible = [(v, ctx.characters[v["id"]]) for v in shot["characters"]]
    names = [c["name"] for _, c in visible]
    speakers = [c["name"] for v, c in visible
                if any(l["speaker"] == v["id"] and l.get("on_screen") is True for l in shot["lines"])]
    out: list[str] = []
    if names:
        out.append(_identity_lock(names))
    if any(a.kind in ("location", "anchor") for a in attachments):
        out.append("Match the place shown in the attached location reference.")
    out.append("Match the rendering style of the attached style reference.")
    out += ["", "Create a cinematic 16:9 illustrated storybook frame.", "",
            f"Location: {ctx.location_description(shot['location'])}",
            f"Lighting: {TIME_OF_DAY[shot['time_of_day']]}."]
    scene = [SCENE_ATMOSPHERE[a] for a in shot["atmosphere"] if a in SCENE_ATMOSPHERE]
    if scene:
        out.append("Atmosphere: " + "; ".join(scene) + ".")
    if visible:
        out.append("Characters:")
        for v, c in visible:
            out.append(f"- {identity_block(c)}")
            out.append(f"  In this frame: {POSITION[v['position']]}, {_join(v['pose'])}, "
                       f"{_join(v['expression'])}, {FACING[v['facing']]}.")
    else:
        out.append("Characters: none. Show no characters or animals.")
    props = [ctx.props[p] for p in shot.get("props", []) if p in ctx.props]
    if props:
        out.append("Props:")
        out += [f"- {_join(p['description'])}" for p in props]
    out += [f"Action: {_join(shot['action'])}", f"Mood: {_join(shot['emotion'])}",
            f"Composition: {_join(shot['composition_notes'])} Leave extra scenery on every side of the frame, "
            f"because {CAMERA[shot['camera']['move']]} and the edges may be cropped."]
    prep = []
    eyes = [c["name"] for v, c in visible if v["facing"] != "away"]
    if eyes:
        prep.append(f"keep the eyes of {_names(eyes)} clearly visible")
    if speakers:
        prep.append(f"keep the {'face and mouth' if len(speakers) == 1 else 'faces and mouths'} of "
                    f"{_names(speakers)} fully visible and unobstructed "
                    f"(no paws, props or other characters in front of a mouth)")
    if len(visible) > 1:
        prep.append("keep the characters separated with clean silhouettes, never overlapping each other's faces")
    if prep:
        out.append("Animation preparation: " + "; ".join(prep) + ".")
    animated = [ANIMATED_ATMOSPHERE[a] for a in shot["atmosphere"] if a in ANIMATED_ATMOSPHERE]
    if animated:
        out.append(f"Do not draw {_names(animated)}; they are animated later.")
    out += ["", ctx.style_line(), ctx.avoid_line()]
    return "\n".join(out)


def anchor_prompt(ctx: EpisodeContext, lid: str) -> str:
    first_shot = next(s for s in ctx.doc["shots"] if s["location"] == lid)
    return "\n".join([
        "Match the rendering style of the attached style reference.", "",
        "Create a cinematic 16:9 illustrated storybook establishing view of this place, with no characters or "
        "animals. It will be the reference for every shot set here, so show the whole place clearly with its "
        "key landmarks.", "",
        f"Location: {ctx.location_description(lid)}",
        f"Lighting: {TIME_OF_DAY[first_shot['time_of_day']]}.", "",
        ctx.style_line(),
        ctx.avoid_line(FIXED_EXCLUSIONS[:2] + ["any characters or animals"]),
    ])


def thumbnail_attachments(ctx: EpisodeContext) -> tuple[list[Attachment], list[Attachment]]:
    views = [ctx.attachment(ctx.characters[cid]["references"]["front"],
                            f"{ctx.characters[cid]['name']} front view", "view")
             for cid in ctx.doc["publishing"]["thumbnail"]["characters"]]
    keep = MAX_ATTACHMENTS - 1
    return [ctx.style(), *views[:keep]], views[keep:]


def thumbnail_prompt(ctx: EpisodeContext) -> str:
    thumb = ctx.doc["publishing"]["thumbnail"]
    chars = [ctx.characters[cid] for cid in thumb["characters"]]
    out = [_identity_lock([c["name"] for c in chars])] if chars else []
    out += ["Match the rendering style of the attached style reference.", "",
            "Create a 16:9 illustrated YouTube thumbnail in the series style: one clear focal point, a bold and "
            "simple composition that reads at a small size, and calm uncluttered space in the upper third for a "
            "title that is added later.", "",
            f"Concept: {_join(thumb['concept'])}"]
    if chars:
        out.append("Characters:")
        out += [f"- {identity_block(c)}" for c in chars]
    else:
        out.append("Characters: none. Draw no characters or animals.")
    out += ["Do not draw any text, letters or numbers.", "", ctx.style_line(), ctx.avoid_line()]
    return "\n".join(out)


def episode_pack(ctx: EpisodeContext) -> list[PromptFile]:
    images = ctx.episode_dir / "images"
    files: list[PromptFile] = []
    for lid in ctx.anchors:
        save = rel(images / "locations" / f"{lid}.png", ctx.root)
        files.append(PromptFile(f"location-{lid}.md", f"Location anchor: {lid}", save, [ctx.style()],
                                anchor_prompt(ctx, lid), []))
    for shot in ctx.doc["shots"]:
        kept, dropped = shot_attachments(ctx, shot)
        files.append(PromptFile(f"{shot['id']}.md", f"Shot {shot['id']}: {_join(shot['action'])}",
                                rel(images / f"{shot['id']}.png", ctx.root), kept, shot_prompt(ctx, shot, kept),
                                dropped))
    kept, dropped = thumbnail_attachments(ctx)
    files.append(PromptFile("thumbnail.md", "Thumbnail", rel(images / "thumbnail.png", ctx.root), kept,
                            thumbnail_prompt(ctx), dropped))
    return files


def series_pack(ctx: SeriesContext) -> list[PromptFile]:
    title = ctx.bible["title"]
    style_refs = ctx.bible["style"]["references"]
    files: list[PromptFile] = []
    n = 0

    def add(slug, heading, declared, attachments, prompt):
        nonlocal n
        n += 1
        files.append(PromptFile(f"{n:02d}-{slug}.md", heading, rel(ctx.series_dir / declared, ctx.root),
                                attachments, prompt, []))

    for i, ref in enumerate(style_refs):
        subject = ("a quiet scene without characters that fits the series" if i == 0 else
                   "a different quiet scene without characters, in exactly the same style as the attached style reference")
        add(f"style-{i + 1:02d}", f"Style reference {i + 1}", ref, [ctx.style()] if i else [],
            "\n".join([f'Create a representative 16:9 illustration that defines the visual style of the series '
                       f'"{title}": {subject}.', "", ctx.style_line(),
                       ctx.avoid_line(FIXED_EXCLUSIONS[:2] + ["any characters or animals"])]))
    for c in ctx.bible["characters"]:
        if c["kind"] != "character":
            continue
        refs = c["references"]
        front = ctx.attachment(refs["front"], f"{c['name']} front view", "view")
        sheet = ("full body, standing in a neutral pose with a neutral expression, on a plain light-grey "
                 "background with no scenery, showing the complete outfit")
        views = [("front", "front view", [ctx.style()]),
                 ("three_quarter", "three-quarter view, turned slightly to the viewer's left", [ctx.style(), front]),
                 ("side", "side profile, facing left", [ctx.style(), front])]
        for slot, wording, attach in views:
            lock = ("Match the rendering style of the attached style reference." if slot == "front" else
                    f"Keep {c['name']} exactly as in the attached front view, and match the attached style reference.")
            add(f"{c['id']}-{slot.replace('_', '-')}", f"{c['name']}: {VIEW_LABEL[slot]}", refs[slot], attach,
                "\n".join([lock, "", f"Create a character reference image of {c['name']}: {wording}, {sheet}.", "",
                           identity_block(c), "", ctx.style_line(),
                           ctx.avoid_line(FIXED_EXCLUSIONS[:2] + ["other characters or animals"])]))
        if refs.get("expressions"):
            add(f"{c['id']}-expressions", f"{c['name']}: expression sheet", refs["expressions"], [ctx.style(), front],
                "\n".join([f"Keep {c['name']} exactly as in the attached front view, and match the attached style "
                           f"reference.", "",
                           f"Create an expression sheet for {c['name']}: a 3 x 2 grid of head-and-shoulders portraits "
                           f"on a plain light-grey background showing, in reading order, {', '.join(EXPRESSIONS)}. "
                           f"No labels.", "",
                           identity_block(c), "", ctx.style_line(),
                           ctx.avoid_line(FIXED_EXCLUSIONS[:2] + ["other characters or animals"])]))
    for loc in ctx.bible.get("locations", []) or []:
        first = ctx.attachment(loc["references"][0], f"{loc['id']} location reference 1", "location")
        for j, ref in enumerate(loc["references"]):
            view = ("an establishing view" if j == 0 else
                    "a different angle of the same place, consistent with the attached location reference")
            add(f"{loc['id']}-{j + 1:02d}", f"Location {loc['id']}: reference {j + 1}", ref,
                [ctx.style()] + ([first] if j else []),
                "\n".join(["Match the rendering style of the attached style reference.", "",
                           f"Create a 16:9 reference illustration of this recurring place: {view}, with no characters "
                           f"or animals, in neutral daylight.", "",
                           f"Location: {_join(loc['description'])}", "", ctx.style_line(),
                           ctx.avoid_line(FIXED_EXCLUSIONS[:2] + ["any characters or animals"])]))
    return files


def _render(pf: PromptFile, built_from: str) -> str:
    if pf.attachments:
        attach = "\n".join(f"{i}. `{a.path}` ({a.label})" + ("" if a.exists else " — MISSING: generate it first")
                           for i, a in enumerate(pf.attachments, 1))
    else:
        attach = "Nothing to attach."
    notes = ("\nNot attached (six-attachment limit): " + ", ".join(f"`{a.path}`" for a in pf.dropped) + "\n"
             if pf.dropped else "")
    template = Template(resources.files("story").joinpath("templates/prompt-file.md.tmpl").read_text(encoding="utf-8"))
    return template.substitute(title=pf.title, save_as=pf.save_as, attachments=attach, prompt=pf.prompt,
                               notes=notes, built_from=built_from)


def write_pack(target_dir: Path, files: list[PromptFile], heading: str, next_steps: list[str],
               built_from: str) -> tuple[Path, list[Attachment]]:
    """Replace target_dir/build/prompts with the pack; return (dir, missing attachments)."""
    out = target_dir / PROMPTS_DIR
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    index = [f"# {heading}", "",
             "Generate the images in this order. For each one: open its prompt file, attach the listed images in "
             "order, paste the prompt into Gemini, and save the result at the given path.", ""]
    index += [f"- [ ] `{pf.name}` → `{pf.save_as}`" for pf in files]
    index += ["", "Then:", ""] + [f"{n}. {step}" for n, step in enumerate(next_steps, 1)]
    (out / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    missing: list[Attachment] = []
    for pf in files:
        (out / pf.name).write_text(_render(pf, built_from), encoding="utf-8")
        missing += [a for a in pf.attachments if not a.exists and a not in missing]
    return out, missing
