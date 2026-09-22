# Proposal

> **Status: draft.** This proposal records scope agreed on 2026-09-22 so it isn't lost. Specs,
> design and tasks will be written when the change is picked up (`/opsx:propose` → continue).

## Why

A locked `episode.yaml` exists but nothing turns it into images yet. Gemini is used manually, so the producer needs ready-to-paste prompts, and the pipeline needs to check what comes back before any audio or rendering work builds on it. Character and location consistency across episodes depends on frozen reference images being attached to every generation, so the series bible must grow to hold them.

## What Changes

- **Gemini prompt pack, generated rather than written:** `story prompts <episode>` derives one prompt per shot from the series bible plus the locked manifest. It includes the verbatim style block, the character references to attach, the location and prop references, time of day, action, emotion, composition, and animation-preparation constraints; for example, the mouth is kept unobstructed when a line in the shot is `on_screen: true`. Also:
  - the "avoid" list
  - the 16:9 size
  - the exact output filename for each image
  - a thumbnail prompt
  
  The pack is fully rebuildable after a relock. The ChatGPT example prompt from the planning conversation is the starting template.
- **Series bible v2: recurring location references.** A `locations` section in the series bible for places that recur across episodes, each with a visual description and reference image(s). Episodes may reference a series location instead of redefining it.
- **Series bible v2: character expression sheets.** An optional expression-sheet reference per character (neutral, happy, sad, surprised, worried, and so on), in addition to the front, three-quarter and side views. It is attached to prompts when a shot calls for a strong expression.
- **Reference-image prompts:** `story prompts --series <id>` generates the one-time Gemini prompts for the style reference, character turnarounds, expression sheets and recurring locations.
- **Image intake:** `story images <episode>` checks the files dropped into `episodes/<id>/images/`: every expected file present, PNG, exact 16:9, at least 1920×1080 (2560×1440 preferred), no unexpected files. It records metadata (hash, dimensions, prompt used, references attached) in `build/images.json`.
- **Contact sheet and checkpoint 2:** a single contact-sheet image of all shots, with shot ids, for approval. The approval is recorded as a hash-bound entry in `approvals.yaml`, and replacing any image makes it stale.

## Capabilities

### New Capabilities
- `prompt-packs`: deterministic generation of Gemini prompts for series references and per-episode shots.
- `image-intake`: validation, metadata capture and contact sheets for the images the producer drops in.
- `approvals`: hash-bound approval records and staleness (first used here for the contact-sheet checkpoint).

### Modified Capabilities
- `series-bible`: adds recurring locations and character expression sheets (`story-series/v2`, with v1 still accepted or migrated; decided in design).
- `episode-manifest`: allows referencing a series location by id.

## Impact

- New CLI commands `story prompts` and `story images`, and a new `approvals.yaml` per episode.
- A new dependency for image inspection and the contact sheet (likely Pillow).
- Schema version bump for the series bible. The example series is migrated.
- No audio, timeline or Remotion work: those are in the next change (`add-narration-and-render`).
