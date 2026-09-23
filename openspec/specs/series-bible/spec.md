# series-bible Specification

## Purpose

Defines the reusable, per-series description of visual style, recurring characters and their voices, so that every episode in a series draws on one frozen identity instead of re-describing it.

## Requirements

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
The series bible SHALL define a visual style consisting of a non-empty style description and a list of things to avoid. The content rating SHALL be `all-ages`. The style carries no reference images; the series is rendered from code.

#### Scenario: Missing style description
- **WHEN** `style.description` is empty or absent
- **THEN** validation reports an error

#### Scenario: Style reference outside the series folder
- **WHEN** `style` declares `references` with any path, inside the series folder or not
- **THEN** validation reports an unknown-field error, because style reference images no longer exist

### Requirement: Audience and series defaults
The series bible MAY declare an `audience` description and a `defaults` section. `defaults.made_for_kids`, when present, SHALL be a boolean giving the value episodes in the series normally declare. Neither field changes the requirement that every episode states `made_for_kids` explicitly.

#### Scenario: Series with a made-for-kids default
- **WHEN** a series declares `defaults: {made_for_kids: false}`
- **THEN** validation reports no errors

#### Scenario: Non-boolean default
- **WHEN** a series declares `defaults: {made_for_kids: "no"}`
- **THEN** validation reports a type error

### Requirement: Character roster
The series bible SHALL list its characters, each with a unique kebab-case `id`, a display name, a visual description, a canonical outfit, and a list of distinguishing features. Exactly one entry SHALL have `kind: narrator`; the narrator has a voice but no visual fields. Characters carry no reference images.

#### Scenario: Duplicate character id
- **WHEN** two characters share the id `fox`
- **THEN** validation reports a duplicate-id error

#### Scenario: No narrator
- **WHEN** no character has `kind: narrator`
- **THEN** validation reports an error

#### Scenario: Narrator with visual fields
- **WHEN** the narrator entry defines `outfit`
- **THEN** validation reports an error

#### Scenario: Character reference images are no longer accepted
- **WHEN** a character declares `references`
- **THEN** validation reports an unknown-field error

### Requirement: Character voices
Every character, including the narrator, SHALL declare a voice consisting of a Kokoro voice id from the project's English voice allowlist and a speed between 0.5 and 2.0 inclusive.

#### Scenario: Voice not in allowlist
- **WHEN** a character declares voice `zf_xiaobei`
- **THEN** validation reports an error listing the allowed English voices

#### Scenario: Speed out of range
- **WHEN** a character declares speed `2.5`
- **THEN** validation reports an out-of-range error

### Requirement: Recurring locations
The series bible MAY declare `locations` for places that recur across episodes, each with a unique kebab-case `id` and a visual description written without time of day or weather (shots add those). Location ids SHALL NOT collide with character ids.

#### Scenario: Valid recurring location
- **WHEN** a series declares location `ben-burrow-exterior` with a description
- **THEN** validation reports no errors for that location

#### Scenario: Duplicate location id
- **WHEN** two series locations share the id `meadow-path`
- **THEN** validation reports a duplicate-id error

#### Scenario: Location id collides with a character
- **WHEN** a series declares location `pip` and a character `pip`
- **THEN** validation reports an id-collision error
