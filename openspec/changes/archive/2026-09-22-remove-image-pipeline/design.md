# Design

## Context

See proposal.md. The image pipeline was implemented on `main` (commit 186cbcc) under the change `add-prompt-packs-and-image-intake`. That change was never archived, so the main specs never gained its requirements. The main specs still carry the original reference-image requirements from `establish-episode-contract`. The SVG proof of concept (`poc/svg-rig/`) replaces all of it.

## Goals / Non-Goals

**Goals:**
- Leave only what the SVG pipeline needs: the story contract, validation, the ChatGPT story brief, and the series data the renderer will use.
- Keep main green throughout: every bible and manifest in the repository still validates after the change.

**Non-Goals:**
- Building the SVG renderer, rigs or set pieces (the next change).
- Reintroducing approvals. They return with the render change and will cover the rendered preview.

## Decisions

### 1. Carry forward what SVG needs from the abandoned change
Recurring series locations and `publishing.thumbnail.characters` are already implemented and useful to a code renderer: set pieces keyed by location id, and a thumbnail composed from rigs. They are re-specified here, without any image fields, because the abandoned change's specs were never synced. Expression sheets, anchors, prompt packs, intake and approvals are dropped.

### 2. Reference fields become unknown fields
The schemas drop `references` everywhere (style, characters, locations). An old bible that still declares them fails validation with the standard unknown-field error. The contract has no external consumers, and the two bibles in the repository are migrated in the same commit, so strictness beats silent tolerance.

### 3. Remove modules, don't disable them
`prompts.py`, `images.py`, `approvals.py`, their template, tests and producer doc are deleted rather than left unused. Git keeps them if any piece is ever wanted again. The CLI shrinks back to `validate`, `new` and `brief`, and `_checked` no longer builds prompt contexts.

### 4. The ChatGPT prohibitions stay as written
The instructions still forbid ChatGPT from writing image or drawing prompts, timings, paths, voices and line ids. That is still correct: the renderer derives drawing from the manifest.

## Risks / Trade-offs

- [The SVG look depends on hand-built rigs and set pieces per series] → Accepted. This is the maintainability trade the producer chose; the next change defines the rig contract.
- [Approvals disappear until the render change] → No checkpoint is lost in practice: the only approval that existed covered images, which no longer exist.
