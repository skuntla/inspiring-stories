# Tasks

## 1. Setup

- [ ] 1.1 Add Pillow to `pyproject.toml` dependencies and install it into `.venv`; verify `.venv/bin/python -c "import PIL"` succeeds
- [ ] 1.2 Confirm no image path is ignored by git (only `build/` is); verify `git check-ignore` reports nothing for `episodes/x/images/s01.png`, `episodes/x/images/locations/foggy-meadow.png`, `episodes/x/images/thumbnail.png` and `series/willow-meadow/style/ref-01.png`, and that `episodes/x/build/images.json` is ignored

## 2. Contract extensions

- [ ] 2.1 Extend `story-series.v1.schema.json` with optional `locations` (id, description, 1–3 references) and optional `references.expressions`; extend series lint (duplicate location ids, location id vs character id collision, location reference folder, expression-sheet folder, narrator may not declare it, presence warnings for all reference kinds); verify one mutation test per rule in `tests/test_series.py`
- [ ] 2.2 Allow an empty episode `locations` list, resolve shot locations against episode then series locations, and report an error when an episode redeclares a series location id; verify tests for series location use, redeclaration, and an unknown location reported against both sources
- [ ] 2.3 Make `publishing.thumbnail.characters` required in `story-episode.v1.schema.json` (unique kebab ids, may be empty) and lint it (each id in cast, not the narrator); verify mutation tests for a missing field, a non-cast id, the narrator, and an empty list
- [ ] 2.4 Add a recurring-locations section to both ChatGPT renderings (omitted when the series has none) with the use-without-redeclaring rule, and add `thumbnail.characters` with its rule (visible cast ids only, never the narrator, `[]` if none) to both renderings' manifest structure; verify tests for presence and absence of locations, the thumbnail field and rule in both renderings, and that the compact rendering of a fixture with locations stays within 8,000 characters

## 3. Prompt packs

- [ ] 3.1 Implement anchor derivation (episode-only locations used by 2+ shots → `images/locations/<id>.png`) and attachment selection (style → location refs, from the series or the episode anchor → per-character view by facing → expression sheets for on-screen speakers; cap 6 with the defined drop order; missing files marked); verify table-driven tests covering anchor derivation (2+ shots, single-use, series location), each facing, the speaker rule, anchor placement after the style reference, the cap and drop note, and missing-file marking
- [ ] 3.2 Implement shot prompt rendering from `templates/shot-prompt.md.tmpl` (verbatim identity blocks, location and time of day, props, staging, action, emotion, composition, camera headroom, animation preparation, in-drawing vs animated atmosphere split, style, exclusions, no line text, input digests); verify tests for verbatim identity, the atmosphere split, and absence of every line's text
- [ ] 3.3 Implement the location-anchor prompt (`templates/location-anchor.md.tmpl`: 16:9 establishing view, no characters, style reference attached) and the thumbnail prompt (concept, style, identity blocks and front views for exactly `publishing.thumbnail.characters`, never inferred from the concept; explicit no-text rule; hook excluded; "draw no characters" when the list is empty); verify tests that a character named only in the concept is not included, that the hook text is absent, and the empty-list case
- [ ] 3.4 Implement `story prompts <episode-dir>` (refuse on validation errors, clear and rewrite `build/prompts/`, `index.md` checklist ordered anchors → shots → thumbnail, warn on missing references); verify tests for a valid pack, index order, refusal, byte-identical regeneration, and removal of a dropped shot's file
- [ ] 3.5 Implement `story prompts <series-dir>` (one prompt per declared reference slot from `templates/reference-prompt.md.tmpl` in generation order, with style and front-view chaining, save-as paths equal to declared paths); verify tests for completeness, order and chained attachments

## 4. Image intake

