# Spec Delta

## Purpose

Checks the images the producer brings back from Gemini, before anything builds on them: completeness, format, shape and size. It records their metadata and produces a contact sheet for human approval.

## ADDED Requirements

### Requirement: Expected files
`story images <episode-dir>` SHALL expect, in `images/`, one image per shot named by shot id (`s01`, `s02`, …), a `thumbnail`, and one anchor per anchored episode location in `images/locations/` named by location id, each with a `.png`, `.jpg` or `.jpeg` extension. `story images <series-dir>` SHALL expect every reference image path declared in the bible. A missing expected image SHALL be an error. Two files for the same image (for example `s03.png` and `s03.jpg`) SHALL be an error. Any other file SHALL be a warning; system files such as `.DS_Store` are ignored.

#### Scenario: Missing shot image
- **WHEN** `images/` contains `s01.png` to `s15.png` for a 16-shot episode
- **THEN** the report contains an error naming `images/s16.png`

#### Scenario: Missing thumbnail
- **WHEN** every shot image is present but `images/thumbnail.png` is not
- **THEN** the report contains an error naming `images/thumbnail.png`, and the images checkpoint cannot be approved

#### Scenario: Missing location anchor
- **WHEN** `foggy-meadow` is anchored and `images/locations/foggy-meadow.png` does not exist
- **THEN** the report contains an error naming it

#### Scenario: Duplicate image
- **WHEN** `images/` contains both `s03.png` and `s03.jpg`
- **THEN** the report contains an error naming both files

#### Scenario: Unexpected file
- **WHEN** `images/` contains `s03-old.png`
- **THEN** the report contains a warning naming it

### Requirement: Image checks
Each image SHALL be decodable as PNG or JPEG. Shot images, the thumbnail, episode location anchors, style references and series location references SHALL have an aspect ratio within 2% of 16:9; character references MAY have any aspect ratio. An image whose shorter side is under 720 pixels SHALL be an error; a 16:9 image smaller than 1920×1080 SHALL be a warning noting that it will be upscaled and camera movement limited.

#### Scenario: Wrong aspect ratio
- **WHEN** `s05.png` is 1024×1024
- **THEN** the report contains an aspect-ratio error for `s05.png`

#### Scenario: Small but usable
- **WHEN** `s05.png` is 1344×768
- **THEN** the report contains a size warning and no error for `s05.png`

#### Scenario: Corrupt file
- **WHEN** `s05.png` cannot be decoded
- **THEN** the report contains an error for `s05.png`

### Requirement: Validate inputs first
`story images` SHALL validate the manifest and series bible first, and SHALL stop with their errors, without checking images, when either has errors.

#### Scenario: Invalid manifest
- **WHEN** the episode manifest has an error
- **THEN** the report lists that error and no image findings, and the exit code is 1

### Requirement: Metadata record
`story images` SHALL write `build/images.json` listing, for each expected image that is present, its path, SHA-256, format, width and height, together with the SHA-256 of the manifest and series bible it was checked against. The file SHALL be byte-identical for identical inputs.

#### Scenario: Repeat intake
- **WHEN** `story images` is run twice on unchanged files
- **THEN** `build/images.json` is byte-identical between runs

### Requirement: Contact sheet
`story images` SHALL write `build/contact-sheet.png`: a grid of every expected image in order (location anchors, then shots, then the thumbnail for an episode), each tile labelled with its id (location id, shot id, `thumbnail`, or reference slot), and each shot tile also labelled with its action. A missing or undecodable image SHALL appear as a labelled placeholder tile, so the sheet always shows the complete set.

#### Scenario: Sheet with a missing image
- **WHEN** `s16` is missing
- **THEN** the contact sheet contains a tile labelled `s16` marked as missing

### Requirement: Report and exit codes
`story images` SHALL report findings in the same text and `--json` formats as `story validate`, followed by the approval status of the directory's checkpoint (see approvals). It exits 0 when there are no errors, 1 when there are errors, and 2 on usage errors.

#### Scenario: Clean intake
- **WHEN** every image is present and passes its checks
- **THEN** the exit code is 0 and the report ends with the approval status
