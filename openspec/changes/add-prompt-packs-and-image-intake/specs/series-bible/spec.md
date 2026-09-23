# Spec Delta

## ADDED Requirements

### Requirement: Recurring locations
The series bible MAY declare `locations`, each with a unique kebab-case `id`, a visual description written without time-of-day or weather (those belong to shots), and one to three reference image paths under `series/<series-id>/locations/<id>/`. Location ids SHALL NOT collide with character ids.

#### Scenario: Valid recurring location
- **WHEN** a series declares location `ben-burrow-exterior` with a description and reference `locations/ben-burrow-exterior/ref-01.png`
- **THEN** validation reports no errors for that location

#### Scenario: Duplicate location id
- **WHEN** two series locations share the id `meadow-path`
- **THEN** validation reports a duplicate-id error

#### Scenario: Location reference outside its folder
- **WHEN** location `meadow-path` declares reference `characters/pip/ref-front.png`
- **THEN** validation reports an error that the reference must be inside `locations/meadow-path/`

### Requirement: Character expression sheets
An on-screen character MAY declare `references.expressions`: one image path under `series/<series-id>/characters/<id>/` showing the character's range of expressions. The narrator SHALL NOT declare it.

#### Scenario: Expression sheet declared
- **WHEN** character `pip` declares `references.expressions: "characters/pip/expressions.png"`
- **THEN** validation reports no errors for that field

#### Scenario: Expression sheet outside the character folder
- **WHEN** character `pip` declares `references.expressions: "style/ref-01.png"`
- **THEN** validation reports an error that the reference must be inside `characters/pip/`

## MODIFIED Requirements

### Requirement: Reference image presence
Validation SHALL check whether every declared reference image exists: style references, character turnarounds, character expression sheets and location references. A missing reference image SHALL be reported as a warning, not an error, so that a bible can be authored before its images are generated.

#### Scenario: Reference image not yet generated
- **WHEN** `characters/fox/ref-front.png` is declared but does not exist on disk
- **THEN** validation succeeds with a warning naming the missing file

#### Scenario: Location reference not yet generated
- **WHEN** `locations/meadow-path/ref-01.png` is declared but does not exist on disk
- **THEN** validation succeeds with a warning naming the missing file
