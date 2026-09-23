# Tasks

## 1. Contract: rig states

- [x] 1.1 Add `stance` and `mood` enums to `schemas/vocabulary.v1.json` and make both required on visible characters in `story-episode.v1.schema.json`; verify schema tests plus mutation tests for a missing stance and an unknown mood
- [x] 1.2 Assign `stance` and `mood` to all 29 visible characters in the Foggy Path manifest and to both example episodes, from their free-text pose and expression; verify `story validate` reports 0 errors for all three and `git diff` touches only the added lines
- [x] 1.3 Regenerate `series/willow-meadow/chatgpt-project-instructions.md` and `chatgpt-reference.md`; verify the repo-series tests pass, the compact file is at most 8,000 characters, and both list the stance and mood values

## 2. Narration

- [x] 2.1 Add the optional `voice` extra (kokoro 0.9.4, misaki 0.9.4, torch 2.6.0, numpy 1.26.4, soundfile 0.14.0) and install it; verify `.venv/bin/python -c "import kokoro"` works and the base install still imports without it
- [x] 2.2 Implement the phoneme-to-viseme table and the word-merge rule as pure functions (ported from `poc/svg-rig/scripts/make_audio.py`); verify unit tests for each viseme class, the bilabial rule, time ordering and the 60 ms join rule
- [x] 2.3 Implement `story voice <episode>`: per-line synthesis with the bible voice and speed, pronunciations applied to spoken text only, leading-silence trim, `build/audio/<line-id>.wav`, `build/speech.json`, per-line digests and caching, `--force`, and an actionable error when Kokoro is missing; verify tests with Kokoro mocked (voice and speed passed through, pronunciation, caching, missing-extra message) and one real run on the Foggy Path

## 3. Timeline

- [x] 3.1 Implement shot durations (0.5 s lead-in, lines plus `pause_after` or the 0.35 s default, 1.0 s tail, 2.5 s minimum), a single frame rounding, and frame-aligned line starts; verify tests with hand-computed frames
- [x] 3.2 Implement `build/narration.wav` mixing at frame offsets and ffmpeg two-pass loudness normalization to −14 LUFS and −1 dBTP; verify that line audio begins at the exact sample offset and that measured loudness is within ±1 LU
- [x] 3.3 Implement staging (position to x, depth for background, facing, stance, mood), camera paths from move and intensity with easing and clamping, seeded blinks, mouth tracks for on-screen speakers only, and caption pages of at most 7 words with speaker labels; verify table tests for each camera move, the off-screen speaker case and caption paging
- [x] 3.4 Implement `story timeline <episode>` writing canonical `build/timeline.json` (`story-timeline/v1`); verify byte-identical output across runs and one real run on the Foggy Path
- [x] 3.5 Add walking travel to the timeline: characters walking left or right get a start/end x and a speed (≤110 px/s, ≤900 px, inside the scene); verify tests for travel direction, bounds, speed and the camera/away case

## 4. Render kit

- [x] 4.1 Create `render/`, a Remotion 4.0.517 project with the same pins as the POC, containing the Episode composition (timeline via `--props`, audio via `--public-dir`), shot sequencing with short fades, and the camera transform; verify `npx tsc --noEmit` passes and a stub timeline renders one still
- [x] 4.2 Port the shared kit from the POC (ink outline, time-of-day palette, watercolor and paper filters, word-highlight captions with speaker labels) and add one overlay per atmosphere value; write `render/STYLE.md`; verify a still per time of day and per atmosphere value renders without errors
- [x] 4.3 Implement the registry generator and the missing-component and unsupported-stance/mood check in `pipeline/story/render.py`; verify tests for a missing location, a missing prop, an unsupported stance, and a deterministic registry

## 5. Willow Meadow library and Foggy Path components

- [x] 5.1 Write the rigs for `pip` (from the POC), `ben` and `wren` with their supported stances and moods, mouths, eyelids and hand anchors, following `STYLE.md`; verify a rig sheet still showing every supported stance × a sample of moods for each character
- [x] 5.2 Write the series locations `pip-cottage-interior`, `willow-meadow-path`, `ben-burrow-exterior` and `ben-burrow-interior` (Background and Foreground, groundY, propSlots); verify one still per location at morning and night
- [x] 5.3 Write the Foggy Path episode components: locations `foggy-meadow`, `willow-stream` and `old-fence-crossing`, and props `woven-basket`, `berry-buns`, `mossy-stone` and `amber-lantern`; verify `story render --preview` reports no missing components
- [x] 5.4 Replace the in-place walk with a shared planted-foot walk cycle (`kit/walk.ts`) used by the human rigs, Pip and Ben; the renderer moves walkers along their travel range; verify with a walk strip (frames of one cycle) and the re-rendered previews

