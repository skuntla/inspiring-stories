# Tasks

## 1. Contracts and validation

- [x] 1.1 Drop `references` from `story-series.v1.schema.json` (style, characters, locations) and remove the reference-location and reference-presence rules and the expression-sheet handling from the series lint; keep recurring locations (duplicate ids, collision with character ids); verify series tests cover `references` rejected as unknown for style, a character and a location, plus the location rules
- [x] 1.2 Migrate `series/example-meadow/series.yaml` and `series/willow-meadow/series.yaml` (remove style, character and location references); verify `story validate` reports 0 errors and 0 warnings for both series and for the Foggy Path episode

## 2. Remove the image tooling

- [x] 2.1 Delete `pipeline/story/prompts.py`, `images.py`, `approvals.py`, `templates/prompt-file.md.tmpl`, `tests/test_prompts.py`, `tests/test_images.py`, `tests/test_approvals.py` and `docs/producing-an-episode.md`; remove the `prompts`, `images` and `approve` commands and the approval field of the report; verify `story --help` lists only `validate`, `new` and `brief`
- [x] 2.2 Remove Pillow from `pyproject.toml` and reinstall; verify the test suite passes without Pillow imported anywhere (`grep -r PIL pipeline tests` finds nothing)

## 3. ChatGPT documents and project context

- [x] 3.1 Regenerate `series/willow-meadow/chatgpt-project-instructions.md` and `chatgpt-reference.md`; verify the repo-series tests pass and the compact file is at most 8,000 characters
- [x] 3.2 Update `openspec/config.yaml` context: no Gemini, SVG rendering in Remotion from code, checkpoints are story lock and final preview; verify no remaining mention of Gemini or prompt packs in `openspec/config.yaml`, `pipeline/` or `series/`

## 4. Verification

- [x] 4.1 Run the full test suite and `openspec validate remove-image-pipeline --strict`; verify both pass
