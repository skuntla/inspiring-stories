# Design

## Context

The repo is empty apart from OpenSpec scaffolding. This change creates the first code: two contracts (series bible, episode manifest) and the first `story` CLI commands. See proposal.md for motivation and the three specs for the required behavior.

Relevant prior art, read but not reused as code:
- `voicemodels/episodes/*/episode.md` (`video-authoring/v1`): YAML front-matter plus Markdown beats. It worked, but it mixed prose and data, and it needed a custom parser.
- `ai-engineer-interview-video` ADR-001: "validators reject unknown fields, unknown enums, unsupported versions … rather than guessing", and "models propose, code decides". This design adopts both.
- `voicemodels` `build_captions.py`: captions must show display text even when the TTS text differs. That is the reason for the `pronunciations` rule.

Platform: macOS arm64; Python 3.11 at `/opt/homebrew/bin/python3.11`; `uv` available.

## Goals / Non-Goals

**Goals:**
- A contract strict enough that later stages never need to guess what the input means.
- Error messages good enough that pasting a validation report back into ChatGPT gets a corrected manifest in one round.
- Keep every piece of vocabulary in one place, so the brief, the schema and the validator can't disagree.

**Non-Goals:**
- Any media generation, prompt packs, approvals or build caching (later changes).
- Choosing the actual series, its characters or its voices. Only an example series is created here.
- Managing schema migrations. v1 is the first version.

## Decisions

### 1. YAML for authoring, JSON Schema as the canonical contract
Authors (ChatGPT, then you) write YAML. It's comment-friendly, pleasant to read and edit, and ChatGPT emits it reliably. Structure is defined by JSON Schema (draft 2020-12) files in `schemas/`:
`story-series.v1.schema.json` and `story-episode.v1.schema.json`, both with `additionalProperties: false` everywhere.
- *Alternative: Pydantic models as the source.* Rejected: the Remotion/TypeScript side will need the same contract later, and a language-neutral schema file generates types for both.
- *Alternative: Markdown + front-matter (the `voicemodels` format).* Rejected: shots and lines are structured data, and prose sections need a bespoke parser.

### 2. Two-pass validation: structure, then meaning
Pass 1 checks the loaded document against the JSON Schema (`jsonschema` library): types, required fields, enums, limits and unknown fields. Pass 2 is a Python lint for everything a schema can't express: folder/id agreement, references to the bible, shot id sequence, on-screen speaker rules, word counts, unused declarations, runtime estimate and reference-file presence. Pass 2 runs even when pass 1 has errors, but skips any rule whose inputs failed pass 1, so the report stays complete without cascading noise. An unsupported `schema` version stops everything after that single error.

### 3. Vocabulary lives in the schema; everything else reads it from there
The enums are defined once, in `schemas/vocabulary.v1.json`, and referenced by both schemas through `$ref`. The brief generator and the validator's messages read the allowed values from the same file.

| Field | Values |
|---|---|
| `camera.move` | static, push_in, pull_out, pan_left, pan_right, tilt_up, tilt_down |
| `camera.intensity` | low, medium, high |
| `atmosphere[]` | rain, snow, fog, mist, dust_motes, fireflies, embers, firelight_flicker, falling_leaves, sun_rays, sparkles, wind |
| `ambience` | none, forest_day, forest_night, meadow, village, river, rain, ocean_shore, fireplace_indoor, night_crickets, cave, wind |
| `delivery` | neutral, warm, gentle, cheerful, excited, curious, surprised, sad, worried, scared, angry, whisper, proud, thoughtful |
| `position` | left, center_left, center, center_right, right, background |
| `facing` | left, right, camera, away |
| `time_of_day` | dawn, morning, midday, afternoon, dusk, night |

`emotion`, `pose` and `expression` stay free text (at most 12 words). They feed image prompts, where nuance helps and nothing downstream branches on their values. Growing the vocabulary is an additive change and needs a new OpenSpec change. `delivery` is recorded now but Kokoro can't act on it, so a later change will map it to speed or pauses.

### 4. Kokoro voice allowlist as data
`schemas/kokoro-voices.en.json` lists the English Kokoro-82M presets (American `af_*`/`am_*`, British `bf_*`/`bm_*`) with accent and gender. Kokoro's `lang_code` (`a`/`b`) follows from the prefix, so the manifest never needs to carry it. The list is checked against the installed Kokoro package once, when the narration change lands.

### 5. Episode manifest shape
It follows the example agreed in conversation. Key points:
- `cast`, `locations` and `props` are declared at the top, and shots refer to them by id.
- Characters must already exist in the bible. Defining them inline is rejected, because a character's appearance and voice have to be frozen before images exist.
- Lines are `{speaker, text, delivery, on_screen?, pause_after?}`. The narrator is a regular cast id with `kind: narrator` in the bible, so no special-case speaker syntax is needed.
- `pronunciations` is a top-level map from single display words to spoken forms. A single-word key keeps a 1:1 mapping between display words and spoken words, which the future word-level caption stage relies on.

