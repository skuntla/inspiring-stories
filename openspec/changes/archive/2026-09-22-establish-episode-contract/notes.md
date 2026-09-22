# Notes: establish-episode-contract

## Task 7.1: end-to-end ChatGPT round trip (2026-09-22): PASSED

Setup: `series/willow-meadow/chatgpt-project-instructions.md` (4,898 characters) installed as
the instructions of the ChatGPT Project "InspiringStories" for series `willow-meadow`.

| Step | Check | Result |
|---|---|---|
| (a) | Creative mode stays free of YAML | **Passed.** Brainstorming, prose drafting and a 15-shot storyboard stayed in creative mode with no YAML. |
| (b) | Lock with an unresolved blocking decision asks only the minimum question | **Passed.** In a fresh Project chat, an approved three-shot story needing Hazel the owl was locked. ChatGPT replied only: "Hazel is not in the approved Cast. Should Hazel be added as a visible, speaking owl character, or should Old Ben take her role?" No YAML was produced, and it did not ask about `made_for_kids` (the series default applied). |
| (c) | Lock produces exactly one complete, valid manifest | **Passed.** "Pip and the Foggy Path" came back as one YAML block; the 15-shot manifest validated with 0 errors and used `made_for_kids: false` from the series default. |
| (d) | Revision after lock returns to creative mode; relock is a complete replacement | **Passed.** The long final shot was split into shots 15 and 16; the next lock produced a complete replacement manifest that validated with 0 errors and 10 expected missing-reference-image warnings. |

Final episode: `episodes/2026-09-22-pip-and-the-foggy-path/episode.yaml`, committed as
`fee25dd`. It has 16 shots, an estimated 204.7 s of speech, 0 errors, and 10 warnings (all
series reference images not yet generated). Re-validated locally when this change was archived.

## Issues found and resolved during the change

- ChatGPT's Project-instructions field is limited to 8,000 characters; the original ~16,000-character
  brief could not be installed. Resolved by task 5.7: a compact Project-instructions rendering
  (default `story brief`, enforced at most 8,000 characters) plus the full reference (`story brief --full`).
- Setting `made_for_kids` for every episode would have been a lock-time question each time. Resolved by
  task 5.6: series `defaults.made_for_kids`, which the instructions use without asking.

## Observations for later changes

- The first real episode has 7 locations and 4 props; `foggy-meadow` (5 shots) and
  `ben-burrow-exterior` (3 shots) should become recurring location references in
  `add-prompt-packs-and-image-intake`.
- It has 18+ on-screen character lines; lip sync (deferred) will matter most for dialogue-heavy
  shots such as s07–s09 and s14.
