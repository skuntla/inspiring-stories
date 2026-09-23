# Design

## Context

See proposal.md for motivation. Current state:
- `story` CLI (`pipeline/story/`) has `validate`, `new` and `brief`. Validation works in two passes (JSON Schema in `schema.py`, then lint in `lint_series.py` and `lint_episode.py`). It produces sorted `Finding`s, exits 0/1/2, and renders text or `--json` (`report.py`).
- Series `willow-meadow` declares style and turnaround slots, but no reference images exist yet (10 warnings). One locked episode exists, `2026-09-22-pip-and-the-foggy-path`, with 16 shots, 7 episode locations and 4 props.
- Gemini is used by hand in the Gemini app. Its 16:9 output size depends on the model the producer has: some produce about 1344×768 (a 1.75 ratio), others 2K or more.
- `**/build/` is already ignored by git, and no image is ignored.
- The Foggy Path thumbnail concept mentions "Old Ben's warm lantern", but only Pip is visible, which shows why characters can't be inferred from the concept text.

## Goals / Non-Goals

**Goals:**
- One command produces everything the producer pastes into Gemini, in order, with nothing to compose by hand.
- Catch a missing, wrong-shaped or tiny image before narration or render work starts.
- Approvals that can't silently survive a change to what was approved.

**Non-Goals:**
- Gemini API automation, clean plates, eye and mouth edits, cutouts and depth, and upscaling (the next animation change).
- Judging image quality or character consistency automatically. The contact sheet is for a human to review.

## Decisions

### 1. Stay on v1, and migrate the few existing files in the same commit
The bible changes are additive (optional `locations` and `references.expressions`). The episode changes are mixed:
- **Loosened:** `locations` may be empty, and shots may use series location ids.
- **Tightened:** `publishing.thumbnail.characters` becomes **required** (decision 13), and redeclaring a series location becomes an error.

The tightening would invalidate existing manifests, and exactly three exist: the Foggy Path episode and the two series example episodes. All three are migrated in the same commit (tasks 7.2–7.3), so `main` never holds an invalid file.
- *Alternative: `story-episode/v2` with a migrator.* Rejected for now: nothing outside this repository consumes the contract, and a mechanical edit of three files costs less than two parallel schemas. The first change that would break manifests we cannot migrate in-repo must bump the version.

### 2. Series locations share the episode's location namespace
A shot's `location` resolves to the episode's declared locations first, then the series. Redeclaring a series id in an episode is an error, not an override: an override would reintroduce per-episode wording, which is exactly the drift recurring references exist to prevent. Series location descriptions carry no time of day or weather. Shots add those (`time_of_day`, `atmosphere`), so one reference image serves dawn, night and fog.

### 3. The prompt pack is Markdown, one file per image
Each file has four parts:
- **Attach**: a numbered list of reference paths, missing ones marked.
- **Prompt**: one fenced `text` block, for one-click copying.
- **Save as**: the exact path.
- **Built from**: input digests.

`index.md` is a checklist in generation order. Templates live in `pipeline/story/templates/` next to the brief templates, rendered with `string.Template` like the brief. Output goes to `build/prompts/`, which is regenerated wholesale: the directory is cleared first, so shots removed by a relock disappear.

### 4. Attachment selection
The order goes from most to least identity-critical:

| Order | Attachment | Condition |
|---|---|---|
| 1 | first style reference | always |
| 2 | location references | the series location's references, or the episode anchor (decision 12) |
| 3 | one view per visible character | `camera` → front, `left`/`right` → three-quarter, `away` → side |
| 4 | expression sheet | the character has an `on_screen: true` line in this shot |

There's a cap of **6**. Characters beyond the cap are uncommon, since shots rarely show more than 3 characters. Overflow drops expression sheets first, then location references after the first, and the prompt says what was dropped. Six is a practical ceiling: attaching more references to a single generation weakens how strictly each one is followed, and the Gemini app's upload limits vary.

