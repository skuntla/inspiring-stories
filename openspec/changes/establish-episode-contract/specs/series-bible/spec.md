# Spec Delta

## Purpose

Defines the reusable, per-series description of visual style, recurring characters and their voices, so that every episode in a series draws on one frozen identity instead of re-describing it.

## ADDED Requirements

### Requirement: Series bible location and schema
Each series SHALL be defined by exactly one file at `series/<series-id>/series.yaml` declaring `schema: story-series/v1`. The `id` field MUST equal the folder name and MUST be kebab-case.

#### Scenario: Valid series file
- **WHEN** `series/kind-hearts/series.yaml` declares `schema: story-series/v1` and `id: kind-hearts`
- **THEN** validation reports no errors for location or identity

#### Scenario: Folder and id disagree
- **WHEN** `series/kind-hearts/series.yaml` declares `id: kindhearts`
- **THEN** validation reports an error naming both the folder name and the declared id

#### Scenario: Unsupported schema version
- **WHEN** a series file declares `schema: story-series/v2`
- **THEN** validation reports an unsupported-version error and performs no further checks on that file

### Requirement: Strict structure
The series bible SHALL reject any field not defined by the `story-series/v1` schema and any enum value outside the defined vocabulary.

#### Scenario: Unknown field
- **WHEN** a character entry contains a field `hair_colour_hex`
- **THEN** validation reports an unknown-field error at that character's path

### Requirement: Visual style definition
The series bible SHALL define a visual style consisting of a non-empty style description used verbatim in every image prompt, a list of things to avoid, and one to three style reference image paths under `series/<series-id>/style/`. The content rating SHALL be `all-ages`.

#### Scenario: Missing style description
- **WHEN** `style.description` is empty or absent
- **THEN** validation reports an error

#### Scenario: Style reference outside the series folder
- **WHEN** a style reference path resolves outside `series/<series-id>/style/`
- **THEN** validation reports an error

### Requirement: Character roster
The series bible SHALL list its characters, each with a unique kebab-case `id`, a display name, a visual description, a canonical outfit, a list of distinguishing features, and reference image slots `front`, `three_quarter` and `side` whose paths lie under `series/<series-id>/characters/<id>/`. Exactly one entry SHALL have `kind: narrator`; the narrator has a voice but no visual fields or reference slots.

#### Scenario: Duplicate character id
- **WHEN** two characters share the id `fox`
- **THEN** validation reports a duplicate-id error

#### Scenario: No narrator
- **WHEN** no character has `kind: narrator`
- **THEN** validation reports an error

#### Scenario: Narrator with visual fields
- **WHEN** the narrator entry defines `outfit` or reference slots
- **THEN** validation reports an error

### Requirement: Character voices
Every character, including the narrator, SHALL declare a voice consisting of a Kokoro voice id from the project's English voice allowlist and a speed between 0.5 and 2.0 inclusive.

#### Scenario: Voice not in allowlist
- **WHEN** a character declares voice `zf_xiaobei`
- **THEN** validation reports an error listing the allowed English voices

#### Scenario: Speed out of range
- **WHEN** a character declares speed `2.5`
- **THEN** validation reports an out-of-range error

### Requirement: Reference image presence
Validation SHALL check whether every declared style and character reference image exists. A missing reference image SHALL be reported as a warning, not an error, so that a bible can be authored before its images are generated.

#### Scenario: Reference image not yet generated
- **WHEN** `characters/fox/ref-front.png` is declared but does not exist on disk
- **THEN** validation succeeds with a warning naming the missing file
