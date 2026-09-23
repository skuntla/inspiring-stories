# Spec Delta

## ADDED Requirements

### Requirement: Production commands
The `story` command SHALL provide `voice`, `timeline`, `render`, `produce` and `approve` for an episode folder, following the same report format and exit codes as `validate`. Each production command SHALL validate the episode and its series first and stop with the validation report, producing nothing, when there are errors.

#### Scenario: Invalid episode
- **WHEN** `story voice <episode>` is run on an episode with a validation error
- **THEN** no audio is generated, the validation errors are reported, and the exit code is 1

#### Scenario: One trigger
- **WHEN** `story produce <episode>` is run on a valid episode whose components all exist
- **THEN** it runs voice, timeline and a preview render in order, stops at the first failing step, and on success prints the preview path and the approval command

## MODIFIED Requirements

### Requirement: Generate the ChatGPT documents
`story brief <series-id> --story` SHALL write the series' story-only ChatGPT prompt, which asks for plain prose and never YAML (the producer's normal workflow). `story brief <series-id>` SHALL write the compact ChatGPT Project instructions, and `story brief <series-id> --full` the full reference contract, to stdout or to a file given with `--out`. It SHALL refuse to run if the series bible or its example episode has validation errors. For the compact instructions it SHALL refuse to write output longer than 8,000 characters and SHALL warn when the output exceeds 7,500 characters.

#### Scenario: Project instructions for a valid series
- **WHEN** `story brief kind-hearts --out chatgpt-project-instructions.md` is run on a valid bible
- **THEN** the file contains the compact instructions, is at most 8,000 characters, and the exit code is 0

#### Scenario: Full reference
- **WHEN** `story brief kind-hearts --full --out chatgpt-reference.md` is run on a valid bible
- **THEN** the file contains the full instructions, vocabulary, cast and example manifest, and the exit code is 0

#### Scenario: Brief for an invalid series
- **WHEN** the series bible has an error
- **THEN** no document is written, the errors are reported, and the exit code is 1

#### Scenario: Project instructions too long
- **WHEN** the compact rendering would exceed 8,000 characters (for example because character descriptions are very long)
- **THEN** nothing is written, the error states the length and the limit, and the exit code is 1

#### Scenario: Project instructions near the limit
- **WHEN** the compact rendering is between 7,501 and 8,000 characters
- **THEN** the output is written and a warning states the length and the 7,500-character target

#### Scenario: Story-only prompt
- **WHEN** `story brief quiet-lessons --story --out chatgpt-story-prompt.md` is run on a valid bible
- **THEN** the file asks ChatGPT for the story as plain prose with no YAML or shot list, lists the series' reusable characters, contains no example manifest, and the exit code is 0
