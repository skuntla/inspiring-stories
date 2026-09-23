# Proposal

## Why

The series is now rendered as SVG from code. The proof of concept (`poc/svg-rig/`) showed that it works: consistent characters, viseme lip sync from Kokoro's own phonemes, word-level captions, all driven by data. But it's a hand-wired 14-second scene. To produce "Pip and the Foggy Path" and every later episode, the pipeline must turn a locked `episode.yaml` into narrated audio, a frame-exact timeline and a rendered MP4 with one command. The producer should only have to lock the story and approve the preview.

## What Changes

- **Story contract: rig states.** Every visible character in a shot gains `stance` and `mood` from a closed vocabulary. The free-text `pose` and `expression` remain as extra direction. The ChatGPT renderings pick up the new vocabulary automatically. The Foggy Path manifest and both example episodes are migrated.
- **Narration:** `story voice <episode>` runs Kokoro locally for every line, using the speaker's voice and speed from the series bible and the episode's pronunciations for the spoken text only. It records per-word timings and a viseme track derived from Kokoro's phonemes. Lines whose inputs haven't changed are not regenerated. Kokoro becomes an optional `voice` install of this project.
- **Timeline:** `story timeline <episode>` computes shot durations from the measured audio (lead-in, lines, pauses, tail, minimum length), rounds to frames once, and places each line's audio on a frame boundary. It then resolves:
  - a camera path per shot from `camera.move` and `intensity`
  - word-level caption pages, including speaker labels
  - mouth tracks for on-screen speakers
  - seeded blink schedules
  - staging from position, facing, stance and mood

  It writes `build/timeline.json` and the mixed, loudness-normalized `build/narration.wav`.
- **SVG render:** a Remotion project in `render/` draws the timeline. It holds:
  - **A series library:** character rigs, recurring-location set pieces, shared props, and atmosphere overlays.
  - **An episode folder** for the places and props the episode introduces. Claude writes these as SVG components during production.
  - **A shared look:** one ink outline and watercolor-style SVG filters, plus a sky palette per time of day.

  `story render <episode>` refuses to start while any character, location or prop used by the episode lacks a component, and lists each missing file. `--preview` renders a fast 960×540 cut; the default renders the 1920×1080 final.
- **One trigger:** `story produce <episode>` runs voice → timeline → preview render and reports what needs review.
- **Checkpoint 2, preview approval:** `story approve <episode> preview` records a hash-bound approval. It covers the manifest, the bible, the audio, the timeline, the rendered preview and every SVG component used. Any later change makes it stale, and `story render` names what changed.
- **Willow Meadow library and Foggy Path components:**
  - rigs for Pip, Ben and Wren
  - set pieces for the 4 recurring locations and the 3 episode-only ones
  - the episode's 4 props

  The first full preview of "Pip and the Foggy Path" is the acceptance test.

Out of scope, for later changes: ambience and music audio (`ambience` keys are carried but silent), within-shot motion such as walking across the frame, the thumbnail image, and publishing packaging.

## Capabilities

### New Capabilities
- `narration`: Kokoro speech generation per line, with word timings, phoneme-derived visemes and caching.
- `timeline`: the audio-driven, frame-exact render description of an episode.
- `svg-render`: the Remotion SVG renderer, its component library conventions, the missing-component check, and the preview and final outputs.
- `approvals`: hash-bound approval of the rendered preview, and staleness.

### Modified Capabilities
- `episode-manifest`: visible characters carry `stance` and `mood` from the closed vocabulary.
- `pipeline-cli`: new `voice`, `timeline`, `render`, `produce` and `approve` commands.

## Impact

- New: `render/` (a Remotion 4 project, TypeScript, with pinned versions matching the proof of concept) and `pipeline/story/voice.py`, `timeline.py`, `render.py` and `approvals.py`.
- Contract: `story-episode/v1` gains two required fields per visible character. The three manifests in the repository are migrated in the same commit, and the ChatGPT renderings are regenerated (the producer re-pastes the compact one).
- Dependencies: an optional `voice` extra (kokoro 0.9.4, torch 2.6.0, numpy 1.26.4, soundfile, misaki), about 1–2 GB once. Also required: espeak-ng and ffmpeg (both present) and Node 24.
- Episode folders gain `build/` outputs (ignored by git) and a committed `approvals.yaml`. The approved final MP4 is kept out of git; its hash is recorded.
- `poc/svg-rig/` stays as a reference until `render/` supersedes it.
