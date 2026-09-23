# Proposal

## Why

A locked episode now exists ("Pip and the Foggy Path", 16 shots), but nothing turns it into illustrations. Gemini is used by hand, so the producer needs ready-to-paste prompts that say exactly which reference images to attach and what file to save. The pipeline also needs to check what comes back before any audio or rendering work builds on it. Character and place consistency across episodes depends on frozen reference images attached to every generation, so the series bible must hold references for recurring places and character expressions, not only turnarounds.

## What Changes

- **Recurring series locations.** The series bible gains an optional `locations` list: id, visual description and one to three reference images, for places that recur across episodes (Pip's cottage, Ben's burrow, the meadow path). Episodes may use a series location id directly instead of redeclaring it. Redeclaring a series location id inside an episode is an error, because the series description must win for consistency.
- **Character expression sheets.** An optional `references.expressions` image per character, attached when that character speaks on screen.
- **Structured thumbnail characters.** `publishing.thumbnail.characters` becomes a required list of cast ids visible in the thumbnail (possibly empty, never the narrator). The pipeline uses it, rather than guessing names from the free-text concept, to pick identity blocks and references.
- **ChatGPT documents list series locations and the thumbnail-characters rule,** so stories reuse locations and fill the new field. The compact Project instructions stay within 8,000 characters.
- **Prompt packs, generated rather than written:**
  - `story prompts <series-dir>` writes the one-time Gemini prompts for style references, character turnarounds, expression sheets and location references.
  - `story prompts <episode-dir>` writes, in this order: a **location anchor** prompt for each episode-only location used by two or more shots (for example `foggy-meadow`, used by 7 shots); one prompt per shot; and a thumbnail prompt. All are derived from the bible and the locked manifest. Each lists the reference images to attach, in order, and the exact filename to save as. Anchors are attached to every shot at their location.
  - The prompt text fixes identity and style, carries the shot's intent, and adds animation-preparation constraints: speakers' mouths unobstructed, eyes visible, room for camera movement, and no particle effects that are animated later.
  - The same inputs always produce byte-identical packs.
- **Image intake:** `story images <dir>` checks the dropped-in files: every expected file present (shots, location anchors, and the **required** thumbnail) and none unexpected, PNG or JPEG, readable, close to 16:9, and above a minimum size, with a warning below 1920×1080. It records hashes and dimensions in `build/images.json` and builds a labelled contact sheet.
- **Approvals:** `story approve <dir> images|references` records a hash-bound approval in `approvals.yaml`. Any later change to the images, the manifest or the bible makes that approval stale, and `story images` reports the status. This implements checkpoint 2 (the image contact sheet), plus a one-time approval of each series' reference set.
- **Willow Meadow:** four recurring locations move into the series bible. "Pip and the Foggy Path" drops its now-duplicate location declarations and gains `thumbnail.characters: ["pip"]`; its story content is unchanged. Both example episodes gain the thumbnail field too.

Out of scope: clean plates, eye and mouth edits, cutouts and depth (the animation change); narration, timeline and render (`add-narration-and-render`); calling the Gemini API.

## Capabilities

### New Capabilities
- `prompt-packs`: deterministic Gemini prompt generation for series reference images and per-episode shots and thumbnails.
- `image-intake`: checking the images the producer drops in, recording their metadata, and building contact sheets.
- `approvals`: hash-bound approval records, their staleness rules, and the approve command.

### Modified Capabilities
- `series-bible`: adds recurring locations and character expression sheets; reference-presence checks cover them.
- `episode-manifest`: shots may use series location ids; an episode may not redeclare one; `publishing.thumbnail.characters` is required and validated against the cast; the ChatGPT documents list series locations and the thumbnail-characters rule.

## Impact

- New CLI commands: `story prompts`, `story images`, `story approve`. New files per episode: `images/` (shots, the thumbnail, `locations/` anchors), `approvals.yaml`, and `build/prompts/`, `build/images.json` and `build/contact-sheet.png` (the last three regenerable and ignored by git).
- New dependency: Pillow (image reading and the contact sheet).
- `story-series/v1` gains optional fields only. `story-episode/v1` gains one required field (`thumbnail.characters`) and one new error (redeclaring a series location). The three manifests in the repository are migrated in the same commit; nothing outside the repository consumes the contract.
- Git: all approved images are committed, both series references and episode images. Gemini generations are stochastic source assets: a hash proves what was approved but cannot restore it. Only `build/` is ignored. Git LFS or external storage can come later, when repository size becomes a real issue.
