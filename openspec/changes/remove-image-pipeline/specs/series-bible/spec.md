# Spec Delta

## MODIFIED Requirements

### Requirement: Visual style definition
The series bible SHALL define a visual style consisting of a non-empty style description and a list of things to avoid. The content rating SHALL be `all-ages`. The style carries no reference images; the series is rendered from code.

#### Scenario: Missing style description
- **WHEN** `style.description` is empty or absent
- **THEN** validation reports an error

#### Scenario: Style reference outside the series folder
- **WHEN** `style` declares `references` with any path, inside the series folder or not
- **THEN** validation reports an unknown-field error, because style reference images no longer exist

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

## ADDED Requirements

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

## REMOVED Requirements

### Requirement: Reference image presence
**Reason**: Characters, settings and thumbnails are rendered as SVG from code; there are no reference images to generate or check.
**Migration**: Delete `style.references` and every character `references` block from series bibles. Visual identity lives in the SVG character rigs and set pieces introduced by the rendering change.