- [ ] 4.1 Implement expected-file discovery for episodes (shot ids, the required thumbnail, and anchors in `images/locations/`, each `.png`/`.jpg`/`.jpeg`) and series (declared reference paths), with missing (including the thumbnail and anchors), duplicate, unexpected and ignored-file findings; verify one test per case
- [ ] 4.2 Implement per-image checks (decodable, aspect within 2% of 16:9 where required, shorter side at least 720 as an error, below 1920×1080 as a warning); verify tests with generated fixtures at 1920×1080, 1344×768, 1024×1024, 1000×500 and a corrupt file
- [ ] 4.3 Write canonical `build/images.json` and `build/contact-sheet.png` (4 columns; anchors, then shots, then the thumbnail; labelled tiles with shot action; placeholders for missing or corrupt images); verify byte-identical `images.json` across runs and a contact-sheet test checking tile count and dimensions
- [ ] 4.4 Implement `story images <dir>` (validate inputs first and stop on errors, text and `--json` reports, exit codes, approval status line); verify CLI tests for a clean intake, a missing image, and an invalid manifest

## 5. Approvals

- [ ] 5.1 Implement `approvals.yaml` (`story-approvals/v1`) read/append with the strict loader, input collection for the `images` checkpoint (manifest, bible, shots, thumbnail, anchors, attached series references) and the `references` checkpoint, and a canonical digest; verify tests for first approval, append on re-approval, and entry contents
- [ ] 5.2 Implement status (approved / stale naming each changed, added or removed input / not approved) and `story approve <dir> <checkpoint>` (refuses on intake errors, exit 2 for unknown checkpoints); verify tests for a replaced image, a replaced anchor, a relocked manifest, a regenerated reference image, approval blocked by a missing thumbnail, and an unknown checkpoint

## 6. Documentation for the producer

- [ ] 6.1 Add `docs/producing-an-episode.md`: install the compact instructions, lock in ChatGPT, `story new` / `validate`, generate series references once (`story prompts series/...`, `story images`, `story approve ... references`), then per episode `story prompts`, Gemini (anchors first, then shots, then the thumbnail), `story images`, review the contact sheet, `story approve ... images`, and commit the approved images; verify every command in it runs against the example series in a test or by hand

## 7. Willow Meadow data

- [ ] 7.1 Add recurring locations `pip-cottage-interior`, `willow-meadow-path`, `ben-burrow-exterior` and `ben-burrow-interior` (descriptions without time or weather) and expression-sheet slots for `pip`, `ben` and `wren` to `series/willow-meadow/series.yaml`; verify `story validate series/willow-meadow` reports 0 errors
- [ ] 7.2 In `episodes/2026-09-22-pip-and-the-foggy-path/episode.yaml`, remove the four now-duplicate location declarations and add `publishing.thumbnail.characters: ["pip"]` (no other edits); verify `story validate` reports 0 errors and `git diff` touches only those lines
- [ ] 7.3 Add `thumbnail.characters` to `series/example-meadow/example-episode.yaml` and `series/willow-meadow/example-episode.yaml`; verify the repo-series tests pass
- [ ] 7.4 Regenerate `chatgpt-project-instructions.md` and `chatgpt-reference.md` for `willow-meadow`; verify the repo-series tests pass and the compact file is at most 8,000 characters
- [ ] 7.5 Generate the Willow Meadow reference pack and the Foggy Path shot pack; verify both commands exit 0 and the episode index lists the `foggy-meadow` and `old-fence-crossing` anchors, then s01–s16, then the thumbnail

## 8. Verification

- [ ] 8.1 Run the full test suite and `openspec validate add-prompt-packs-and-image-intake --strict`; verify both pass
- [ ] 8.2 Producer round trip: generate the Willow Meadow reference images from the pack, run `story images series/willow-meadow`, approve `references`; then generate the Foggy Path anchors and at least three shots set at `foggy-meadow`, run `story images` on the episode and check the contact sheet, the findings (including the missing-thumbnail error), and whether the anchor kept the fog meadow consistent across those shots; record the results in `notes.md`
