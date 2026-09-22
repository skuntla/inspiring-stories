# Proposal

## Why

Every later stage — Gemini prompt packs, Kokoro narration, timing, captions, the Remotion render — needs one agreed, machine-checkable description of an episode and of the recurring cast and style it draws on. Without that contract first, each stage would invent its own interpretation of ChatGPT's free-form output, and character, voice and style drift would be baked in from episode one. This change fixes the contract before any media is generated.

## What Changes

- Introduce a **series bible** (`series/<series-id>/series.yaml`) holding the reusable visual style, the character roster (appearance, canonical outfit, reference-image slots, Kokoro voice), and series defaults. It is authored once and reused by every episode.
- Introduce the **canonical episode manifest** (`episodes/<id>/episode.yaml`, schema `story-episode/v1`) describing an original story as an ordered list of shots, each with location, characters, action, emotion, camera intent, atmosphere, ambience and spoken lines, plus publishing copy. It carries no durations, pixel positions, file paths or voice IDs.
- Publish both contracts as versioned **JSON Schemas** checked into the repo, plus a closed **enum vocabulary** (camera moves, atmosphere effects, ambience keys, deliveries, positions) and an allowlist of English Kokoro voices.
- Add a **ChatGPT instruction document**, generated per series from the schema and bible so it cannot drift, to be installed once as ChatGPT Project instructions. It has a conversational **creative mode** (prose and a readable storyboard, no YAML) and a **"Lock this story"** mode that outputs a complete, schema-valid `episode.yaml`, asking only the minimum blocking question when something is unresolved.
- Line ids are derived from position (`s03-l02`), never authored; the Gemini prompt pack and the remaining production artifacts are derived by the pipeline, not written by ChatGPT.
- Add the first slice of the local `story` CLI (Python 3.11):
  - `story new <series> "<title>"` scaffolds an episode folder with a stub manifest.
  - `story brief <series>` generates the ChatGPT instruction document for that series.
  - `story validate <episode-dir>` runs schema validation plus semantic lint (cross-references against the bible, line-length and runtime estimates) and prints an actionable report; non-zero exit on errors.
- Add one example series and one example episode that pass validation, used as golden test fixtures.

Out of scope (later changes): prompt-pack generation, image intake, TTS, alignment, layers, timeline, rendering, approvals, packaging.

## Capabilities

### New Capabilities
- `series-bible`: the reusable per-series definition of style, characters, voices and defaults, and the rules that make it valid.
- `episode-manifest`: the canonical `story-episode/v1` episode contract — structure, vocabulary, cross-reference and lint rules, and the ChatGPT handoff it must satisfy.
- `pipeline-cli`: the `story` command-line entry point, its scaffolding and validation commands, report format and exit-code behavior.

### Modified Capabilities
<!-- none: no existing specs -->

## Impact

- New directories: `schemas/`, `series/`, `episodes/`, `pipeline/`, `docs/`.
- New Python 3.11 project (`pipeline/`, `pyproject.toml`) with a small dependency set (PyYAML, jsonschema). No network access, no media dependencies yet.
- No changes to `/Users/skuntla/Documents/projects/voicemodels` or `/Users/skuntla/Documents/projects/ai-engineer-interview-video`; their conventions (manifest-driven stages, hard validation before generation) inform the design only.
- Establishes the contract every subsequent OpenSpec change will build on; later changes that alter it must bump the schema version.