## 6. Render, produce and approve

- [x] 6.1 Implement `story render <episode> [--preview]` (registry, Remotion invocation, ffprobe duration check, approval status line); verify the duration check with a stub timeline and a real preview of the Foggy Path
- [x] 6.2 Implement `story approve <episode> preview` and staleness (inputs: manifest, bible, `speech.json`, `timeline.json`, preview, and component files from the registry); verify tests for approval, a refused stale preview, an edited rig making it stale, and an unknown checkpoint
- [x] 6.3 Implement `story produce <episode>` (voice → timeline → preview, stopping at the first failure, printing the preview path and the approval command); verify a CLI test with mocked stages and the real run

## 7. Verification

- [x] 7.1 Run the full test suite and `openspec validate add-svg-episode-render --strict`; verify both pass
- [ ] 7.2 Producer review: watch `build/preview.mp4` of "Pip and the Foggy Path", note issues, fix components, re-render; when satisfied, run `story approve … preview` and render the final; record the results in `notes.md`

## 8. Producer review round 1 (V4 direction)

- [x] 8.1 Contract: add `framing` (wide, medium, close) and optional `subject` to shot cameras, and the `calm` mood; lint the subject (visible in the shot; close/medium need a character); regenerate both series' ChatGPT renderings; verify mutation tests and the 8,000-character limit
- [x] 8.2 Timeline: camera paths relative to the framed view with subject position/depth; walk speed scaled by mood (brisk for happy/excited, slow for calm/thoughtful/tired/sad); caption pages capped at 42 characters with speaker ids; verify table tests for each case
- [x] 8.3 Renderer: frame medium/close shots on the subject's face (rig height, location ground, clamped); larger, raised, label-free captions; `showsText` locations hide captions; verify stills of a close-up, a medium shot and a text shot
- [x] 8.4 Acting: human posture and gesture table by stance and mood (forehead hand when worried, chin hand when thoughtful, slump when sad/tired, chest up when happy/proud, calm breathing), walk energy by mood; `calm` added to every rig and to the face kit; verify a rig sheet of moods
- [x] 8.5 Micro-animation: phone notification bubbles, stirring papers, a ticking wall clock, lamp flicker, morning light spreading in the room, water drops landing, and episode insert locations for watering soil, an unfurling seedling and a compass close-up whose needle settles on north; verify stills
- [x] 8.6 Rewrite "The Quiet Compass" as V4 (about 80–90 s, cinematic gardener sequence, calm final walk, compass close-up, caption-free closing card); voice, timeline, preview; send it to the producer

## 9. Background music

- [x] 9.1 Contract: optional episode `music` (`none`, `hopeful`) in the vocabulary and schema; brief templates and both series' ChatGPT renderings regenerated
- [x] 9.2 `story/music.py`: a deterministic `hopeful` bed (pad, bass, piano arpeggio over I–V–vi–IV) whose density follows shot moods, resolving home in the final shot, leveled under the voices and ducked while speaking; mixed into `build/narration.wav` before normalization; verify with tests
- [x] 9.3 Enable it on "The Quiet Compass"; re-render the preview and send it to the producer

## 10. Shared library and directing guide

- [x] 10.1 Shared tier `render/src/common/{locations,props}` (episode → series → shared lookup), `about` descriptions, listed as ready-made shots in both ChatGPT renderings; verify with tests
- [x] 10.2 Components receive the shot's spoken words (`kit/spoken.ts`: sentences, lastWordAt, wrap); move the Quiet Compass close-ups and cards to the shared tier and time them from the voice instead of fixed seconds
- [x] 10.3 Write `render/DIRECTING.md` (workflow, pacing, shot grammar, acting, walking, timing, review checklist), update `render/STYLE.md`, and add a root `CLAUDE.md` pointing to both

