# Spec Delta

## Purpose

Turns every spoken line of a locked episode into audio with Kokoro, locally, and measures what the renderer needs from it: per-word timings for captions and a viseme track for lip sync.

## ADDED Requirements

### Requirement: Per-line synthesis
`story voice <episode>` SHALL synthesize each line with the speaker's Kokoro voice and speed from the series bible, writing one WAV per line at `build/audio/<line-id>.wav` (24 kHz mono), where the line id is `<shot id>-l<NN>`. Pronunciation overrides SHALL replace display words in the spoken text only; captions keep display text.

#### Scenario: Voice from the bible
- **WHEN** a line is spoken by `ben`, whose bible voice is `bm_george` at speed 0.9
- **THEN** its audio is generated with `bm_george` at speed 0.9

#### Scenario: Pronunciation override
- **WHEN** the manifest maps `Zephyrine` to `ZEF-ih-reen` and a line says "Zephyrine smiled."
- **THEN** Kokoro receives "ZEF-ih-reen smiled." and the recorded words show "Zephyrine"

### Requirement: Word timings and visemes
For each line, narration SHALL record, relative to the start of the line's audio, every display word with its start and end time, and a viseme track: time-ordered keys whose shape is one of `rest`, `closed`, `fv`, `consonant`, `ee`, `mid`, `open`, `round`. It SHALL derive these by spreading each word's phonemes across the word's duration. Adjacent words SHALL NOT be separated by a `rest` key when the next word starts within 60 ms. Results are written to `build/speech.json`.

#### Scenario: Keys in time order
- **WHEN** `build/speech.json` is written
- **THEN** every line's viseme keys have non-decreasing times and start at or after its first word

#### Scenario: Bilabial closes the mouth
- **WHEN** a word begins with the phoneme `b`, `m` or `p`
- **THEN** its first viseme key is `closed`

### Requirement: Caching
Narration SHALL record, per line, a digest of its inputs (spoken text, voice, speed, and Kokoro version). A line whose digest is unchanged SHALL NOT be regenerated. `--force` SHALL regenerate every line.

#### Scenario: Relock changes one line
- **WHEN** only line `s03-l02` changed since the last run
- **THEN** only `s03-l02` is synthesized again

### Requirement: Local and deterministic
Narration SHALL run without network access once the Kokoro model and voices are cached, and SHALL fail with an actionable message when the optional voice install is missing.

#### Scenario: Voice extra not installed
- **WHEN** `story voice` runs in an environment without Kokoro
- **THEN** it exits with code 1 and prints the install command
