# Design

## Context

See proposal.md. What exists:
- `story` (Python 3.11) validates `episode.yaml` against `story-episode/v1` and the series bible, and renders the ChatGPT instructions.
- `poc/svg-rig/` proves the approach. Kokoro's `KPipeline` yields per-word `start_ts`, `end_ts` and IPA `phonemes`. `make_audio.py` maps phonemes to 8 mouth shapes. A Remotion 4.0.517 scene draws layered SVG with an ink outline, watercolor filters, a seeded blink schedule, an eased camera and word captions. A 14 s clip at 1080p renders in about 2½ minutes on the M4.
- `sandcastle-film.html` (the producer's reference) contributes a shot-list-driven world: settings as code, a pose library with pivots, a camera `[x, y, zoom]` eased from → to, and sky palettes per time of day.
- ffmpeg and espeak-ng are installed, and Kokoro 0.9.4 with its voices is cached in `~/.cache/huggingface`.

## Goals / Non-Goals

**Goals:**
- `story produce <episode>` goes from a locked manifest to a reviewable preview with no manual steps, apart from Claude writing components for new places and props.
- Every render input is data (`timeline.json`) or a component file; nothing is decided inside React at render time except drawing.
- Adding the next episode reuses the series library, and only genuinely new places or props need new code.

**Non-Goals:**
- Ambience and music, motion across the frame (walking from A to B), the thumbnail, publishing packaging.
- A general-purpose scene editor or a parametric scene kit. Components are hand-written (by Claude) and reviewed in the preview.

## Decisions

### 1. Rig-state vocabulary in the contract
Two new enums go in `schemas/vocabulary.v1.json`:
- `stance`: stand, walk, sit, kneel, lie, reach, hold, hug, fly, perch
- `mood`: neutral, happy, sad, surprised, worried, scared, angry, thoughtful, proud, tired

Both are required on every visible character. Free-text `pose` and `expression` stay as direction for whoever writes components and as flavor for the ChatGPT storyboard. In this change, `walk` is an in-place walk cycle, because traversal needs acts, which come later. Rigs declare the subset they support; Wren supports `fly` and `perch` but not `kneel`. The render check enforces this, not the schema, because support is per character.
- *Alternative: keyword mapping from free text.* Rejected by the producer: silent mis-mappings.

### 2. Narration runs Kokoro in-process
`pipeline/story/voice.py` imports `kokoro.KPipeline` lazily. The `voice` optional extra pins kokoro 0.9.4, misaki 0.9.4, torch 2.6.0, numpy 1.26.4 and soundfile 0.14.0, the versions proven in `voicemodels`. `lang_code` follows the voice prefix (`a`/`b`). The POC's phoneme-to-viseme table and its merge rule move here unchanged, and are covered by tests. `build/speech.json` holds, per line id: the spoken text, voice, speed, input digest, duration, words and visemes. Per-line WAVs are trimmed of Kokoro's leading silence using the first word's `start_ts`, minus 60 ms, with the timings shifted to match.

### 3. Timeline in Python, drawing in TypeScript
`pipeline/story/timeline.py` owns all arithmetic: durations, frames, camera, staging, mouth and blink tracks, captions and mixing. Remotion receives `build/timeline.json` through `--props` and the episode's `build/` as `--public-dir`, so `narration.wav` is served as a static file. The React side is a pure function of `(timeline, frame)`.

Sketch of `timeline.json`:
```json
{ "schema": "story-timeline/v1", "fps": 30, "width": 1920, "height": 1080, "durationInFrames": 6141,
  "series": "willow-meadow", "episode": "2026-09-22-pip-and-the-foggy-path",
  "shots": [{ "id": "s01", "from": 0, "frames": 438, "location": "pip-cottage-interior", "timeOfDay": "morning",
    "atmosphere": ["firelight_flicker", "dust_motes"], "props": ["woven-basket", "berry-buns"],
    "camera": {"from": [960, 560, 1.0], "to": [930, 590, 1.06]},
    "cast": [{ "id": "pip", "x": 960, "depth": 1, "facing": "camera", "stance": "hold", "mood": "proud",
      "mouth": [[412, "consonant"], [414, "ee"]], "blinks": [60, 171] }],
    "captions": [{ "from": 15, "to": 150, "speaker": null, "words": [["One", 15, 22]] }] }],
  "audio": {"src": "narration.wav"} }
```

### 4. Staging and camera rules
- **Position to x:** left 0.18, center_left 0.35, center 0.5, center_right 0.65, right 0.82 of the width.
- **Background characters:** drawn at 0.6 scale on a higher ground line, behind foreground characters.
- **Facing:** `left` mirrors the rig, which is drawn facing right; `camera` and `away` are rig variants.
- **Camera:** this is the sandcastle model. Each move applies a delta to the start view, eased in and out and clamped to the scene. The intensity sets the size of the delta:

  | intensity | zoom delta | pan / tilt |
  |---|---|---|
  | low | 0.06 | 6% |
  | medium | 0.12 | 12% |
  | high | 0.20 | 20% |

  `static` keeps a subtle drift (0.01).

### 5. Component conventions (`render/STYLE.md`)
One small interface per kind, all in plain TSX:
- **Rigs** export `{id, stances, moods, anchors: {hand, head}, height, Component}`. The Component receives `{stance, mood, mouth, eye, t, facing}` and is drawn facing right, with its origin at the feet on the ground line.
- **Locations** export `{id, Background, Foreground, groundY, propSlots}`. Characters are drawn between Background and Foreground. Both receive `{timeOfDay, t, camera}` for parallax.
- **Props** export `{id, Component, width}`. Placement: each character with stance `hold` holds the next unplaced prop at its hand anchor, and the remaining props fill the location's `propSlots` in order.
- **Shared:** `ink` outline props, the `palette(timeOfDay)` sky, watercolor and paper filters, the atmosphere overlays and the captions, taken over from the POC.

`STYLE.md` records the look (outline width and color, the palette, filter use) so that every component Claude writes later matches the series.

### 6. Component discovery by generated registry
Remotion bundles with webpack, so episode folders can't be discovered at runtime. `story render` therefore writes `render/src/generated/registry.ts`, which imports exactly the series and episode components the timeline needs. The same scan produces the missing-component report. The registry is deterministic and sorted, and it's the render project's only file ignored by git.
- *Alternative: webpack `require.context` over all folders.* Rejected: it bundles every episode's code into every render, and hides missing files until runtime.

### 7. Rendering
`story render` shells out to `npx remotion render` with `--props`, `--public-dir`, `--codec=h264 --audio-codec=aac --crf=18`, and `--scale=0.5` for the preview. It then checks the duration with `ffprobe` against the timeline. For speed, the heavy displacement filters apply only to static background layers, and preview renders use half resolution. Expect roughly 10× real time at 1080p: about 35 minutes for the Foggy Path's 205 s.

### 8. Approvals return, scoped to the preview
The module is a trimmed version of the one removed in `remove-image-pipeline` (git `186cbcc`): an append-only `approvals.yaml`, a canonical JSON digest, and per-input hashes so staleness names what changed. The inputs are the manifest, the bible, `speech.json`, `timeline.json`, `preview.mp4`, and every component file in the generated registry.

### 9. What gets committed
Committed: component source, manifests and `approvals.yaml`. Not committed: `build/`, the preview and the final MP4. Everything in them is reproducible, because Kokoro is deterministic for a fixed voice and text, and the render is a pure function of the timeline. The approval records their hashes. This differs from the Gemini era, when approved images were stochastic and had to be committed.

### 10. Migrating existing manifests
The Foggy Path (29 visible-character entries) and both example episodes get `stance` and `mood` assigned once by Claude from their free-text pose and expression. For example, "placing warm buns carefully into a basket" becomes `hold` and `proud`. The result is reviewed in the diff and validated.

## Risks / Trade-offs

- [Rig and set-piece quality depends on hand-written SVG] → `STYLE.md`, reuse of the POC's Pip, and review at the preview checkpoint. Components are small files that are easy to iterate.
- [Render time of about 35 minutes for a 3½-minute episode] → Half-resolution previews, filters only on static layers. Optimize later, for example by pre-rasterizing static backgrounds, if it becomes a bottleneck.
- [Kokoro phoneme timing is spread evenly within a word, so it's approximate] → Good enough in the POC. The viseme table and merge rule are unit-tested, and the preview catches bad cases.
- [An in-place `walk` looks odd for long shots] → Acceptable for the MVP; acts (traversal) are the next motion change.
- [torch in the project venv (1–2 GB)] → Optional `voice` extra: validation-only users don't need it.

## Migration Plan

1. Contract: add the enums, migrate three manifests, regenerate the ChatGPT renderings (the producer re-pastes), all in one commit.
2. Land narration and timeline with tests (no rendering yet).
3. Land `render/`: shared kit, Willow Meadow library, Foggy Path components, the registry and the render command.
4. Produce the Foggy Path preview. The producer reviews and approves it (checkpoint 2).

Rollback is per commit; nothing outside the repository changes.
