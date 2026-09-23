# Spec Delta

## MODIFIED Requirements

### Requirement: Cast, locations and props
The manifest SHALL list the cast it uses by series character id; every listed id MUST exist in the series bible. Characters not in the bible SHALL NOT be defined inline. A shot's location SHALL be either a recurring location declared in the series bible or a location declared in the episode. Episode locations and props SHALL each be declared once with a unique kebab-case id and a visual description, and shots SHALL reference them by id. An episode SHALL NOT declare a location whose id is already a series location. The episode's `locations` list MAY be empty when every shot uses series locations.

#### Scenario: Character missing from bible
- **WHEN** the cast lists `owl` and the series bible has no `owl`
- **THEN** validation reports an error instructing that `owl` be added to the series bible first

#### Scenario: Undeclared location
- **WHEN** a shot references location `river-bank` that is declared neither in the episode nor in the series
- **THEN** validation reports an unknown-location error at that shot's path

#### Scenario: Declared but unused location
- **WHEN** a location is declared in the episode but no shot references it
- **THEN** validation reports a warning

#### Scenario: Series location used directly
- **WHEN** the series declares location `ben-burrow-exterior` and a shot uses it without the episode declaring it
- **THEN** validation reports no location error

#### Scenario: Episode redeclares a series location
- **WHEN** the series declares `ben-burrow-exterior` and the episode also declares a location with that id
- **THEN** validation reports an error telling the producer to remove the episode declaration and use the series location

### Requirement: Publishing copy
The manifest SHALL declare a YouTube title of at most 100 characters, a description of at most 5000 characters, tags whose combined length is at most 500 characters, an explicit `made_for_kids` boolean, and a thumbnail with a hook of at most 40 characters, a visual concept, and `characters`: the list of cast ids visible in the thumbnail. The list MAY be empty. Each id MUST be in the episode cast, MUST NOT be the narrator, and MUST appear at most once.

#### Scenario: Title too long
- **WHEN** the publishing title has 120 characters
- **THEN** validation reports an error stating the 100-character limit

#### Scenario: Missing audience declaration
- **WHEN** `made_for_kids` is absent
- **THEN** validation reports an error

#### Scenario: Differs from the series default
- **WHEN** the series declares `defaults.made_for_kids: false` and an episode declares `made_for_kids: true`
- **THEN** validation succeeds with a warning asking the producer to confirm the deviation

#### Scenario: Thumbnail characters missing
- **WHEN** `publishing.thumbnail` has no `characters` field
- **THEN** validation reports a missing-field error

#### Scenario: Thumbnail character not in cast
- **WHEN** `publishing.thumbnail.characters` contains `owl` and `owl` is not in the episode cast
- **THEN** validation reports an error at `publishing.thumbnail.characters[0]`

#### Scenario: Narrator in thumbnail
- **WHEN** `publishing.thumbnail.characters` contains the narrator
- **THEN** validation reports an error that the narrator is never drawn

#### Scenario: Scenery-only thumbnail
- **WHEN** `publishing.thumbnail.characters` is `[]`
- **THEN** validation reports no thumbnail error

## ADDED Requirements

### Requirement: Series locations in the ChatGPT documents
Both ChatGPT renderings SHALL list the series' recurring locations (id and description) and instruct ChatGPT to use a recurring location's id, without redeclaring it, whenever a shot takes place there. The compact Project instructions SHALL still not exceed 8,000 characters.

#### Scenario: Recurring location listed
- **WHEN** the series declares location `ben-burrow-exterior` and the Project instructions are regenerated
- **THEN** they list `ben-burrow-exterior` with its description and the rule to use it without redeclaring it

#### Scenario: Series without recurring locations
- **WHEN** the series declares no locations
- **THEN** the renderings omit the recurring-locations section

### Requirement: Thumbnail characters in the ChatGPT documents
Both ChatGPT renderings SHALL include `publishing.thumbnail.characters` in the manifest structure and instruct ChatGPT to list the cast ids visible in the thumbnail (excluding the narrator), or `[]` when none are.

#### Scenario: Field in the Project instructions
- **WHEN** the compact Project instructions are regenerated
- **THEN** the manifest structure shows `characters` under `thumbnail`, with the rule for filling it
