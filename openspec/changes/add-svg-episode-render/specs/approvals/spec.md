# Spec Delta

## Purpose

Records human approval of the rendered preview as digests of exactly what was approved, so any later change is detected and the approval becomes stale instead of silently carrying over.

## ADDED Requirements

### Requirement: Preview approval
`story approve <episode> preview` SHALL record, in the episode's `approvals.yaml` (`story-approvals/v1`, append-only, committed), the UTC time and the SHA-256 of every input covered: the manifest, the series bible, `build/speech.json`, `build/timeline.json`, `build/preview.mp4`, and every component source file the episode uses. It SHALL refuse, writing nothing, when the preview is missing or older than the timeline.

#### Scenario: Approve a fresh preview
- **WHEN** the preview was rendered from the current timeline and `story approve <episode> preview` runs
- **THEN** an entry with every input hash is appended and the exit code is 0

#### Scenario: Unknown checkpoint
- **WHEN** `story approve <episode> images` runs
- **THEN** the exit code is 2 and the message lists `preview` as the supported checkpoint

### Requirement: Staleness
`story render` SHALL report the preview approval as `approved`, `stale` (naming each input that was added, removed or changed) or `not approved`. A final render SHALL warn when the preview approval is not `approved`.

#### Scenario: Rig edited after approval
- **WHEN** Pip's rig component changes after the preview was approved
- **THEN** the status is `stale` and names the rig file
