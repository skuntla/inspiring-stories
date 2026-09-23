# Spec Delta

## Purpose

Records human approval at pipeline checkpoints as digests of exactly what was approved, so any later change to an approved input is detected and the approval becomes stale instead of silently carrying over.

## ADDED Requirements

### Requirement: Approval records
Approvals SHALL be stored in `approvals.yaml` in the episode or series folder, declaring `schema: story-approvals/v1` and holding an append-only list of entries. Each entry has a checkpoint name, the UTC time of approval, an overall digest, and the SHA-256 of every input it covers. The latest entry for a checkpoint is the effective one. The file and the images it approves are committed to version control, so an approval can be both verified and restored.

#### Scenario: First approval
- **WHEN** the producer approves the images of an episode that has no `approvals.yaml`
- **THEN** `approvals.yaml` is created with one `images` entry holding the digest and per-input hashes

#### Scenario: Re-approval
- **WHEN** an episode's images are approved a second time after a change
- **THEN** a second entry is appended, and earlier entries are kept unchanged

### Requirement: Checkpoints and their inputs
An episode SHALL support the `images` checkpoint, which covers the manifest, the series bible, every shot image, the thumbnail, every episode location anchor, and every series reference image attached by the episode's prompt pack. A series SHALL support the `references` checkpoint, which covers the series bible and every declared reference image. Any other checkpoint name SHALL be a usage error.

#### Scenario: Unknown checkpoint
- **WHEN** `story approve episodes/2026-09-22-pip-and-the-foggy-path audio` is run
- **THEN** the command exits with code 2 and lists the supported checkpoints

### Requirement: Approve command
`story approve <dir> <checkpoint>` SHALL recompute the checkpoint's inputs and record an approval only when the corresponding intake (`story images <dir>`) has no errors. Otherwise it SHALL report the errors, write nothing, and exit with code 1.

#### Scenario: Approval blocked by a missing image
- **WHEN** `s16` is missing and `story approve <episode-dir> images` is run
- **THEN** no approval is recorded and the exit code is 1

#### Scenario: Successful approval
- **WHEN** intake is clean and `story approve <episode-dir> images` is run
- **THEN** an approval entry is appended and the exit code is 0

### Requirement: Staleness
The status of a checkpoint SHALL be `approved` when the recomputed inputs match the effective entry, `stale` when any input was added, removed or changed since, and `not approved` when there is no entry. A stale status SHALL name each input that differs.

#### Scenario: Image replaced after approval
- **WHEN** `images/s03.png` is replaced after the `images` checkpoint was approved
- **THEN** the status is `stale` and names `images/s03.png`

#### Scenario: Manifest relocked after approval
- **WHEN** `episode.yaml` changes after the `images` checkpoint was approved
- **THEN** the status is `stale` and names `episode.yaml`

#### Scenario: Unchanged
- **WHEN** nothing has changed since approval
- **THEN** the status is `approved`
