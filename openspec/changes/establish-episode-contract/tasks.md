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

## 6. Example series and golden fixtures

- [x] 6.1 Author `series/example-meadow/series.yaml` (narrator plus 2–3 characters, style description, reference slots) and `series/example-meadow/example-episode.yaml` (6 shots covering narration, on-screen dialogue, off-screen voice, pronunciations and atmosphere); verify `story validate series/example-meadow` reports 0 errors (missing-image warnings expected)
- [x] 6.2 Add a golden test that validates the brief's embedded example against its series with 0 errors; verify `pytest` passes

## 7. Verification

- [ ] 7.1 End-to-end check: run `story brief example-meadow --out /tmp/brief.md`, paste the brief into ChatGPT, save the returned YAML as a new episode via `story new`, and run `story validate`; verify either a clean pass, or a report whose messages alone let ChatGPT produce a clean manifest in one round (record the result in the change notes)
- [x] 7.2 Run the full test suite and `openspec validate establish-episode-contract --strict`; verify both pass
