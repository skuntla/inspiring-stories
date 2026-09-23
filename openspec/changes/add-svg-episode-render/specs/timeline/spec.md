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
The timeline SHALL write `build/narration.wav`, the lines placed at their frames with the episode's background music (if any) beneath them, normalized to −14 LUFS integrated (±1 LU) with true peak at or below −1 dBTP.

#### Scenario: Loudness
- **WHEN** `build/narration.wav` is measured
- **THEN** its integrated loudness is between −15 and −13 LUFS

### Requirement: Background music
An episode MAY declare `music` (`none` or `hopeful`; default `none`). For `hopeful`, the timeline SHALL compose a light music bed in code, deterministically for the episode: sparser and quieter in shots whose characters are low (sad, tired, worried, scared, angry), fuller in happy or proud shots, with inserts keeping the previous shot's energy, and resolving on the home chord in the final shot. The bed SHALL sit well under the voices and dip further while anyone speaks.

#### Scenario: No music by default
- **WHEN** an episode declares no `music`
- **THEN** the soundtrack contains only the voices

#### Scenario: Ducking under speech
- **WHEN** a line is spoken over the `hopeful` bed
- **THEN** the music is quieter during the line than between lines

#### Scenario: Same episode, same music
- **WHEN** the timeline is built twice for the same episode
- **THEN** the music is sample-identical

### Requirement: Resolved staging and camera
For every shot, the timeline SHALL record the location id, time of day, atmosphere, props, and each visible character's x position (from `position`), facing, stance and mood. A character walking left or right SHALL also get a travel range and a walking speed of at most 110 px/s, limited so the travel stays within 900 px and inside the scene. It SHALL also record a camera path: start and end center and zoom, eased, derived from `camera.move` and `camera.intensity` and clamped so the frame never leaves the scene.

#### Scenario: Walking character travels
- **WHEN** a visible character has stance `walk` and faces `left` or `right`
- **THEN** the timeline gives it a start and end x in its facing direction, centered on its position, kept inside the scene, and a walking speed, so it crosses the frame at that constant speed during the shot

#### Scenario: Walking toward or away from the camera
- **WHEN** a walking character faces `camera` or `away`
- **THEN** it stays at its position and does not travel

#### Scenario: Walk energy follows mood
- **WHEN** one walking character is `happy` and another is `calm`
- **THEN** the happy walker's speed is higher than the calm walker's

#### Scenario: Close-up framing
- **WHEN** a shot has `framing: close` with subject `arjun`
- **THEN** the timeline records the framing and the subject's position and depth, and the camera move is expressed relative to that framed view

#### Scenario: Push-in
- **WHEN** a shot has `camera: {move: push_in, intensity: medium}`
- **THEN** its camera zoom increases over the shot and the view stays inside the 1920×1080 scene

### Requirement: Mouths, blinks and captions
The timeline SHALL give each on-screen speaker a mouth track in frames from their line's visemes; every other character rests. Blinks SHALL follow a schedule seeded by character and shot. Captions SHALL list each line's words in frames, grouped into pages of at most 42 characters so a page fits in two short lines on a phone, and SHALL record the speaker (the character id for dialogue, none for narration) for styling; the renderer does not print speaker names.

#### Scenario: Off-screen voice
- **WHEN** a character speaks with `on_screen: false`
- **THEN** no mouth track is produced for that line, and its caption pages record that character as the speaker

#### Scenario: Same input, same timeline
- **WHEN** `story timeline` runs twice on unchanged inputs
- **THEN** `build/timeline.json` is byte-identical
