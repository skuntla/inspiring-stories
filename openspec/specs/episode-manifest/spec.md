# episode-manifest Specification

## Purpose

Defines `episode.yaml` (schema `story-episode/v1`), the single canonical description of one episode's story, shots, spoken lines and publishing copy, which ChatGPT produces and every later pipeline stage consumes.

## Requirements

### Requirement: Manifest location, identity and version
Each episode SHALL be described by `episodes/<episode-id>/episode.yaml` declaring `schema: story-episode/v1`. The episode id MUST have the form `YYYY-MM-DD-<kebab-slug>` and MUST equal the folder name. The `series` field MUST name an existing series bible.

#### Scenario: Unknown series
- **WHEN** an episode declares `series: moonlit-tales` and `series/moonlit-tales/series.yaml` does not exist
- **THEN** validation reports an unknown-series error

#### Scenario: Id does not match folder
- **WHEN** the folder is `episodes/2026-10-01-brave-seed` and the manifest id is `2026-10-02-brave-seed`
- **THEN** validation reports an error naming both values

#### Scenario: Unsupported version
- **WHEN** an episode declares `schema: story-episode/v2`
- **THEN** validation reports an unsupported-version error and performs no further checks

### Requirement: Strict structure and closed vocabulary
The manifest SHALL reject any field not defined by `story-episode/v1`. Camera moves, camera intensity, atmosphere effects, ambience keys, line deliveries, character positions and character facing SHALL each accept only values from the project's published vocabulary.

#### Scenario: Unknown camera move
- **WHEN** a shot declares `camera.move: dolly_zoom`
- **THEN** validation reports an error listing the allowed camera moves

### Requirement: No authored timing or layout
The manifest SHALL NOT contain durations, timestamps, frame numbers, pixel coordinates, file paths or voice ids. The only timing input permitted is an optional per-line `pause_after` between 0 and 3 seconds inclusive.

#### Scenario: Authored shot duration
- **WHEN** a shot contains `duration: 8`
- **THEN** validation reports an unknown-field error explaining that durations are derived from audio

#### Scenario: Pause out of range
- **WHEN** a line declares `pause_after: 5`
- **THEN** validation reports an out-of-range error

### Requirement: Episode metadata
The manifest SHALL declare a title, a one-sentence logline, `language: en`, `content_rating: all-ages`, and `source.kind: original`. A moral is optional.

#### Scenario: Non-English episode
- **WHEN** an episode declares `language: te`
- **THEN** validation reports an error stating that only `en` is supported

### Requirement: Cast, locations and props
The manifest SHALL list the cast it uses by series character id; every listed id MUST exist in the series bible. Characters not in the bible SHALL NOT be defined inline. Locations and props SHALL each be declared once with a unique kebab-case id and a visual description, and shots SHALL reference them by id.

#### Scenario: Character missing from bible
- **WHEN** the cast lists `owl` and the series bible has no `owl`
- **THEN** validation reports an error instructing that `owl` be added to the series bible first

#### Scenario: Undeclared location
- **WHEN** a shot references location `river-bank` that is not declared
- **THEN** validation reports an unknown-location error at that shot's path

#### Scenario: Declared but unused location
- **WHEN** a location is declared but no shot references it
- **THEN** validation reports a warning

### Requirement: Shots
The manifest SHALL contain an ordered list of between 1 and 30 shots whose ids are `s01`, `s02`, … in sequence with no gaps. Each shot SHALL declare a location, time of day, the characters visible (each with position, pose, expression and facing, and each a member of the cast), an action description, an emotion, a camera intent (move and intensity), zero or more atmosphere effects, an ambience key, composition notes, and at least one line. Shot counts outside 4–16 SHALL produce a warning, not an error, because story length varies.

#### Scenario: Gap in shot ids
- **WHEN** shots are `s01`, `s02`, `s04`
- **THEN** validation reports an error naming the expected id `s03`

#### Scenario: Visible character not in cast
- **WHEN** a shot shows character `fox` and `fox` is not in the episode cast
- **THEN** validation reports an error at that shot's path

#### Scenario: Very long story
- **WHEN** an episode has 20 shots
- **THEN** validation succeeds with a shot-count warning

### Requirement: Lines and speakers
Each line SHALL have a speaker, non-empty display text of at most 60 words, and a delivery. The speaker MUST be the narrator or a cast member. A line with `on_screen: true` MUST have a speaker who is visible in that shot and not facing `away`. A line spoken by a cast member not visible in the shot MUST have `on_screen: false`.

#### Scenario: On-screen speaker not in shot
- **WHEN** a line has `speaker: fox` and `on_screen: true` and `fox` is not visible in that shot
- **THEN** validation reports an error

#### Scenario: Narrator line
- **WHEN** a line has `speaker: narrator`
- **THEN** `on_screen` is not required and validation reports no speaker error

#### Scenario: Overlong line
- **WHEN** a line contains 75 words
- **THEN** validation reports an error suggesting the line be split

### Requirement: Pronunciation overrides
The manifest MAY map display words to spoken forms. Overrides SHALL affect only the text sent to speech synthesis; captions SHALL always use display text. Each override key MUST be a single word. An override key that appears in no line SHALL produce a warning.

