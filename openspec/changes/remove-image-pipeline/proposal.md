# Proposal

## Why

The SVG proof of concept (`poc/svg-rig/`) showed that drawing characters and settings as code gives perfect character consistency, free layering and real viseme lip sync from Kokoro's phonemes. All of it is programmatic and easy to maintain. The Gemini image pipeline existed to work around the problems of painted frames: reference images, prompt packs, image intake and contact sheets. It is now dead weight. The producer has chosen to render everything as SVG.

## What Changes

- **BREAKING** Remove every reference-image concept from the series bible: style reference images, character `references` (front, three-quarter, side and expression sheets), and location reference images, along with their presence warnings. The style description, avoid list, characters, voices, audience and defaults remain.
- Keep **recurring series locations** as `{id, description}` (no images), because SVG set pieces are keyed by location id. Episodes may use a series location directly; redeclaring one is an error.
- Keep **`publishing.thumbnail.characters`** (required list of visible cast ids), because the thumbnail will be composed from SVG characters.
- Both ChatGPT renderings list the recurring locations and the thumbnail-characters rule. ChatGPT remains the story writer; nothing about the story contract changes.
- Remove the image tooling: `story prompts`, `story images`, `story approve`, their modules, templates and tests, `docs/producing-an-episode.md`, and the Pillow dependency. Hash-bound approvals return with the render change, where they will cover the rendered preview.
- The unfinished change `add-prompt-packs-and-image-intake` is abandoned. It was never archived, and its folder has been removed; git history keeps it.
- Update the project context: no Gemini; rendering is SVG in Remotion; checkpoints become story lock and final preview.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `series-bible`: style and characters lose reference-image slots; the reference-presence requirement is removed; recurring locations are added (id and description only).
- `episode-manifest`: shots may use recurring series locations; `publishing.thumbnail.characters` is required; both ChatGPT renderings list recurring locations and the thumbnail rule.

## Impact

- Code removed: `pipeline/story/prompts.py`, `images.py`, `approvals.py`, `templates/prompt-file.md.tmpl`, `tests/test_prompts.py`, `test_images.py`, `test_approvals.py`, `docs/producing-an-episode.md`. The CLI keeps `validate`, `new` and `brief`.
- Schemas: `story-series/v1` drops the `references` fields (style, characters, locations). All bibles in the repository are migrated in the same commit.
- Data: `series/example-meadow` and `series/willow-meadow` lose their reference paths; both ChatGPT renderings are regenerated. The producer re-pastes the compact instructions.
- Dependencies: Pillow is removed.
- Unaffected: the Foggy Path episode manifest, `poc/svg-rig/`, and `sandcastle-film.html`.