### 5. Prompt wording
It follows the structure of the ChatGPT example agreed in planning:
1. The identity lock ("Use the attached references for …, without changing facial features, proportions, colors or clothing"), followed by each character's verbatim identity block.
2. The frame spec ("cinematic 16:9 illustrated storybook frame").
3. Location plus time-of-day lighting.
4. Characters (position, pose, expression, facing).
5. Props.
6. Action and emotion.
7. Composition notes, plus camera headroom ("leave extra scenery on all sides; the camera will slowly <move>").
8. Animation preparation.
9. The style description, verbatim.
10. Exclusions.

Atmosphere splits in two:

| In the drawing (described as part of the scene) | Animated later (the prompt says do not draw) |
|---|---|
| fog, mist, sun_rays, firelight_flicker (warm firelight), wind (windswept grass and fur) | rain*, snow*, dust_motes, fireflies, embers, falling_leaves, sparkles |

\* For rain and snow, the scene is drawn as rainy or snowy (wet surfaces, overcast light, snow on the ground), but without falling drops or flakes.

Spoken line text is never included, so Gemini is never tempted to render dialogue as text.

### 6. Series reference prompts
- **Style reference:** a representative 16:9 scene in the style, with no characters.
- **Turnaround views:** full body on a plain light-grey background, neutral expression, canonical outfit, one view per image. Views other than the front attach the front view to chain identity.
- **Expression sheet:** a 3×2 grid on plain grey. The six expressions are neutral, happy, sad, surprised, worried and determined, chosen to cover the delivery vocabulary's emotional range.
- **Location references:** 16:9, no characters, neutral daylight, as described.

Save-as paths are the ones declared in the bible, so a finished pack clears every missing-reference warning.

### 7. Intake thresholds
| Check | Error | Warning |
|---|---|---|
| format | not decodable as PNG or JPEG | — |
| aspect (shots, thumbnail, style and location references) | more than 2% off 16:9 | — |
| size | shorter side under 720 px | smaller than 1920×1080 |

The 2% tolerance accepts 1344×768 (1.75 against 1.778). The render stage will crop to exactly 16:9, which costs under 2% of the frame. The warning, rather than an error, keeps smaller Gemini outputs usable: the animation change adds upscaling, and camera moves are limited meanwhile.

### 8. Metadata and the contact sheet
- `build/images.json` is canonical JSON: sorted keys, no timestamps. It holds the manifest and bible digests plus per-image `{path, sha256, format, width, height}`.
- The contact sheet uses **Pillow**, the one new dependency: 4 columns, 480×270 tiles, a label strip under each (id, then the action, truncated), and grey placeholder tiles for missing images. It's also Pillow's first use. Later changes (layers, upscaling) will need it anyway.

### 9. Approvals
`approvals.yaml` (`story-approvals/v1`) is append-only:
```yaml
schema: "story-approvals/v1"
approvals:
  - checkpoint: "images"
    approved_at: "2026-09-23T10:15:00Z"
    digest: "sha256:…"            # sha256 of the canonical JSON of `inputs`
    inputs:
      "episodes/…/episode.yaml": "sha256:…"
      "series/willow-meadow/series.yaml": "sha256:…"
      "episodes/…/images/s01.png": "sha256:…"
```
Storing the per-input hashes, not only the digest, lets the stale status name exactly what changed. The `images` inputs include the series reference images attached by the pack: regenerating Pip's front view legitimately invalidates an episode's image approval. `approved_at` is the only non-reproducible value, and it's never part of a digest.

### 10. Git policy: commit every approved image
Series reference images **and** episode images (shots, the thumbnail and location anchors) are committed. Gemini generations are stochastic source assets, not reproducible build artifacts: a hash in `approvals.yaml` proves what was approved but cannot restore it. Only `build/` stays ignored, because everything in it is regenerable.
- *Alternative: ignore episode images and keep only hashes.* Rejected: an approved episode could not be rebuilt on another machine or after a disk loss.
- *Alternative: Git LFS or external artifact storage now.* Deferred: it adds tooling before repository size is a real problem. Revisit when the repository or clone time becomes painful.

