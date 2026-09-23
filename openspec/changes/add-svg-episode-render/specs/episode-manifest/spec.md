# Spec Delta

## MODIFIED Requirements

### Requirement: Shots
The manifest SHALL contain an ordered list of between 1 and 30 shots whose ids are `s01`, `s02`, … in sequence with no gaps. Each shot SHALL declare a location, time of day, the characters visible (each with position, facing, `stance` and `mood` from the closed vocabulary, free-text pose and expression as extra direction, and each a member of the cast), an action description, an emotion, a camera intent (move and intensity), zero or more atmosphere effects, an ambience key, composition notes, and at least one line. Shot counts outside 4–16 SHALL produce a warning, not an error, because story length varies.

#### Scenario: Gap in shot ids
- **WHEN** shots are `s01`, `s02`, `s04`
- **THEN** validation reports an error naming the expected id `s03`

#### Scenario: Visible character not in cast
- **WHEN** a shot shows character `fox` and `fox` is not in the episode cast
- **THEN** validation reports an error at that shot's path

#### Scenario: Very long story
- **WHEN** an episode has 20 shots
- **THEN** validation succeeds with a shot-count warning

#### Scenario: Missing rig state
- **WHEN** a visible character has no `stance`
- **THEN** validation reports a missing-field error at that character's path

#### Scenario: Unknown mood
- **WHEN** a visible character declares `mood: "ecstatic"`
- **THEN** validation reports an error listing the allowed moods
