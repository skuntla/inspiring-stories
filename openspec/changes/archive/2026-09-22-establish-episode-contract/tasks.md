# Tasks

## 1. Project setup

- [x] 1.1 Create `pyproject.toml` (package `story-pipeline`, console script `story`, deps PyYAML + jsonschema, dev dep pytest) and the `pipeline/story/` package skeleton; verify `uv venv --python 3.11 .venv && uv pip install -e '.[dev]'` succeeds and `.venv/bin/story --help` prints usage
- [x] 1.2 Update `.gitignore` for `.venv/`, `**/build/`, `__pycache__/` and `.pytest_cache/`; verify `git status` shows no venv or cache files

## 2. Contracts

- [x] 2.1 Write `schemas/vocabulary.v1.json` with every enum from design.md §3; verify it loads as valid JSON Schema via `jsonschema.Draft202012Validator.check_schema`
- [x] 2.2 Write `schemas/kokoro-voices.en.json` (English `af_/am_/bf_/bm_` presets with accent and gender); verify a test asserts every id matches `^[ab][fm]_[a-z]+$` with no duplicates
- [x] 2.3 Write `schemas/story-series.v1.schema.json` (strict: `additionalProperties: false`, narrator vs visual character variants, voice speed 0.5–2.0, `content_rating: all-ages`); verify `check_schema` passes
- [x] 2.4 Write `schemas/story-episode.v1.schema.json` (strict; shots 1–30; `pause_after` 0–3; publishing length limits; `language: en`; `source.kind: original`; `made_for_kids` required; no timing fields); verify `check_schema` passes

## 3. Loading and reporting

- [x] 3.1 Implement the strict YAML loader (rejects duplicate keys, anchors and aliases) and project-root discovery with `--root` override; verify unit tests for a duplicate key, an alias and root discovery
- [x] 3.2 Implement the Finding model and text and `--json` report renderers with a stable sort order and exit codes 0/1/2; verify tests show identical output across two runs and the correct exit code for each case

## 4. Validation

- [x] 4.1 Implement pass 1 (schema validation → plain-language findings with field paths; enum errors list allowed values; an unsupported version stops early); verify tests for an unknown field, a bad enum, `schema: story-episode/v2` and a `duration` field
- [x] 4.2 Implement series lint: folder/id match, unique ids, exactly one narrator, narrator without visual fields, voice in allowlist, reference paths inside the series folder, missing reference files as warnings; verify one failing case per rule (golden series plus a single mutation each, in `tests/test_series.py`)
- [x] 4.3 Implement episode lint: id format and folder match, series exists, cast in bible, declared/unused locations and props, shot id sequence, visible characters in cast, on-screen speaker rules, 60-word line limit, pronunciation key rules, shot-count warning outside 4–16; verify one failing case per rule (golden episode plus a single mutation each, in `tests/test_episode.py`)
- [x] 4.4 Implement the runtime estimate (140 wpm × voice speed, plus pauses, plus 0.4 s between lines) with per-shot and total output and a >30 s shot warning; verify a test with hand-computed expected values

## 5. Commands

- [x] 5.1 Implement `story validate <path>` (series or episode; an episode validates its bible first); verify tests for a valid episode (exit 0), an episode with a broken bible (exit 1, bible error reported) and a bad path (exit 2)
- [x] 5.2 Implement `story new <series> "<title>" [--date]` (ASCII kebab slug, refuses overwrite, unknown series errors); verify tests for creation, overwrite refusal and an unknown series, and that the generated stub is reported as a stub by `story validate`
- [x] 5.3 Implement `story brief <series> [--out]` from `templates/brief.md.tmpl` (instructions, vocabulary table from the schema, cast from the bible, example episode); verify tests that it refuses on an invalid bible and that adding a character to a fixture bible makes it appear in the output
- [x] 5.4 Rewrite `templates/brief.md.tmpl` as two-mode ChatGPT Project instructions (creative mode by default with prose and a plain-text storyboard format, "Lock this story" with a blocking-decision pre-flight, complete replacement on relock, and no image prompts, line ids, durations or voices from ChatGPT); verify tests assert that each mode's rules and the blocking-decision list appear in the generated brief
- [x] 5.5 Explain derived line ids when a line carries an `id` field (unknown-field message names the `sNN-lMM` convention); verify a test for `shots[0].lines[0].id`
- [x] 5.6 Add optional series `audience` and `defaults.made_for_kids` (schema, brief rendering: made-for-kids is blocking only without a default, episode warning when it deviates from the default); verify tests for a valid default, a non-boolean default, the deviation warning, and brief text with and without a default
- [x] 5.7 Split the brief into compact Project instructions (default `story brief`, hard limit 8,000 characters, warning above 7,500) and the full reference (`story brief --full`); verify tests for the preserved rules, refusal over 8,000, the warning above 7,500, and the series default in both renderings

## 6. Example series and golden fixtures

- [x] 6.1 Author `series/example-meadow/series.yaml` (narrator plus 2–3 characters, style description, reference slots) and `series/example-meadow/example-episode.yaml` (6 shots covering narration, on-screen dialogue, off-screen voice, pronunciations and atmosphere); verify `story validate series/example-meadow` reports 0 errors (missing-image warnings expected)
- [x] 6.2 Add a golden test that validates the brief's embedded example against its series with 0 errors; verify `pytest` passes
- [x] 6.3 Author the production series `series/willow-meadow/` (Tales from Willow Meadow: narrator, pip, ben (formerly bramble), wren; example-meadow style; `defaults.made_for_kids: false`) with its example episode, commit `series/willow-meadow/chatgpt-project-instructions.md` (compact, installable) and `chatgpt-reference.md` (full), and add tests that every repo series validates, that each committed rendering matches a fresh render, and that committed Project instructions are at most 8,000 characters; verify `pytest` passes

## 7. Verification

- [x] 7.1 End-to-end ChatGPT round trip: install `series/willow-meadow/chatgpt-project-instructions.md` as ChatGPT Project instructions (optionally upload `chatgpt-reference.md` as a Project file), then (a) brainstorm and confirm you get prose and a storyboard with no YAML; (b) say "Lock this story" while the story still needs a character who is not in the cast and confirm ChatGPT asks only that question; also confirm it uses the series default `made_for_kids: false` without asking; (c) answer it and confirm one YAML block comes back; paste it into a `story new willow-meadow ...` episode and run `story validate`; (d) request a revision and relock, and confirm a complete replacement manifest that validates. Record the results in the change folder as `notes.md`
- [x] 7.2 Run the full test suite and `openspec validate establish-episode-contract --strict`; verify both pass

## Notes

- 2026-09-22: ChatGPT's Project-instructions field is limited to 8,000 characters; the single ~16,000-character brief could not be installed. Resolved by task 5.7 (compact plus full renderings). The compact Willow Meadow instructions are about 4,900 characters.
