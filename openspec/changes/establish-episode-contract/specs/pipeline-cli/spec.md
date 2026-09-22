# Spec Delta

## Purpose

Provides the local `story` command that humans and Claude skills use to create and check episodes; this change introduces its scaffolding and validation commands and the report and exit-code conventions all later commands follow.

## ADDED Requirements

### Requirement: Local, offline, repeatable execution
The `story` command SHALL run entirely locally without network access. Given identical input files, a command SHALL produce identical output.

#### Scenario: Repeat validation
- **WHEN** `story validate` is run twice on unchanged files
- **THEN** both runs produce byte-identical reports and the same exit code

### Requirement: Scaffold a new episode
`story new <series-id> "<title>"` SHALL create `episodes/<YYYY-MM-DD>-<slug>/episode.yaml` containing a stub manifest with the series, id and title filled in. The date SHALL default to today and MAY be overridden with `--date YYYY-MM-DD`. The slug SHALL be derived from the title in lowercase kebab-case ASCII.

#### Scenario: Create episode
- **WHEN** `story new kind-hearts "The Brave Little Seed" --date 2026-10-01` is run
- **THEN** `episodes/2026-10-01-the-brave-little-seed/episode.yaml` exists with `series: kind-hearts` and `id: 2026-10-01-the-brave-little-seed`

#### Scenario: Refuse to overwrite
- **WHEN** the target episode folder already contains `episode.yaml`
- **THEN** the command exits with an error and leaves the existing file unchanged

#### Scenario: Unknown series
- **WHEN** the named series bible does not exist
- **THEN** the command exits with an error and creates nothing

### Requirement: Validate episodes and series
`story validate <path>` SHALL accept an episode folder or a series folder. For an episode it SHALL validate the episode's series bible first and then the episode. For a series it SHALL validate the bible only.

#### Scenario: Validate an episode with a broken bible
- **WHEN** an episode is validated and its series bible has an error
- **THEN** the report includes the bible error and the command exits with the error code

### Requirement: Actionable report
The validation report SHALL list every error and warning found (not only the first), each with its severity, the file, a path to the offending field (for example `shots[2].lines[0].speaker`), and a message stating what is wrong and what is allowed. It SHALL end with counts of errors and warnings. `--json` SHALL produce the same findings as machine-readable JSON.

#### Scenario: Multiple problems
- **WHEN** an episode has an unknown camera move in `s02` and a missing title
- **THEN** both findings appear in one report with their field paths

#### Scenario: Machine-readable output
- **WHEN** `story validate <dir> --json` is run
- **THEN** stdout is a single JSON document listing findings with severity, file, path and message

### Requirement: Generate the ChatGPT brief
`story brief <series-id>` SHALL write the series' ChatGPT instruction document to stdout, or to a file given with `--out`. It SHALL refuse to run if the series bible has validation errors.

#### Scenario: Brief for a valid series
- **WHEN** `story brief kind-hearts --out brief.md` is run on a valid bible
- **THEN** `brief.md` contains the instructions, vocabulary, cast and example manifest, and the exit code is 0

#### Scenario: Brief for an invalid series
- **WHEN** the series bible has an error
- **THEN** no document is written, the errors are reported, and the exit code is 1

### Requirement: Exit codes
Commands SHALL exit with 0 on success (warnings allowed), 1 when validation errors are found, and 2 on usage errors such as a missing path or unknown command.

#### Scenario: Warnings only
- **WHEN** validation finds warnings but no errors
- **THEN** the exit code is 0

#### Scenario: Bad path
- **WHEN** `story validate does/not/exist` is run
- **THEN** the exit code is 2
