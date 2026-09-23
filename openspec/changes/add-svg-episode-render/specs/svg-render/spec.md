# Spec Delta

## Purpose

Draws an episode's timeline as SVG in Remotion: character rigs, set pieces, props and atmosphere from a component library. It produces the preview and final MP4.

## ADDED Requirements

### Requirement: Component library
Visual components SHALL live in `render/src/`, one file per component:
- Series components go in `series/<series-id>/`: `characters/<id>.tsx`, `locations/<id>.tsx` and `props/<id>.tsx`.
- Episode components go in `episodes/<episode-id>/`: `locations/<id>.tsx` and `props/<id>.tsx`.
- Atmosphere overlays are shared, one per atmosphere value.

A character rig SHALL declare the stances and moods it supports and render any supported combination with a given mouth shape and eye openness.

#### Scenario: Episode-only location
- **WHEN** the episode uses location `foggy-meadow`, declared only in the episode
- **THEN** the renderer draws it from `render/src/episodes/<episode-id>/locations/foggy-meadow.tsx`

### Requirement: Shared component library
Generic locations and props (close-ups, inserts, text cards) SHALL live in `render/src/common/{locations,props}/`, usable by every series and episode. Lookup SHALL prefer the episode's component, then the series', then the shared one. Each shared component SHALL declare a one-line `about` description, and the ChatGPT renderings SHALL list the shared locations as ready-made shots. Components SHALL receive the words spoken in the shot with their times, so text and payoffs follow the voice instead of fixed seconds.

#### Scenario: Reusing a shared close-up
- **WHEN** an episode declares and uses `compass-closeup` and neither the episode nor its series has that component
- **THEN** the render uses `render/src/common/locations/compass-closeup.tsx`

#### Scenario: A more specific component wins
- **WHEN** the series also has `locations/compass-closeup.tsx`
- **THEN** the render uses the series component

#### Scenario: Briefs list ready-made shots
- **WHEN** `story brief` renders either series
- **THEN** the output lists every shared location id with its description

### Requirement: Thumbnails
An episode MAY describe its YouTube thumbnail in `render/src/episodes/<episode>/thumbnail.tsx` using the series' own components, with one or more headline variants. `story thumbnail <episode>` SHALL render one 1280×720 JPEG per variant to `build/thumbnail-<n>.jpg` and report each file's size against YouTube's 2 MB limit. The thumbnail SHALL NOT be an approval input.

#### Scenario: Thumbnail variants
- **WHEN** an episode's thumbnail spec declares three headlines and `story thumbnail` is run
- **THEN** `build/thumbnail-1.jpg`, `-2.jpg` and `-3.jpg` are written at 1280×720

#### Scenario: No thumbnail spec
- **WHEN** the episode has no `thumbnail.tsx`
- **THEN** nothing is rendered, the error names the file to write, and the exit code is 1

### Requirement: Missing-component check
Before rendering, `story render` SHALL verify that every character, location and prop the episode uses has a component. It SHALL also verify that every stance and mood used is supported by that character's rig. When anything is missing, it SHALL render nothing, list each missing item with the file path where it belongs, and exit with code 1.

#### Scenario: New prop without a component
- **WHEN** the episode uses prop `amber-lantern` and no component exists for it
- **THEN** the report names `amber-lantern` and `render/src/episodes/<episode-id>/props/amber-lantern.tsx` (or the series props folder), and nothing is rendered

#### Scenario: Unsupported stance
- **WHEN** a shot gives `wren` the stance `kneel` and Wren's rig does not support it
- **THEN** the report names the shot, `wren` and `kneel`, and nothing is rendered

### Requirement: Consistent look
Every component SHALL use the shared ink outline and palette helpers. Rigs SHALL animate walking with the shared walk cycle, which plants each foot during its stance phase at the character's walking speed. Skies SHALL follow the shot's time of day. Atmosphere values SHALL be drawn as animated overlays. Captions SHALL highlight the word being spoken, be sized for phones (at most two short lines, about 66 px at 1080p, raised from the bottom edge), style narration and dialogue differently without printing speaker names, and be hidden on shots whose location shows its own text. Human rigs SHALL express mood through posture and gesture, not only the face. A `medium` or `close` shot SHALL be framed on its subject's face using the rig's height and the location's ground line, clamped to the scene.

#### Scenario: Planted feet while walking
- **WHEN** a character walks with a given speed
- **THEN** its rig takes strides matched to that speed, so the foot on the ground does not slide while the body moves across the frame

#### Scenario: Mood drives acting
- **WHEN** a seated human character's mood is `worried`
- **THEN** the rig draws a worried posture (shoulders forward, a hand to the forehead), distinct from its `calm` and `happy` postures

#### Scenario: Captions stay out of text shots
- **WHEN** a shot's location declares that it shows its own text (such as a notebook page or a closing card)
- **THEN** no captions are drawn over that shot

#### Scenario: Night shot
- **WHEN** a shot's time of day is `night`
- **THEN** its sky uses the night palette

### Requirement: Preview and final outputs
`story render <episode> --preview` SHALL write `build/preview.mp4` at 960×540. `story render <episode>` SHALL write `build/final.mp4` at 1920×1080, 30 fps, H.264 video with AAC audio from `build/narration.wav`. After rendering, the command SHALL verify that the file's duration matches the timeline within one frame.

#### Scenario: Duration check
- **WHEN** a render finishes
- **THEN** the MP4 duration equals the timeline duration within one frame, or the command reports an error
