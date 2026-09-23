# Directing guide

How a locked story becomes a video that feels directed rather than illustrated. `STYLE.md` covers how
components are drawn; this covers how shots are chosen, staged, timed and checked. Both apply to every
series. When a lesson is learned on an episode, it goes here, not only into that episode.

## Workflow

1. **Story** — the producer locks a manifest with ChatGPT (`series/<series>/chatgpt-project-instructions.md`).
2. **Direct** — `story validate episodes/<id>`, then improve the manifest for the screen: shot sizes,
   inserts, acting, pacing (below). Keep the story and its words; change how it is shown.
3. **Components** — `story render episodes/<id> --check` names every missing rig, location and prop with
   the path to write. Reuse before drawing (see *Where components live*).
4. **Voice and timeline** — `story voice`, then `story timeline` (prints the length; it also mixes music).
5. **Look before rendering** — render, then pull a contact sheet (one still per shot) and read it:
   ```sh
   # one still at 60% through each shot, tiled 4×4
   for kv in $(python -c "import json;t=json.load(open('episodes/<id>/build/timeline.json'));print(' '.join(f\"{s['id']}:{(s['from']+s['frames']*0.6)/30:.2f}\" for s in t['shots']))"); do
     ffmpeg -v error -y -ss ${kv#*:} -i episodes/<id>/build/preview.mp4 -frames:v 1 stills/${kv%%:*}.png; done
   ffmpeg -v error -y -pattern_type glob -i 'stills/s*.png' -vf tile=4x4:padding=6 stills/contact.png
   ```
6. **Preview** — `story render --preview`; the producer watches on a phone (a re-encoded copy at CRF 26
   is about 4–5 MB). VS Code's video preview has no AAC: use QuickTime.
7. **Approve and final** — `story approve episodes/<id> preview`, then `story render --final`.

## Pacing

- Aim for **70–90 s** for a short motivational story; every shot must earn its time.
- A shot lasts its lines plus pauses, never less than 2.5 s. Long narration makes long static shots:
  split a paragraph across shots or cut words rather than holding one picture.
- `pause_after` is the breath after a line: 0.3–0.6 s normally, about 1 s after a turning point
  (a whisper, a realization), up to 1.2 s at the very end.
- The opening line should land in the first 2 s; don't open on scenery alone.

## Shot grammar

- **Wide** (default) establishes a place, shows walking, or shows someone small and alone.
- **Medium** (`camera.framing: medium`, `subject: <id>`) for a character in a situation: at a desk, at work.
- **Close** for emotion and key lines: a whisper, a realization, the line the story turns on.
  Cut to the speaker's close-up for the line that matters; cut back wider for the reply.
- **Inserts** (ready-made close-ups with no characters) carry off-screen dialogue and let an image say
  the lesson: water on dry soil under a question, a seedling on "the next seed", a compass on "north".
  The speaker's line is `on_screen: false`.
- **Text shots** (`notebook-page`, `closing-card`) show words on screen; their locations set
  `showsText: true`, so captions are hidden there and the words are never shown twice.
- Mirror the opening at the end when the story is about change: same place, same action, a different
  mood (a brisk happy walk at the start, a slower calm walk at the end).
- One idea per shot. If a shot's action needs "and then", it is two shots.

## Acting

What the renderer draws comes from `stance` and `mood`; `pose` and `expression` are notes for the
component author and are **not** drawn by themselves. Choose moods that move:

| Mood | Human rig (`kit/human.tsx`) |
|---|---|
| worried | hand to the temple, shoulders forward |
| thoughtful | hand at the chin, elbow forward |
| sad, tired | slump, head down, slow breathing; sad adds a tear |
| surprised | lean back, eyes wide |
| happy, proud | chest up, open face |
| calm | settled, slow visible breathing, soft eyes |

- Change the mood across shots to show the arc (worried → sad → calm → happy).
- Hands never cover the face or mouth; check any new gesture on the acting sheet (`src/dev/ActingSheet.tsx`).
- Arms: elbows bend backward (forward only for a hand raised in front of the body); knees bend forward.

## Walking

- `stance: walk` with `facing: left|right` travels across the scene; feet are planted (no sliding).
- Speed follows mood: happy/scared are brisk, calm/thoughtful/tired/sad are slow (`WALK_ENERGY` in
  `pipeline/story/timeline.py`). Use this to contrast the same walk at two points of the story.
- Walkers facing the camera or away don't travel.

## Timing visuals to the voice

Never hard-code seconds in a component. Every component receives `words` (each word with its start and
end in seconds from the shot's start, and its speaker) and `kit/spoken.ts` turns them into what you need:
`sentences(words)` for text that writes itself as it is read, `lastWordAt(words)` for a payoff on the
last word (the compass settles on "north"), `wrap(text, n)` for SVG text. Then a re-voiced or re-paced
episode still lines up.

## Keep the frame alive

Blinks, breathing and mouths are automatic. Locations should add one or two slow motions driven by `t`:
a ticking clock, lamp flicker, steam, papers stirring, light spreading at morning, notification
bubbles popping when a scene is about overload. Randomness only through `rand(i, salt)`.

## Captions and music

- Captions: two short lines (≤ 42 characters per page), no speaker names; narration italic, dialogue upright.
- Music: `music: hopeful` in the manifest adds the composed bed (`pipeline/story/music.py`). It thins out
  in low-mood shots, fills out in happy ones, resolves home in the final shot and ducks under speech.
  Level: `LEVEL_DB` (bed vs voice between lines) and `DUCK_DB` (extra dip while speaking).

## Where components live

| Tier | Path | Use for |
|---|---|---|
| Episode | `src/episodes/<episode>/{locations,props}/` | things only this story has |
| Series | `src/series/<series>/{characters,locations,props}/` | the cast, recurring places, recurring props |
| Shared | `src/common/{locations,props}/` | generic close-ups, inserts and cards any story can use |

The most specific wins. **Promote to shared** anything with no story names in it: time it from `words`,
import only from `kit/`, and add a one-line `export const about = "...";`. The ChatGPT briefs list every
shared location under *Ready-made shots*: regenerate them after adding one
(`story brief <series> --out series/<series>/chatgpt-project-instructions.md`, and `--full` to
`chatgpt-reference.md`) and keep the compact file under 8,000 characters.

## Review checklist

- Is every face visible when it matters (not cropped by a close-up, not hidden by a hand)?
- Do feet stay planted while walking, and do arms and knees bend the right way?
- Does each close-up frame the right character, with room in front of the face?
- Do text shots show no captions, and does the text finish before the voice does?
- Is there motion in every shot, and does the final shot hold long enough to breathe?
- Is the episode inside 70–90 s?
