# Tasks

## 1. Contract: rig states

- [ ] 1.1 Add `stance` and `mood` enums to `schemas/vocabulary.v1.json` and make both required on visible characters in `story-episode.v1.schema.json`; verify schema tests plus mutation tests for a missing stance and an unknown mood
- [ ] 1.2 Assign `stance` and `mood` to all 29 visible characters in the Foggy Path manifest and to both example episodes, from their free-text pose and expression; verify `story validate` reports 0 errors for all three and `git diff` touches only the added lines
- [ ] 1.3 Regenerate `series/willow-meadow/chatgpt-project-instructions.md` and `chatgpt-reference.md`; verify the repo-series tests pass, the compact file is at most 8,000 characters, and both list the stance and mood values

## 2. Narration

- [ ] 2.1 Add the optional `voice` extra (kokoro 0.9.4, misaki 0.9.4, torch 2.6.0, numpy 1.26.4, soundfile 0.14.0) and install it; verify `.venv/bin/python -c "import kokoro"` works and the base install still imports without it
- [ ] 2.2 Implement the phoneme-to-viseme table and the word-merge rule as pure functions (ported from `poc/svg-rig/scripts/make_audio.py`); verify unit tests for each viseme class, the bilabial rule, time ordering and the 60 ms join rule
- [ ] 2.3 Implement `story voice <episode>`: per-line synthesis with the bible voice and speed, pronunciations applied to spoken text only, leading-silence trim, `build/audio/<line-id>.wav`, `build/speech.json`, per-line digests and caching, `--force`, and an actionable error when Kokoro is missing; verify tests with Kokoro mocked (voice and speed passed through, pronunciation, caching, missing-extra message) and one real run on the Foggy Path

## 3. Timeline

- [ ] 3.1 Implement shot durations (0.5 s lead-in, lines plus `pause_after` or the 0.35 s default, 1.0 s tail, 2.5 s minimum), a single frame rounding, and frame-aligned line starts; verify tests with hand-computed frames
- [ ] 3.2 Implement `build/narration.wav` mixing at frame offsets and ffmpeg two-pass loudness normalization to −14 LUFS and −1 dBTP; verify that line audio begins at the exact sample offset and that measured loudness is within ±1 LU
- [ ] 3.3 Implement staging (position to x, depth for background, facing, stance, mood), camera paths from move and intensity with easing and clamping, seeded blinks, mouth tracks for on-screen speakers only, and caption pages of at most 7 words with speaker labels; verify table tests for each camera move, the off-screen speaker case and caption paging
- [ ] 3.4 Implement `story timeline <episode>` writing canonical `build/timeline.json` (`story-timeline/v1`); verify byte-identical output across runs and one real run on the Foggy Path

## 4. Render kit

- [ ] 4.1 Create `render/`, a Remotion 4.0.517 project with the same pins as the POC, containing the Episode composition (timeline via `--props`, audio via `--public-dir`), shot sequencing with short fades, and the camera transform; verify `npx tsc --noEmit` passes and a stub timeline renders one still
- [ ] 4.2 Port the shared kit from the POC (ink outline, time-of-day palette, watercolor and paper filters, word-highlight captions with speaker labels) and add one overlay per atmosphere value; write `render/STYLE.md`; verify a still per time of day and per atmosphere value renders without errors
- [ ] 4.3 Implement the registry generator and the missing-component and unsupported-stance/mood check in `pipeline/story/render.py`; verify tests for a missing location, a missing prop, an unsupported stance, and a deterministic registry

## 5. Willow Meadow library and Foggy Path components

- [ ] 5.1 Write the rigs for `pip` (from the POC), `ben` and `wren` with their supported stances and moods, mouths, eyelids and hand anchors, following `STYLE.md`; verify a rig sheet still showing every supported stance × a sample of moods for each character
- [ ] 5.2 Write the series locations `pip-cottage-interior`, `willow-meadow-path`, `ben-burrow-exterior` and `ben-burrow-interior` (Background and Foreground, groundY, propSlots); verify one still per location at morning and night
- [ ] 5.3 Write the Foggy Path episode components: locations `foggy-meadow`, `willow-stream` and `old-fence-crossing`, and props `woven-basket`, `berry-buns`, `mossy-stone` and `amber-lantern`; verify `story render --preview` reports no missing components

## 6. Render, produce and approve

- [ ] 6.1 Implement `story render <episode> [--preview]` (registry, Remotion invocation, ffprobe duration check, approval status line); verify the duration check with a stub timeline and a real preview of the Foggy Path
- [ ] 6.2 Implement `story approve <episode> preview` and staleness (inputs: manifest, bible, `speech.json`, `timeline.json`, preview, and component files from the registry); verify tests for approval, a refused stale preview, an edited rig making it stale, and an unknown checkpoint
- [ ] 6.3 Implement `story produce <episode>` (voice → timeline → preview, stopping at the first failure, printing the preview path and the approval command); verify a CLI test with mocked stages and the real run

## 7. Verification

- [ ] 7.1 Run the full test suite and `openspec validate add-svg-episode-render --strict`; verify both pass
- [ ] 7.2 Producer review: watch `build/preview.mp4` of "Pip and the Foggy Path", note issues, fix components, re-render; when satisfied, run `story approve … preview` and render the final; record the results in `notes.md`