#### Scenario: Unused override
- **WHEN** `pronunciations` contains `Zephyrine` and no line contains that word
- **THEN** validation succeeds with a warning

#### Scenario: Multi-word key
- **WHEN** `pronunciations` contains the key `Old Oak`
- **THEN** validation reports an error

### Requirement: Publishing copy
The manifest SHALL declare a YouTube title of at most 100 characters, a description of at most 5000 characters, tags whose combined length is at most 500 characters, an explicit `made_for_kids` boolean, and a thumbnail with a hook of at most 40 characters and a visual concept.

#### Scenario: Title too long
- **WHEN** the publishing title has 120 characters
- **THEN** validation reports an error stating the 100-character limit

#### Scenario: Missing audience declaration
- **WHEN** `made_for_kids` is absent
- **THEN** validation reports an error

#### Scenario: Differs from the series default
- **WHEN** the series declares `defaults.made_for_kids: false` and an episode declares `made_for_kids: true`
- **THEN** validation succeeds with a warning asking the producer to confirm the deviation

### Requirement: Runtime estimate
Validation SHALL report an estimated spoken runtime per shot and for the whole episode, computed from word counts at a fixed reference speaking rate plus declared pauses. A shot whose estimate exceeds 30 seconds SHALL produce a warning. The estimate is informational and SHALL NOT be written into the manifest.

#### Scenario: Estimate reported
- **WHEN** a valid episode is validated
- **THEN** the report includes an estimated runtime for each shot and a total

### Requirement: Derived line identifiers
Lines SHALL NOT carry authored identifiers. Downstream stages SHALL identify a line by its position as `<shot id>-l<NN>`, where `NN` is the 1-based two-digit line index within the shot (for example `s03-l02`).

#### Scenario: Authored line id
- **WHEN** a line contains `id: "greeting"`
- **THEN** validation reports an unknown-field error explaining that line ids are derived from position

### Requirement: ChatGPT handoff document
The project SHALL provide, per series, two renderings generated from the schema and the series bible, so both always list the allowed vocabulary and the cast exactly as currently defined:
- **Compact Project instructions**, installed once as ChatGPT Project instructions. They MUST NOT exceed 8,000 characters (ChatGPT's limit); 7,500 is the safety target, enforced by a warning. They SHALL preserve: creative and lock modes; the exact "Lock this story" trigger; the blocking-decision rules; complete replacement after revisions; the series id, audience and made-for-kids default; the approved cast ids; the required manifest field structure; the closed vocabulary; the essential validation rules; and the prohibition on image prompts, line ids, timings, paths and voices. A full example episode is not required.
- **The full reference contract**, kept in the repository and optionally uploaded as a Project file. It contains the same rules in full plus a complete example manifest that MUST pass validation.

Both SHALL define two modes:
- **Creative mode** (the default): ChatGPT discusses the idea conversationally, develops a prose story, and presents a readable plain-text storyboard (one block per shot with visual, emotion, camera, narration and dialogue). It SHALL NOT output YAML in this mode.
- **Lock**: when the producer says "Lock this story", ChatGPT outputs only a complete `story-episode/v1` manifest for the agreed story and storyboard.

Both SHALL state that ChatGPT does not write image-generation prompts, line ids, durations or voice choices, because the pipeline derives them from the series bible and the locked manifest.

#### Scenario: Project instructions fit ChatGPT's limit
- **WHEN** the compact Project instructions are rendered for any series in the repository
- **THEN** they are at most 8,000 characters long

#### Scenario: Committed renderings are current
- **WHEN** a series bible changes and its committed Project instructions or reference are not regenerated
- **THEN** the automated tests fail and name the command that regenerates them

#### Scenario: Example stays valid
- **WHEN** the example manifest from the full reference is validated against its series
- **THEN** validation reports no errors

#### Scenario: Brief reflects the current bible
- **WHEN** a character is added to a series bible and the renderings are regenerated
- **THEN** both list the new character's id, name and description

#### Scenario: Creative mode produces no YAML
- **WHEN** the producer describes an idea and asks for a draft or storyboard without saying "Lock this story"
- **THEN** ChatGPT answers in prose and a plain-text storyboard, with no YAML

#### Scenario: Lock produces only the manifest
- **WHEN** the producer says "Lock this story" and every required decision is resolved
- **THEN** ChatGPT outputs exactly one fenced YAML block containing a complete manifest and nothing else

#### Scenario: Lock with an unresolved blocking decision
- **WHEN** the producer says "Lock this story" while a required story or schema decision is unresolved (for example the story needs a character not in the cast, the storyboard or ending has not been agreed, or `made_for_kids` has not been stated and the series declares no default)
- **THEN** ChatGPT asks only the minimum question needed to resolve it, outputs no YAML, and does not invent the missing information

#### Scenario: Series default for made-for-kids
- **WHEN** the series declares `defaults.made_for_kids` and the producer has not mentioned it
- **THEN** ChatGPT uses the series default at lock without asking, unless the producer explicitly states otherwise

#### Scenario: Revising a locked story
- **WHEN** the producer asks for changes after a story has been locked
- **THEN** ChatGPT returns to creative mode, and a later "Lock this story" produces a complete replacement manifest (never a partial patch) that can be revalidated and used to rebuild downstream assets
