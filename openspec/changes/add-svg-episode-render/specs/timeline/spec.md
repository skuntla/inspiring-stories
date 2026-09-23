# Spec Delta

## Purpose

Resolves a locked episode plus its measured speech into one frame-exact description of the video, so the renderer only draws and never decides timing, staging or camera.

## ADDED Requirements

### Requirement: Audio-driven shot durations
`story timeline <episode>` SHALL compute each shot's duration from its lines' measured audio: a 0.5 s lead-in, each line followed by its `pause_after` (default 0.35 s), and a 1.0 s tail. A shot SHALL last at least 2.5 s. Durations SHALL be rounded up to whole frames at 30 fps once, and each line's audio SHALL start on a frame boundary. The same frames SHALL place the audio in `build/narration.wav`, so picture and sound share one clock.

#### Scenario: Frame-aligned lines
- **WHEN** the timeline is built
- **THEN** every line's start is an integer frame, and its audio begins at exactly that sample offset in `build/narration.wav`

#### Scenario: Short shot
- **WHEN** a shot's lines total 1.2 s of speech
- **THEN** the shot lasts 2.5 s

### Requirement: Mixed narration
The timeline SHALL write `build/narration.wav`, the lines placed at their frames, normalized to −14 LUFS integrated (±1 LU) with true peak at or below −1 dBTP.

#### Scenario: Loudness
- **WHEN** `build/narration.wav` is measured
- **THEN** its integrated loudness is between −15 and −13 LUFS

### Requirement: Resolved staging and camera
For every shot, the timeline SHALL record the location id, time of day, atmosphere, props, and each visible character's x position (from `position`), facing, stance and mood. It SHALL also record a camera path: start and end center and zoom, eased, derived from `camera.move` and `camera.intensity` and clamped so the frame never leaves the scene.

#### Scenario: Push-in
- **WHEN** a shot has `camera: {move: push_in, intensity: medium}`
- **THEN** its camera zoom increases over the shot and the view stays inside the 1920×1080 scene

### Requirement: Mouths, blinks and captions
The timeline SHALL give each on-screen speaker a mouth track in frames from their line's visemes; every other character rests. Blinks SHALL follow a schedule seeded by character and shot. Captions SHALL list each line's words in frames, grouped into pages of at most seven words, with a speaker label for dialogue and none for narration.

#### Scenario: Off-screen voice
- **WHEN** a character speaks with `on_screen: false`
- **THEN** no mouth track is produced for that line, and the caption still shows the speaker label

#### Scenario: Same input, same timeline
- **WHEN** `story timeline` runs twice on unchanged inputs
- **THEN** `build/timeline.json` is byte-identical
