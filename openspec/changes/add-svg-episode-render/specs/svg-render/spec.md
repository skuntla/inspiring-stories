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

### Requirement: Missing-component check
Before rendering, `story render` SHALL verify that every character, location and prop the episode uses has a component. It SHALL also verify that every stance and mood used is supported by that character's rig. When anything is missing, it SHALL render nothing, list each missing item with the file path where it belongs, and exit with code 1.

#### Scenario: New prop without a component
- **WHEN** the episode uses prop `amber-lantern` and no component exists for it
- **THEN** the report names `amber-lantern` and `render/src/episodes/<episode-id>/props/amber-lantern.tsx` (or the series props folder), and nothing is rendered

#### Scenario: Unsupported stance
- **WHEN** a shot gives `wren` the stance `kneel` and Wren's rig does not support it
- **THEN** the report names the shot, `wren` and `kneel`, and nothing is rendered

### Requirement: Consistent look
Every component SHALL use the shared ink outline and palette helpers. Skies SHALL follow the shot's time of day. Atmosphere values SHALL be drawn as animated overlays. Captions SHALL highlight the word being spoken.

#### Scenario: Night shot
- **WHEN** a shot's time of day is `night`
- **THEN** its sky uses the night palette

### Requirement: Preview and final outputs
`story render <episode> --preview` SHALL write `build/preview.mp4` at 960×540. `story render <episode>` SHALL write `build/final.mp4` at 1920×1080, 30 fps, H.264 video with AAC audio from `build/narration.wav`. After rendering, the command SHALL verify that the file's duration matches the timeline within one frame.

#### Scenario: Duration check
- **WHEN** a render finishes
- **THEN** the MP4 duration equals the timeline duration within one frame, or the command reports an error