### 11. Willow Meadow data
These recurring places move into the bible, with time and weather removed from their descriptions: `pip-cottage-interior`, `willow-meadow-path`, `ben-burrow-exterior` and `ben-burrow-interior`. The one-off places stay in the episode: `foggy-meadow` (7 shots) and `old-fence-crossing` (2 shots) get anchors; `willow-stream` (1 shot) does not. Pip, Ben and Wren each gain an expression-sheet slot. The Foggy Path manifest loses its four now-duplicate declarations and gains `publishing.thumbnail.characters: ["pip"]`. That matches its concept, where Ben appears only as a distant lantern glow. Shots and lines are untouched. Both ChatGPT renderings are regenerated, and the compact one must stay within 8,000 characters (it's about 4,900 now; the locations and the thumbnail rule add about 800).

### 12. Episode location anchors are derived, not declared
An episode-only location used by **two or more shots** gets an anchor: a 16:9 establishing image of the place, with no characters, generated before any shot and attached to every shot there. It's saved at `images/locations/<id>.png`. A single-use location gets none, because its one shot is its own reference.
- *Alternative: a manifest flag (for example `anchor: true`) set by ChatGPT.* Rejected: it puts a production decision and an implied file into the story contract, and ChatGPT would have to reason about image generation.
- *Alternative: anchors for every location.* Rejected: it adds an image to generate and approve with no consistency benefit for single-shot places.

An anchor sits in the same attachment slot as series location references (decision 4). It's part of the `images` checkpoint, so replacing it makes the approval stale, like any shot.

### 13. Thumbnail characters are structured
`publishing.thumbnail.characters` is a required list of cast ids (possibly empty, never the narrator). The thumbnail prompt uses exactly these ids for identity blocks and front-view attachments. Matching names inside the free-text concept was fragile ("Old Ben's lantern" names Ben without showing him) and would silently attach the wrong references. Both ChatGPT renderings show the field and the rule: list only the characters visible in the thumbnail, or `[]`.

### 14. The thumbnail is a required image
The contract always has `publishing.thumbnail` and the pack always writes `thumbnail.md`, so a missing `images/thumbnail.png` is an intake error, and it blocks the `images` approval. The thumbnail is part of what the producer approves at checkpoint 2.

## Risks / Trade-offs

- [Gemini ignores references or drifts across 16 shots] → Identity blocks are verbatim, references are chained, and a human reviews the contact sheet at checkpoint 2. Rerolling one shot is cheap: regenerate `sNN.png`, rerun `story images`, re-approve.
- [Small Gemini output (1344×768) looks soft at 1080p] → A warning now; upscaling in the animation change.
- [Committed images grow the repository: about 15 reference images per series plus about 20 images per episode, at 1–5 MB each] → Accepted for the MVP, since approved generations can't be recreated. Move to Git LFS or external storage when size or clone time becomes a real problem. Only approved images need to be committed; rerolled drafts stay out of the commit.
- [An anchor makes a location look identical in shots meant to differ (for example, fog thinning)] → Shots still carry their own atmosphere and action, and the prompt treats the anchor as a place reference, not a frame to copy.
- [Six attachments aren't enough for crowded shots] → Deterministic drop order, noted in the prompt. Revisit if the attachment limit or reliability changes.

## Migration Plan

1. Land the schema and lint changes (optional fields, required thumbnail characters, the redeclaration error).
2. In the same commit, edit the Willow Meadow bible, the Foggy Path manifest and both series example episodes, so `main` never holds an invalid manifest.
3. Regenerate and commit both ChatGPT renderings. The producer re-pastes the compact instructions into the Project.

Rollback: revert the commit. No other state exists.