### 6. Strict YAML loading
PyYAML's `safe_load` is extended to **reject duplicate keys** (by default a duplicate silently overwrites the earlier value) and to reject YAML anchors and aliases. Values PyYAML 1.1 misreads (`on_screen: yes`, `no` → `false`, `1:30` → `90`) surface as schema type errors, because every field has a strict type. The brief tells ChatGPT to quote all strings.

### 7. Runtime estimate
Estimated seconds = words ÷ (140 wpm × the speaker's voice speed) + `pause_after` + 0.4 s between lines. A word is a whitespace-separated token containing a letter or digit. This is reported only, and never stored. 140 wpm is a calm all-ages pace. The narration change will measure real Kokoro rates and may tune it.

### 8. CLI layout
```
pyproject.toml            # package "story-pipeline", console script "story"
pipeline/story/
  cli.py                  # argparse: new | validate | brief
  load.py                 # strict YAML loader, project-root discovery
  schema.py               # pass 1 (jsonschema) → Finding list
  lint_series.py, lint_episode.py   # pass 2
  report.py               # text and --json renderers, exit codes
  brief.py                # renders the ChatGPT brief from a template
  templates/brief.md.tmpl
schemas/                  # contracts (see 1, 3, 4)
series/example-meadow/    # example series (fixture + brief example source)
episodes/                 # real episodes live here
tests/                    # pytest; golden valid + one-defect-per-file invalid fixtures
```
- The project root is the nearest ancestor containing `schemas/`. `--root` overrides it for tests.
- The venv is created with `uv venv --python 3.11`.
- Dependencies are limited to `PyYAML` and `jsonschema`, plus `pytest` for development.
- Findings are sorted by file, path and rule, so reports come out byte-identical on every run.

### 9. Brief generation
The brief template interpolates the vocabulary table, the series cast (id, name, description, narrator flag), and the example episode from `series/<id>/example-episode.yaml`. A test validates that example on every run, so the brief can never ship an invalid example.

### 10. The brief is a two-mode ChatGPT Project instruction
The producer brainstorms naturally and should never have to think in YAML until the story is final. The brief is therefore written to be installed **once** as the instructions of a ChatGPT Project (one Project per series), not pasted per episode:
- **Creative mode (default):** conversation, prose drafts, and a readable plain-text storyboard. No YAML.
- **Lock ("Lock this story"):** a pre-flight check of the blocking decisions, then exactly one fenced YAML block. A blocking decision is one the validator would reject or ChatGPT would have to invent: a character outside the cast, an unagreed ending or storyboard, or an unstated `made_for_kids`. Anything ChatGPT can reasonably choose itself (camera, atmosphere, publishing copy, and the id when none is given) is not blocking.
- **Revisions after a lock** return to creative mode. Every lock emits a complete replacement manifest, never a patch, so `episode.yaml` is simply overwritten and revalidated, and downstream stages rebuild from it.
- *Alternative: ChatGPT also emits the Gemini image-prompt pack.* Rejected: prompt wording would drift episode to episode and undermine character consistency, and everything in such a prompt can be derived from the bible and the locked manifest. The pack will be generated by the pipeline (`story prompts`, in a later change).

Lock-mode behavior is enforced only by instructions. It is verified by the manual round trip in task 7.1 and, above all, by `story validate` on whatever ChatGPT returns.

### 11. Derived line ids
Lines carry no authored id. Downstream stages derive `sNN-lMM` from position. Authored ids would be one more thing ChatGPT could get wrong, and a relock replaces the whole manifest anyway, so hash-bound approvals (not ids) detect what changed.

### 12. Checkpoints carried into later changes
The production flow keeps three human checkpoints: (1) story and storyboard, which is approval by locking in ChatGPT; (2) the image contact sheet; (3) the final preview video, which includes the audio review. This change implements none of them. The decision is recorded here so the next changes inherit it.

## Risks / Trade-offs

- [ChatGPT drifts from the schema: extra fields, invented enums] → Strict rejection plus field-path error messages written to be pasted back into ChatGPT. The `--json` output lets a Claude skill do that loop later.
- [The closed vocabulary is too narrow for a story] → Additive vocabulary changes are cheap. Free-text `emotion`, `pose` and `expression` absorb nuance meanwhile.
- [Requiring characters in the bible first adds a step for one-off characters] → Intentional: an undefined character can't be drawn consistently or given a stable voice. A later change can add a `story add-character` helper if this becomes friction.
- [The runtime estimate is inaccurate before real TTS measurements] → It's informational only and never feeds timing.
- [ChatGPT ignores lock-mode discipline: YAML during brainstorming, or invented details at lock] → Clear mode rules and a blocking-question list in the brief. Whatever comes back is validated strictly before it is used.
- [Long Project conversations drift away from the instructions] → The brief repeats the key lock rules next to the example. The producer can say "Lock this story" in a fresh reply after restating the agreed storyboard.
- [JSON Schema error messages are cryptic by default] → Pass-1 errors are rewritten into plain messages. For enum errors the message lists the allowed values.

## Open Questions

- The actual first series name, style and cast, and the narrator voice. These are decided when you author the real bible and don't affect this change. The example series only proves the contract.
