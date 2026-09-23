# Render style guide

The rules every SVG component follows, so that characters, places and props written at different times still look like one world. `story render` enforces the file layout and the rig declarations; the look is enforced at the preview checkpoint.

## Files

| What | Where | Exports |
|---|---|---|
| Character rig (series-wide) | `src/series/<series>/characters/<id>.tsx` | `rig: Rig` |
| Recurring location | `src/series/<series>/locations/<id>.tsx` | `location: Location` |
| Shared prop | `src/series/<series>/props/<id>.tsx` | `prop: Prop` |
| Episode-only location / prop | `src/episodes/<episode-id>/{locations,props}/<id>.tsx` | same as above |

The file name is the id from the manifest. An episode component wins over a series one with the same id. Interfaces live in `src/kit/types.ts`.

## Rigs

- Drawn **facing right**, origin at the **feet on the ground line**, standing height roughly: Pip 260 px, Ben 380 px, Wren 150 px. The renderer mirrors for `facing: left` and scales background characters to 0.6.
- Declare support as **one-line literal arrays**, which `story render` reads:
  ```ts
  stances: ['stand', 'walk', 'sit'],
  moods: ['neutral', 'happy', 'sad'],
  ```
- `anchors.hand` is where a held prop is drawn (the `hold` stance); `anchors.head` is the top of the head.
- Mouths: use `kit/face.tsx` (`Mouth`, `moodFace`) so the eight visemes and the ten moods read the same on every character. Eyes blink through the `eye` prop (1 open → 0 closed).
- Keep idle life subtle: breathing about 1%, a small head tilt, a little extra movement while `speaking`.

## Locations

- Draw in the 1920×1080 scene space, **with margin beyond the frame** (about 200 px each side): the camera pans and zooms.
- `groundY` is where foreground characters stand (keep it about 850–880 so captions never cover feet); `backgroundGroundY` is for background characters.
- `propSlots` lists where free props stand, in the order props are assigned.
- Descriptions carry no time of day or weather: the renderer adds the sky, the light tint and the atmosphere. Interiors set `interior: true` and draw their own walls; windows may use `palette.skyMid` so they follow the time of day.
- Put slow SVG filters (`watercolor`) only on static background groups, never on characters or animated parts.

## Look

- **One ink outline**: `ink(width)` from `kit/style.tsx` (`#3b2a20`, round joins), about 3–3.5 px on characters, 2.5–3 on props and near scenery, lighter opacity on far scenery.
- **Palette**: muted greens and golden ochres, warm browns, soft creams; saturated colors only for small accents (Pip's scarf, Wren's berry, the lantern glow).
- **Depth**: far layers lighter, bluer and softly blurred (`farBlur`); near layers darker and crisper.
- Randomness only through `rand(i, salt)`: every frame must render identically on every run.
