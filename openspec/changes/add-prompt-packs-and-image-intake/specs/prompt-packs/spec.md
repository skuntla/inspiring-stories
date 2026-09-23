# Spec Delta

## Purpose

Generates the Gemini prompts the producer pastes by hand: one-time prompts for a series' reference images, and per-episode prompts for every shot and the thumbnail. Every prompt is derived from the series bible and the locked manifest, so identity and style wording never drift.

## ADDED Requirements

### Requirement: Series reference prompt pack
`story prompts <series-dir>` SHALL write one prompt file per declared reference image (style references, each character's front, three-quarter and side views and expression sheet, and each location reference) plus an index listing them in generation order. Style references come first. Character views and location references attach the first style reference. A character's three-quarter view, side view and expression sheet also attach that character's front view. Each prompt SHALL name the exact path to save the image as, which is the path declared in the bible.

#### Scenario: Reference pack for a series
- **WHEN** `story prompts series/willow-meadow` is run on a valid bible
- **THEN** `series/willow-meadow/build/prompts/` contains an index and one prompt per declared reference image, each naming its save-as path

#### Scenario: Chained identity
- **WHEN** the prompt for `pip`'s three-quarter view is generated
- **THEN** its attachments are the first style reference followed by `pip`'s front view

### Requirement: Episode shot prompt pack
`story prompts <episode-dir>` SHALL write one prompt file per episode location anchor (`build/prompts/location-<id>.md`), one per shot (`build/prompts/sNN.md`), a thumbnail prompt, and an index listing every image to generate, in that order, with its save-as path (`images/locations/<id>.png`, `images/sNN.png`, `images/thumbnail.png`). It SHALL refuse, and write nothing, if the episode or its series has validation errors.

#### Scenario: Pack for a valid episode
- **WHEN** `story prompts episodes/2026-09-22-pip-and-the-foggy-path` is run
- **THEN** the pack contains `location-foggy-meadow.md`, `location-old-fence-crossing.md`, `s01.md` through `s16.md`, `thumbnail.md` and an index that lists the anchors first, and the exit code is 0

#### Scenario: Invalid episode
- **WHEN** the episode has a validation error
- **THEN** no prompt files are written, the errors are reported, and the exit code is 1

### Requirement: Episode location anchors
Every location declared in the episode (not in the series) that is used by two or more shots SHALL get an anchor image: a 16:9 establishing view of the location as described, with no characters. Its prompt attaches the first style reference and names the save-as path `images/locations/<id>.png`. A location used by only one shot SHALL NOT get an anchor. The manifest carries no field for anchors; they are derived from location usage.

#### Scenario: Location used by several shots
- **WHEN** episode location `foggy-meadow` is used by seven shots
- **THEN** the pack contains an anchor prompt for `foggy-meadow` with save-as path `images/locations/foggy-meadow.png`

#### Scenario: Single-use location
- **WHEN** episode location `willow-stream` is used by one shot
- **THEN** the pack contains no anchor prompt for `willow-stream`

#### Scenario: Series location
- **WHEN** a shot uses series location `ben-burrow-exterior`
- **THEN** no episode anchor is generated for it, because the series reference images serve that role

### Requirement: Reference attachments per shot
Each shot prompt SHALL list the reference images to attach, in this order: the first style reference; the shot's location references (the series location's reference images, or the episode anchor when the location has one); for each visible character, the view that matches their facing (`camera` → front, `left` or `right` → three-quarter, `away` → side); then the expression sheet of each character who speaks on screen in the shot. At most six attachments SHALL be listed; when there are more, expression sheets and then location references beyond the first are dropped, and the prompt notes what was dropped. An attachment whose file does not exist yet SHALL be marked as missing, and the command SHALL warn.

#### Scenario: Speaking character facing the camera
- **WHEN** a shot shows `pip` facing `camera` and `pip` has an on-screen line in that shot
- **THEN** the attachments include `pip`'s front view followed by `pip`'s expression sheet, if declared

#### Scenario: Shot at an anchored episode location
- **WHEN** a shot uses episode location `foggy-meadow`, which has an anchor
- **THEN** the attachments list `images/locations/foggy-meadow.png` directly after the style reference

#### Scenario: Missing reference image
- **WHEN** a listed attachment file has not been generated yet
- **THEN** the prompt marks it as missing and the command warns that the series references and location anchors should be generated first

### Requirement: Prompt content
Each shot prompt SHALL include: the series style description verbatim; for every visible character, their name, description, outfit and distinguishing features verbatim, with an instruction to keep them identical to the attached references; the location's description and the shot's time of day; visible props with their descriptions; position, pose, expression and facing for each visible character; the action, emotion and composition notes; a 16:9 frame with extra scenery around the edges to leave room for the camera move; and animation-preparation constraints (eyes visible for characters not facing away, faces and mouths of on-screen speakers unobstructed, characters not overlapping each other's faces). Atmosphere effects that are animated later (rain, snow, dust motes, fireflies, embers, falling leaves, sparkles) SHALL be excluded from the drawing; the others (fog, mist, sun rays, firelight, wind) SHALL be described as part of the scene. Prompts SHALL list the series' avoid list plus fixed exclusions (no text, captions, borders, signatures, watermarks or extra characters), and SHALL NOT contain spoken line text.

#### Scenario: Identity carried verbatim
- **WHEN** a shot shows `ben`
- **THEN** the prompt contains `ben`'s description, outfit and each distinguishing feature exactly as written in the bible

#### Scenario: Animated atmosphere left out
- **WHEN** a shot's atmosphere is `["fog", "fireflies"]`
- **THEN** the prompt describes fog in the scene and tells the illustrator not to draw fireflies

#### Scenario: No dialogue in prompts
- **WHEN** a shot contains the line "Pip!"
- **THEN** no prompt file contains that line's text

### Requirement: Thumbnail prompt
The thumbnail prompt SHALL be built from the publishing thumbnail concept, the series style, and the characters listed in `publishing.thumbnail.characters`. It SHALL NOT infer characters from the concept text. For each listed character it SHALL include the verbatim identity block and attach that character's front view, after the first style reference, within the six-attachment cap. It SHALL instruct the illustrator not to draw any text; the hook text is added later by the pipeline.

#### Scenario: Thumbnail without text
- **WHEN** the thumbnail hook is "ONE SMALL STEP"
- **THEN** the thumbnail prompt forbids text and does not contain "ONE SMALL STEP"

#### Scenario: Characters come from the structured list
- **WHEN** `publishing.thumbnail.characters` is `["pip"]` and the concept text also mentions "Old Ben's lantern"
- **THEN** the thumbnail prompt contains `pip`'s identity block and front-view attachment, and nothing for `ben`

#### Scenario: Scenery-only thumbnail
- **WHEN** `publishing.thumbnail.characters` is `[]`
- **THEN** the thumbnail prompt attaches only the style reference and tells the illustrator to draw no characters

### Requirement: Deterministic packs
Given identical inputs, a prompt pack SHALL be byte-identical. Each prompt file SHALL record the SHA-256 digests of the manifest and series bible it was built from. Regenerating after a relock SHALL replace the pack, and files for shots that no longer exist SHALL be removed.

#### Scenario: Regenerate unchanged
- **WHEN** `story prompts` is run twice on unchanged inputs
- **THEN** every file in the pack is byte-identical between runs

#### Scenario: Shot removed by a relock
- **WHEN** a relocked manifest has 15 shots where the previous one had 16
- **THEN** `s16.md` no longer exists in the regenerated pack
