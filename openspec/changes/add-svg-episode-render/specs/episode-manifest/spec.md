# Spec Delta

## MODIFIED Requirements

### Requirement: Shots
The manifest SHALL contain an ordered list of between 1 and 60 shots whose ids are `s01`, `s02`, … in sequence with no gaps. Each shot SHALL declare a location, time of day, the characters visible (each with position, facing, `stance` and `mood` from the closed vocabulary, free-text pose and expression as extra direction, and each a member of the cast), an action description, an emotion, a camera intent (move and intensity), zero or more atmosphere effects, an ambience key, composition notes, and at least one line. Shot counts outside 4–40 SHALL produce a warning, not an error, because a story takes the length it needs.

#### Scenario: Gap in shot ids
- **WHEN** shots are `s01`, `s02`, `s04`
- **THEN** validation reports an error naming the expected id `s03`

#### Scenario: Visible character not in cast
- **WHEN** a shot shows character `fox` and `fox` is not in the episode cast
- **THEN** validation reports an error at that shot's path

#### Scenario: Very long story
- **WHEN** an episode has 45 shots
- **THEN** validation succeeds with a shot-count warning

#### Scenario: Missing rig state
- **WHEN** a visible character has no `stance`
- **THEN** validation reports a missing-field error at that character's path

#### Scenario: Calm mood
- **WHEN** a visible character declares `mood: "calm"`
- **THEN** validation reports no error

#### Scenario: Unknown mood
- **WHEN** a visible character declares `mood: "ecstatic"`
- **THEN** validation reports an error listing the allowed moods

## ADDED Requirements

### Requirement: Shot framing
A shot's camera MAY declare `framing` (`wide`, `medium` or `close`; default `wide`) and `subject`, the id of a character visible in that shot. A `medium` or `close` shot without a subject SHALL frame its first on-screen speaker, or else its first visible character; such a shot with no visible character SHALL be an error.

#### Scenario: Close-up on a visible character
- **WHEN** a shot declares `camera: {move: "push_in", intensity: "low", framing: "close", subject: "gardener"}` and the gardener is visible
- **THEN** validation reports no error

#### Scenario: Subject not in the shot
- **WHEN** a shot declares `subject: "gardener"` and the gardener is not visible in it
- **THEN** validation reports an error at that shot's camera path

#### Scenario: Close-up of nobody
- **WHEN** a shot declares `framing: "close"` and shows no characters
- **THEN** validation reports an error
