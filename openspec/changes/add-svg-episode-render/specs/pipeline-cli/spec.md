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
